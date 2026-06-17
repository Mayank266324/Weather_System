from PyQt5.QtCore import QTimer

from model.core.dataset_manager import DatasetManager
from model.export_manager import ExportManager
from model.forecasting.forecast_manager import ForecastManager
from model.processing.analysis import AnalysisEngine
from model.processing.dataset_view import DatasetViewBuilder
from model.processing.metadata import MetadataExtractor
from model.report_manager import ReportManager


class MainController:
    """Coordinates GUI events with the model layer."""

    def __init__(self, view):
        self.view = view
        self.dataset_manager = DatasetManager()
        self.metadata_extractor = MetadataExtractor()
        self.analysis_engine = AnalysisEngine()
        self.dataset_view_builder = DatasetViewBuilder()
        self.forecast_manager = ForecastManager()
        self.export_manager = ExportManager()
        self.report_manager = ReportManager()
        self.metadata = {}
        self.current_variable = None
        self.current_rows = []
        self.current_statistics = {}
        self.active_overlay_layers = []
        self.layer_opacity = 0.45
        self.region_bounds = None
        self._pending_time_index = 0
        self._refresh_timer = QTimer(self.view)
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.timeout.connect(self._flush_refresh)

        self.view.open_dataset_requested.connect(self.open_dataset)
        self.view.close_dataset_requested.connect(self.close_dataset)
        self.view.variable_selected.connect(self.select_variable)
        self.view.weather_layer_selected.connect(self.select_weather_layer)
        self.view.weather_layer_toggled.connect(self.toggle_weather_layer)
        self.view.layer_opacity_changed.connect(self.set_layer_opacity)
        self.view.region_selected.connect(self.select_region)
        self.view.time_slice_changed.connect(self.refresh_current_variable)
        self.view.export_metadata_requested.connect(self.export_metadata)
        self.view.export_telemetry_requested.connect(self.export_telemetry)
        self.view.export_dataset_requested.connect(self.export_dataset)
        self.view.generate_report_requested.connect(self.generate_report)
        self.view.run_forecast_requested.connect(self.run_forecast)

    def open_dataset(self):
        file_path = self.view.choose_dataset_file()
        if not file_path:
            return

        try:
            dataset = self.dataset_manager.load_dataset(file_path)
            self.metadata = self.metadata_extractor.extract(dataset)
            self.view.set_metadata(self.metadata)
            self.view.set_dataset_summary(self.dataset_manager.get_dataset_info())
            self.view.set_time_labels(self.dataset_view_builder.time_labels(dataset))
            self.view.set_weather_layers(self.dataset_view_builder.weather_layer_options(dataset))
            self.view.set_variables(self.dataset_manager.get_variable_names())
            self.view.set_status(f"Loaded dataset: {file_path}")
        except Exception as error:
            self.view.show_error("Dataset Load Failed", str(error))
            self.view.set_status("Dataset load failed.")

    def select_variable(self, variable_name):
        if not self.dataset_manager.has_variable(variable_name):
            return

        try:
            self.current_variable = variable_name
            current_time = self.view.current_time_slice()
            self.view.configure_time_slice(
                self.dataset_manager.get_time_dimension_size(variable_name),
                current_time,
            )
            self._schedule_refresh(variable_name, self.view.current_time_slice())
        except Exception as error:
            self.view.show_error("Variable Preview Failed", str(error))

    def refresh_current_variable(self, time_index):
        if not self.current_variable or not self.dataset_manager.has_variable(self.current_variable):
            return

        try:
            self._schedule_refresh(self.current_variable, time_index)
        except Exception as error:
            self.view.show_error("Variable Preview Failed", str(error))

    def select_weather_layer(self, category):
        dataset = self.dataset_manager.get_dataset()
        if dataset is None:
            return
        variable_name = self.dataset_view_builder.find_variable_for_category(dataset, category)
        if not variable_name:
            return
        self.view.set_current_variable(variable_name)
        self.select_variable(variable_name)

    def toggle_weather_layer(self, category, enabled):
        if enabled and category not in self.active_overlay_layers:
            self.active_overlay_layers.append(category)
        if not enabled and category in self.active_overlay_layers:
            self.active_overlay_layers.remove(category)
        if self.current_variable:
            self._schedule_refresh(self.current_variable, self.view.current_time_slice())

    def set_layer_opacity(self, opacity):
        self.layer_opacity = opacity
        if self.current_variable:
            self._schedule_refresh(self.current_variable, self.view.current_time_slice())

    def select_region(self, bounds):
        self.region_bounds = bounds
        self.view.set_region_bounds(bounds)
        if self.current_variable:
            self._schedule_refresh(self.current_variable, self.view.current_time_slice())

    def close_dataset(self):
        self.dataset_manager.close_dataset()
        self.metadata = {}
        self.current_variable = None
        self.view.reset_dataset_view()
        self.active_overlay_layers = []
        self.region_bounds = None
        self.view.clear_region_bounds()
        self.view.set_status("Dataset closed.")

    def _refresh_all(self, variable_name, time_index):
        dataset = self.dataset_manager.get_dataset()
        data_array = self.dataset_manager.get_variable(variable_name)
        spatial_view = self.dataset_view_builder.multi_layer_view(
            dataset,
            variable_name,
            time_index,
            self.active_overlay_layers,
            {category: self.layer_opacity for category in self.active_overlay_layers},
        )
        slice_stats = self.dataset_view_builder.variable_statistics(dataset, variable_name, time_index)
        if self.region_bounds:
            slice_stats.update(
                self.dataset_view_builder.regional_statistics(
                    dataset,
                    variable_name,
                    time_index,
                    self.region_bounds,
                )
            )
        metrics = self.dataset_view_builder.metric_summary(dataset, time_index)
        rows = self.dataset_view_builder.grid_rows(
            dataset,
            variable_name,
            time_index,
            region_bounds=self.region_bounds,
        )
        comparison_series = self.dataset_view_builder.comparison_series(dataset, variable_name)
        anomaly_summary = self.analysis_engine.anomaly_summary(
            self.dataset_view_builder._time_slice(data_array, time_index)
        )
        slice_stats["anomaly_count"] = anomaly_summary.get("count", 0)
        slice_stats["anomaly_percent"] = anomaly_summary.get("percent", "0.00")
        self.current_rows = rows
        self.current_statistics = slice_stats

        self.view.set_map_data(spatial_view)
        self.view.set_variable_plot(data_array, time_index, comparison_series)
        self.view.set_slice_statistics(slice_stats)
        self.view.set_metrics(metrics)
        self.view.set_grid_rows(rows)
        self.view.set_status(
            f"Showing {variable_name} at {spatial_view['timestamp']} "
            f"({len(rows)} inspected grid cells"
            f"{'; regional selection active' if self.region_bounds else ''})"
        )

    def _schedule_refresh(self, variable_name, time_index):
        self._pending_variable = variable_name
        self._pending_time_index = int(time_index)
        self._refresh_timer.start(120)

    def _flush_refresh(self):
        variable_name = getattr(self, "_pending_variable", None)
        if not variable_name:
            return
        if not self.dataset_manager.has_variable(variable_name):
            return
        self._refresh_all(variable_name, self._pending_time_index)

    def export_metadata(self):
        if not self.metadata:
            self.view.show_info("Nothing to Export", "Open a dataset before exporting metadata.")
            return

        try:
            output_path = self.export_manager.export_metadata(
                self.metadata,
                self.dataset_manager.file_path,
            )
            self.view.show_info("Metadata Exported", f"Saved metadata to:\n{output_path}")
            self.view.set_status(f"Metadata exported: {output_path}")
        except Exception as error:
            self.view.show_error("Export Failed", str(error))

    def export_telemetry(self):
        if not self.current_rows:
            self.view.show_info("Nothing to Export", "Load a dataset and select a variable first.")
            return
        try:
            output_path = self.export_manager.export_telemetry_csv(self.current_rows)
            self.view.show_info("Telemetry Exported", f"Saved telemetry to:\n{output_path}")
        except Exception as error:
            self.view.show_error("Export Failed", str(error))

    def export_dataset(self):
        dataset = self.dataset_manager.get_dataset()
        if dataset is None:
            self.view.show_info("Nothing to Export", "Open a dataset first.")
            return
        try:
            output_path = self.export_manager.export_dataset_netcdf(dataset)
            self.view.show_info("Dataset Exported", f"Saved processed dataset to:\n{output_path}")
        except Exception as error:
            self.view.show_error("Export Failed", str(error))

    def generate_report(self):
        dataset = self.dataset_manager.get_dataset()
        if dataset is None or not self.current_variable:
            self.view.show_info("Nothing to Report", "Open a dataset and select a variable first.")
            return
        try:
            summary = self.dataset_manager.get_dataset_info()
            html_path = self.report_manager.generate_html_report(
                self.metadata,
                summary,
                self.current_variable,
                self.current_statistics,
                self.current_rows,
            )
            pdf_path = self.report_manager.generate_pdf_report(
                dataset,
                summary,
                self.current_variable,
                self.current_statistics,
            )
            self.view.show_info("Reports Generated", f"HTML:\n{html_path}\n\nPDF:\n{pdf_path}")
        except Exception as error:
            self.view.show_error("Report Failed", str(error))

    def run_forecast(self, config):
        dataset = self.dataset_manager.get_dataset()
        variable_name = config.get("variable") if isinstance(config, dict) else self.current_variable
        if dataset is None or not variable_name:
            self.view.show_info("Nothing to Forecast", "Open a dataset and select a weather variable first.")
            return
        if not self.dataset_manager.has_variable(variable_name):
            self.view.show_info("Unsupported Forecast Variable", "Select a variable that exists in the loaded dataset.")
            return

        try:
            mode = config.get("mode", "Linear Regression") if isinstance(config, dict) else str(config)
            window_size = int(config.get("window_size", 3)) if isinstance(config, dict) else 3
            horizon = int(config.get("horizon", 1)) if isinstance(config, dict) else 1
            future_steps = int(config.get("future_steps", 3)) if isinstance(config, dict) else 3
            data_array = self.dataset_manager.get_variable(variable_name)
            forecast = self.forecast_manager.run_forecast(
                data_array,
                variable_name,
                region_bounds=self.region_bounds,
                mode=mode,
                window_size=window_size,
                horizon=horizon,
                future_steps=future_steps,
            )
            self.view.set_forecast(forecast)
            self.view.set_status(
                f"Forecasted {forecast.variable} with {forecast.model_name}; "
                f"RMSE={forecast.metrics.get('rmse', 'n/a')}"
            )
        except Exception as error:
            self.view.show_error("Forecast Failed", str(error))
