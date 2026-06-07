# Weather Data Analysis and Forecasting System

This is the first working MVC milestone for the desktop weather analytics project,
now using the v2.1 dashboard-style interface.

## What Works Now

- Open NetCDF datasets (`.nc`, `.netcdf`, `.cdf`)
- Store the loaded dataset as an `xarray.Dataset`
- Extract dimensions, coordinates, variables, units, shapes, data types, and attributes
- Display metadata in a dark PyQt5 dashboard UI
- Select a variable from the dataset
- Preview the selected variable with Matplotlib
- Show quick statistics: count, mean, standard deviation, minimum, maximum
- Export metadata snapshots to `data/exports`
- Show a compact GIS-style globe, telemetry table, live widgets, and satellite tiles

## How To Run

From the project root:

```powershell
.\venv\Scripts\python.exe app.py
```

Then choose **Open Dataset** and select a NetCDF file.

## Current Architecture

```text
app.py
config/
model/
  loaders/
  core/
  processing/
view/
  widgets/
controller/
utils/
data/
```

## MVC Flow

```text
User opens dataset
        |
MainController
        |
DatasetManager -> NetCDFLoader -> xarray.Dataset
        |
MetadataExtractor + AnalysisEngine
        |
MainWindow + MetadataViewer + PlotPanel
```

## Next Milestones

1. Add GRD parsing.
2. Add GRIB loading through `cfgrib`.
3. Replace the basic Matplotlib image preview with Cartopy map projections.
4. Add histogram, PDF, and CDF plots.
5. Add forecasting with ARIMA or regression models.
6. Generate HTML/PDF reports.
