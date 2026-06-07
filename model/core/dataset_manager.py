from pathlib import Path

import numpy as np

from config.settings import (
    SUPPORTED_DATASET_EXTENSIONS,
    SUPPORTED_GRD_EXTENSIONS,
    SUPPORTED_GRIB_EXTENSIONS,
    SUPPORTED_NETCDF_EXTENSIONS,
)
from model.loaders.grd_loader import GRDLoader
from model.loaders.grib_loader import GRIBLoader
from model.loaders.netcdf_loader import NetCDFLoader
from model.processing.validation import DatasetValidator
from model.processing.weather_variables import WeatherVariableNormalizer
from utils.logger import get_logger


class DatasetManager:
    """Owns the currently loaded dataset and hides format-specific loading."""

    def __init__(self):
        self.dataset = None
        self.file_path = None
        self.validation_report = {}
        self.loaders = {
            "netcdf": NetCDFLoader(),
            "grib": GRIBLoader(),
            "grd": GRDLoader(),
        }
        self.validator = DatasetValidator()
        self.normalizer = WeatherVariableNormalizer()
        self.logger = get_logger(__name__)

    def load_dataset(self, file_path):
        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix not in SUPPORTED_DATASET_EXTENSIONS:
            raise ValueError(
                f"Unsupported format '{suffix}'. Supported formats: NetCDF, GRIB, GRD."
            )

        loader = self._loader_for_suffix(suffix)
        dataset = loader.load(path)
        self.validation_report = self.validator.validate(dataset)
        if not self.validation_report["valid"]:
            raise ValueError(
                "Dataset validation failed:\n"
                + "\n".join(self.validation_report["errors"])
            )

        self.dataset = dataset
        self.file_path = path
        self.logger.info("Loaded %s dataset: %s", self.dataset.attrs.get("source_format", suffix), path)
        return self.dataset

    def close_dataset(self):
        """Release the active xarray dataset and reset file state."""
        if self.dataset is not None:
            self.dataset.close()
        self.dataset = None
        self.file_path = None
        self.validation_report = {}

    def get_dataset(self):
        return self.dataset

    def has_dataset(self):
        return self.dataset is not None

    def get_variable_names(self):
        if self.dataset is None:
            return []
        names = list(self.dataset.data_vars)
        wind = self.normalizer.resolve(self.dataset)["wind"]
        if wind.get("vector_available") and not wind.get("scalar") and "wind_speed" not in names:
            names.insert(0, "wind_speed")
        return names

    def has_variable(self, variable_name):
        if self.dataset is None:
            return False
        if variable_name in self.dataset.data_vars:
            return True
        return variable_name == "wind_speed" and self._derived_wind_speed() is not None

    def get_variable(self, variable_name):
        if not self.has_variable(variable_name):
            raise KeyError(f"Variable not found in dataset: {variable_name}")
        if variable_name not in self.dataset.data_vars and variable_name == "wind_speed":
            return self._derived_wind_speed()
        return self.dataset[variable_name]

    def get_dimensions(self):
        if self.dataset is None:
            return {}
        return {name: int(size) for name, size in self.dataset.sizes.items()}

    def get_coordinates(self):
        if self.dataset is None:
            return []
        return list(self.dataset.coords)

    def get_coordinate_ranges(self):
        if self.dataset is None:
            return {}

        ranges = {}
        for name, coord in self.dataset.coords.items():
            values = coord.values
            if values.size == 0:
                ranges[name] = {"min": "", "max": ""}
                continue
            try:
                ranges[name] = {
                    "min": str(values.min()),
                    "max": str(values.max()),
                }
            except TypeError:
                ranges[name] = {
                    "min": str(values[0]),
                    "max": str(values[-1]),
                }
        return ranges

    def get_variable_profile(self, variable_name):
        variable = self.get_variable(variable_name)
        values = self._numeric_values(variable)
        missing = ""
        valid = ""
        if values is not None:
            missing = int(np.count_nonzero(np.isnan(values)))
            valid = int(np.count_nonzero(~np.isnan(values)))
        return {
            "name": variable_name,
            "dims": list(variable.dims),
            "shape": [int(size) for size in variable.shape],
            "dtype": str(variable.dtype),
            "units": variable.attrs.get("units", ""),
            "long_name": variable.attrs.get("long_name", variable_name),
            "ndim": int(variable.ndim),
            "attrs": dict(variable.attrs),
            "valid_count": valid,
            "missing_values": missing,
        }

    def get_dataset_info(self):
        if self.dataset is None:
            return {}

        file_size = self.file_path.stat().st_size if self.file_path and self.file_path.exists() else 0
        variables = {
            name: self.get_variable_profile(name)
            for name in self.get_variable_names()
        }
        time_range = self._time_range()

        return {
            "dataset_name": self.dataset.attrs.get("title", self.file_path.name if self.file_path else "Loaded dataset"),
            "file_path": str(self.file_path) if self.file_path else "",
            "file_size_bytes": int(file_size),
            "file_size": self._format_file_size(file_size),
            "dimensions": self.get_dimensions(),
            "coordinates": self.get_coordinate_ranges(),
            "coordinate_names": self.get_coordinates(),
            "time_range": time_range,
            "variable_count": len(variables),
            "variables": variables,
            "attributes": dict(self.dataset.attrs),
            "validation": self.validation_report,
        }

    def get_validation_report(self):
        return dict(self.validation_report)

    def get_time_dimension_size(self, variable_name):
        if not self.has_variable(variable_name):
            return 0

        variable = self.get_variable(variable_name)
        for dim_name in variable.dims:
            if dim_name.lower() in {"time", "valid_time", "forecast_time"}:
                return int(variable.sizes[dim_name])
        return int(variable.shape[0]) if variable.ndim == 3 else 0

    def _format_file_size(self, size_bytes):
        if size_bytes < 1024:
            return f"{size_bytes} B"
        if size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        return f"{size_bytes / (1024 * 1024):.1f} MB"

    def _time_range(self):
        if self.dataset is None:
            return {}
        for coord_name, coord in self.dataset.coords.items():
            if coord_name.lower() in {"time", "valid_time", "forecast_time"} and coord.size:
                values = coord.values
                return {
                    "name": coord_name,
                    "start": str(values[0]),
                    "end": str(values[-1]),
                    "count": int(coord.size),
                }
        return {}

    def _numeric_values(self, data_array):
        try:
            return np.asarray(data_array.values, dtype=float)
        except (TypeError, ValueError):
            return None

    def _derived_wind_speed(self):
        if self.dataset is None:
            return None
        wind = self.normalizer.resolve(self.dataset)["wind"]
        if not wind.get("vector_available"):
            return None
        u = self.dataset[wind["u"]]
        v = self.dataset[wind["v"]]
        speed = np.sqrt(u**2 + v**2)
        speed.name = "wind_speed"
        speed.attrs["long_name"] = "Derived wind speed"
        speed.attrs["units"] = u.attrs.get("units", "m/s")
        speed.attrs["derived_from"] = f"{wind['u']}, {wind['v']}"
        return speed

    def _loader_for_suffix(self, suffix):
        if suffix in SUPPORTED_NETCDF_EXTENSIONS:
            return self.loaders["netcdf"]
        if suffix in SUPPORTED_GRIB_EXTENSIONS:
            return self.loaders["grib"]
        if suffix in SUPPORTED_GRD_EXTENSIONS:
            return self.loaders["grd"]
        raise ValueError(f"Unsupported dataset suffix: {suffix}")
