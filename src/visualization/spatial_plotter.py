import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QSlider, QVBoxLayout, QWidget

from src.utils.constants import CARTOPY_CACHE_DIR
from src.visualization.widgets.dashboard_visuals import C

try:
    import cartopy
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    import cartopy.io.shapereader as shapereader

    cartopy.config["data_dir"] = str(CARTOPY_CACHE_DIR)
except ImportError:
    ccrs = None
    cfeature = None
    shapereader = None


class ScientificMapPanel(QWidget):
    """Matplotlib geospatial heatmap based on dataset latitude/longitude arrays."""

    layer_requested = pyqtSignal(str)
    layer_toggled = pyqtSignal(str, bool)
    opacity_changed = pyqtSignal(float)
    region_selected = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.figure = Figure(facecolor="#101722")
        self.canvas = FigureCanvas(self.figure)
        self._view_data = None
        self._axis = None
        self._hud = None
        self._layer_buttons = {}
        self._feature_cache = {}
        self._projection_name = "Auto"
        self._region_start = None
        self._region_bounds = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._layer_bar())
        layout.addWidget(self.canvas)
        self.canvas.mpl_connect("motion_notify_event", self._inspect_point)
        self.canvas.mpl_connect("button_press_event", self._inspect_point)
        self.canvas.mpl_connect(
            "figure_leave_event",
            self._hide_hover_info,
        )
        self.canvas.mpl_connect("button_press_event", self._region_press)
        self.canvas.mpl_connect("button_release_event", self._region_release)
        self.clear()

    def set_layers(self, layers):
        self._layer_buttons.clear()
        while self.layer_layout.count():
            item = self.layer_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        for layer in layers:
            button = QPushButton(layer["label"])
            button.setToolTip(f"{layer['name']} layer: {layer['variable']}")
            button.setProperty("category", layer["category"])
            button.setCheckable(True)
            button.clicked.connect(lambda checked=False, category=layer["category"]: self._layer_button_clicked(category, checked))
            button.setFixedSize(48, 30)
            button.setStyleSheet(self._button_style(False))
            self.layer_layout.addWidget(button)
            self._layer_buttons[layer["category"]] = button
        self.layer_layout.addStretch()

    def render(self, view_data):
        self._view_data = view_data
        self.figure.clear()
        projection = self._projection_for(view_data) if ccrs is not None else None
        projection_kind = self._projection_kind(view_data)
        axis_box, colorbar_box = self._layout_boxes(projection_kind, projection is not None)
        axis = self.figure.add_axes(axis_box, projection=projection) if projection is not None else self.figure.add_axes(axis_box)
        self._axis = axis
        axis.set_anchor("C")
        axis.set_aspect("equal", adjustable="box")
        axis.set_facecolor("#0d1420")
        axis.tick_params(colors="#dce8f2", labelsize=9)
        axis.xaxis.label.set_color("#dce8f2")
        axis.yaxis.label.set_color("#dce8f2")
        axis.title.set_color("#f0f6ff")

        lon = view_data["lon"]
        lat = view_data["lat"]
        values = view_data["values"]
        cmap = self._colormap(view_data.get("category", "generic"))

        mesh_kwargs = {"shading": "auto", "cmap": cmap, "alpha": 0.92, "zorder": 3}
        if projection is not None:
            mesh_kwargs["transform"] = ccrs.PlateCarree()
        if projection is not None:
            self._draw_cartopy_context(axis, lon, lat, projection_kind)
        mesh = axis.pcolormesh(lon, lat, values, **mesh_kwargs)
        for overlay in view_data.get("overlays", []):
            self._draw_overlay(axis, overlay, projection)
            if overlay.get("wind_vectors"):
                self._draw_wind_vectors(axis, overlay["lon"], overlay["lat"], overlay, projection)
        self._draw_region_overlay(axis, projection)
        axis.set_title(
            view_data["title"],
            fontsize=13,
            fontweight="bold",
            pad=8,
            color="#f0f6ff",
        )

        if projection is not None:
            self._draw_cartopy_foreground(axis)
        else:
            axis.set_xlabel(f"{view_data['lon_name']} / longitude")
            axis.set_ylabel(f"{view_data['lat_name']} / latitude")
            axis.grid(True, color="#344556", linewidth=0.5, alpha=0.65)

        self._draw_wind_vectors(axis, lon, lat, view_data, projection)
        self._set_active_layer(view_data.get("category"))

        if colorbar_box is None:
            colorbar = self.figure.colorbar(mesh, ax=axis, shrink=0.86, pad=0.02)
        else:
            colorbar = self.figure.colorbar(mesh, cax=self.figure.add_axes(colorbar_box))
        label = view_data.get("long_name", view_data.get("variable", "value"))
        units = view_data.get("units", "")
        colorbar.set_label(f"{label} ({units})" if units else label, color="#dce8f2")
        colorbar.ax.yaxis.set_tick_params(color="#dce8f2", labelcolor="#dce8f2")

        # ---------------------------------------------------------
        # HOVER INSPECTION TOOLTIP
        # ---------------------------------------------------------

        self._hud = axis.annotate(
            "",
            xy=(0, 0),
            xytext=(14, 14),
            textcoords="offset points",
            ha="left",
            va="bottom",
            fontsize=8.5,
            color="#F8FAFC",
            annotation_clip=True,
            zorder=100,
            bbox={
                "boxstyle": "round,pad=0.45",
                "facecolor": "#0B111B",
                "edgecolor": "#49BAFF",
                "linewidth": 1.0,
                "alpha": 0.94,
            },
        )

        self._hud.set_visible(False)

        self.canvas.draw_idle()

    def set_layer_checked(self, category, checked):
        button = self._layer_buttons.get(category)
        if button is not None:
            button.blockSignals(True)
            button.setChecked(checked)
            button.blockSignals(False)

    def set_projection(self, projection_name):
        self._projection_name = projection_name or "Auto"
        if self._view_data is not None:
            self.render(self._view_data)

    def set_region_bounds(self, bounds):
        self._region_bounds = bounds or None
        if self._view_data is not None:
            self.render(self._view_data)

    def clear_region_bounds(self):
        self._region_bounds = None
        if self._view_data is not None:
            self.render(self._view_data)

    def clear(self):
        self._view_data = None
        self._axis = None
        self._hud = None
        self._region_bounds = None
        self.figure.clear()
        axis = self.figure.add_subplot(111)
        axis.set_anchor("C")
        axis.set_facecolor("#0d1420")
        axis.text(
            0.5,
            0.5,
            "Open a NetCDF dataset to view geospatial weather data",
            ha="center",
            va="center",
            color="#9fb4c6",
            transform=axis.transAxes,
        )
        axis.set_axis_off()
        self.canvas.draw_idle()

    def _layout_boxes(self, projection_kind, has_projection):
        """
        Return plotting and colorbar geometry.

        Keep the map dominant. The colorbar gets its own narrow column
        without squeezing the actual globe.
        """

        if not has_projection:
            return [0.06, 0.08, 0.88, 0.86], None

        if projection_kind == "global":
            # Large centered globe with a compact colorbar.
            return (
                [0.035, 0.055, 0.84, 0.89],
                [0.895, 0.16, 0.022, 0.68],
            )

        # Regional projection
        return (
            [0.045, 0.07, 0.84, 0.86],
            [0.895, 0.16, 0.022, 0.68],
        )

    def _layer_bar(self):
        frame = QFrame()
        frame.setStyleSheet(
            f"""
            QFrame{{
                background:#0d1420;
                border:1px solid {C['soft_border']};
                border-bottom:none;
            }}
            QLabel{{color:{C['txt']};background:transparent;border:none;font-weight:600;}}
            """
        )
        root = QHBoxLayout(frame)
        root.setContentsMargins(8, 6, 8, 6)
        root.setSpacing(6)
        root.addWidget(QLabel("Weather Layers"))
        self.layer_layout = QHBoxLayout()
        self.layer_layout.setSpacing(5)
        root.addLayout(self.layer_layout)
        root.addWidget(QLabel("Opacity"))
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(15, 90)
        self.opacity_slider.setValue(45)
        self.opacity_slider.setFixedWidth(100)
        self.opacity_slider.valueChanged.connect(lambda value: self.opacity_changed.emit(value / 100))
        root.addWidget(self.opacity_slider)
        return frame

    def _draw_overlay(self, axis, overlay, projection):
        alpha = float(overlay.get("opacity", 0.45))
        kwargs = {"shading": "auto", "cmap": self._colormap(overlay.get("category", "generic")), "alpha": alpha, "zorder": 3.5}
        if projection is not None:
            kwargs["transform"] = ccrs.PlateCarree()
        if overlay.get("category") == "pressure":
            contour_kwargs = {"colors": "#dce8f2", "linewidths": 0.55, "alpha": max(0.25, alpha), "zorder": 6}
            if projection is not None:
                contour_kwargs["transform"] = ccrs.PlateCarree()
            axis.contour(overlay["lon"], overlay["lat"], overlay["values"], levels=8, **contour_kwargs)
        else:
            axis.pcolormesh(overlay["lon"], overlay["lat"], overlay["values"], **kwargs)

    def _draw_cartopy_context(self, axis, lon, lat, projection_kind):
        lon_values = lon.ravel() if hasattr(lon, "ravel") else lon
        lat_values = lat.ravel() if hasattr(lat, "ravel") else lat
        lon_min, lon_max = float(min(lon_values)), float(max(lon_values))
        lat_min, lat_max = float(min(lat_values)), float(max(lat_values))
        if projection_kind == "regional":
            lon_pad = max(1.0, (lon_max - lon_min) * 0.08)
            lat_pad = max(1.0, (lat_max - lat_min) * 0.08)
            axis.set_extent(
                [lon_min - lon_pad, lon_max + lon_pad, lat_min - lat_pad, lat_max + lat_pad],
                crs=ccrs.PlateCarree(),
            )
        else:
            axis.set_global()
        axis.patch.set_facecolor("#07111d")
        if cfeature is not None:
            if self._feature_ready("physical", "ocean"):
                axis.add_feature(
                    cfeature.NaturalEarthFeature("physical", "ocean", "110m"),
                    facecolor="#071d30",
                    edgecolor="none",
                    zorder=0,
                )
            if self._feature_ready("physical", "land"):
                axis.add_feature(
                    cfeature.NaturalEarthFeature("physical", "land", "110m"),
                    facecolor="#263022",
                    edgecolor="none",
                    alpha=0.68,
                    zorder=0,
                )
            if self._feature_ready("physical", "lakes"):
                axis.add_feature(
                    cfeature.NaturalEarthFeature("physical", "lakes", "110m"),
                    edgecolor="#7894a8",
                    facecolor="#09263a",
                    linewidth=0.25,
                    zorder=1,
                )
        gridlines = axis.gridlines(
            crs=ccrs.PlateCarree(),
            draw_labels=projection_kind == "regional",
            linewidth=0.4,
            color="#52677a",
            alpha=0.75,
            linestyle="--",
        )
        if projection_kind == "regional":
            gridlines.top_labels = False
            gridlines.right_labels = False
            gridlines.xlabel_style = {"color": "#dce8f2", "size": 8}
            gridlines.ylabel_style = {"color": "#dce8f2", "size": 8}

    def _draw_cartopy_foreground(self, axis):
        if self._feature_ready("physical", "coastline"):
            axis.coastlines(resolution="110m", color="#dce8f2", linewidth=0.7, zorder=4)
        if cfeature is not None:
            if self._feature_ready("cultural", "admin_0_boundary_lines_land"):
                axis.add_feature(
                    cfeature.NaturalEarthFeature("cultural", "admin_0_boundary_lines_land", "110m"),
                    edgecolor="#a9bac8",
                    facecolor="none",
                    linewidth=0.45,
                    zorder=4,
                )

    def _draw_wind_vectors(self, axis, lon, lat, view_data, projection):
        vectors = view_data.get("wind_vectors")
        if not vectors:
            return

        u = vectors["u"]
        v = vectors["v"]
        stride = max(1, int(np.ceil(max(u.shape) / 5)))
        lon_grid, lat_grid = np.meshgrid(lon, lat) if np.ndim(lon) == 1 and np.ndim(lat) == 1 else (lon, lat)
        quiver_kwargs = {
            "color": "#7ee7ff",
            "alpha": 0.68,
            "width": 0.0018,
            "scale": 55,
            "zorder": 5,
        }
        if projection is not None:
            quiver_kwargs["transform"] = ccrs.PlateCarree()
        axis.quiver(
            lon_grid[::stride, ::stride],
            lat_grid[::stride, ::stride],
            u[::stride, ::stride],
            v[::stride, ::stride],
            **quiver_kwargs,
        )
        if np.ndim(lon) == 1 and np.ndim(lat) == 1:
            try:
                axis.streamplot(
                    lon,
                    lat,
                    u,
                    v,
                    color="#7ee7ff",
                    linewidth=0.45,
                    density=0.7,
                    arrowsize=0.6,
                    transform=ccrs.PlateCarree() if projection is not None else None,
                    zorder=5,
                )
            except Exception:
                pass

    def _draw_region_overlay(self, axis, projection):
        if not self._region_bounds:
            return

        bounds = self._region_bounds
        lon_min = float(bounds["lon_min"])
        lon_max = float(bounds["lon_max"])
        lat_min = float(bounds["lat_min"])
        lat_max = float(bounds["lat_max"])
        width = lon_max - lon_min
        height = lat_max - lat_min
        if width <= 0 or height <= 0:
            return

        patch_kwargs = {
            "fill": True,
            "facecolor": "#49baff",
            "edgecolor": "#ffffff",
            "linewidth": 2.4,
            "linestyle": "--",
            "alpha": 0.18,
            "zorder": 7,
        }
        if projection is not None:
            patch_kwargs["transform"] = ccrs.PlateCarree()

        rect = Rectangle((lon_min, lat_min), width, height, **patch_kwargs)
        axis.add_patch(rect)
        axis.text(
            lon_min,
            lat_max,
            " Selected region ",
            color="#ffffff",
            fontsize=9,
            va="bottom",
            ha="left",
            bbox={"facecolor": "#0b111b", "edgecolor": "#ffffff", "alpha": 0.96},
            transform=ccrs.PlateCarree() if projection is not None else axis.transData,
            zorder=8,
        )
        for corner_lon, corner_lat in (
            (lon_min, lat_min),
            (lon_min, lat_max),
            (lon_max, lat_min),
            (lon_max, lat_max),
        ):
            scatter_kwargs = {
                "s": 28,
                "facecolor": "#ffffff",
                "edgecolor": "#0b111b",
                "linewidth": 0.8,
                "zorder": 8,
            }
            if projection is not None:
                scatter_kwargs["transform"] = ccrs.PlateCarree()
            axis.scatter([corner_lon], [corner_lat], **scatter_kwargs)

    def _colormap(self, category):
        return {
            "temperature": "coolwarm",
            "humidity": "YlGnBu",
            "pressure": "viridis",
            "wind": "plasma",
            "wind_speed": "plasma",
            "precipitation": "Blues",
        }.get(category, "viridis")

    def _inspect_point(self, event):
        """Show weather information for the grid cell under the cursor."""

        if self._view_data is None:
            return

        if self._axis is None:
            return

        if self._hud is None:
            return

        if event.inaxes is not self._axis:
            self._hide_hover_info()
            return

        if event.xdata is None or event.ydata is None:
            self._hide_hover_info()
            return

        # ---------------------------------------------------------
        # Convert cursor position to geographic coordinates
        # ---------------------------------------------------------

        lon_value, lat_value = self._event_lon_lat(event)

        if lon_value is None or lat_value is None:
            self._hide_hover_info()
            return

        # ---------------------------------------------------------
        # Dataset arrays
        # ---------------------------------------------------------

        lat = np.asarray(
            self._view_data["lat"],
            dtype=float
        )

        lon = np.asarray(
            self._view_data["lon"],
            dtype=float
        )

        values = np.asarray(
            self._view_data["values"],
            dtype=float
        )

        # ---------------------------------------------------------
        # Find nearest grid cell
        # ---------------------------------------------------------

        try:

            if np.ndim(lat) == 1 and np.ndim(lon) == 1:

                lat_index = int(
                    np.nanargmin(
                        np.abs(lat - lat_value)
                    )
                )

                lon_index = int(
                    np.nanargmin(
                        np.abs(lon - lon_value)
                    )
                )

                nearest_lat = float(
                    lat[lat_index]
                )

                nearest_lon = float(
                    lon[lon_index]
                )

                value = float(
                    values[
                        lat_index,
                        lon_index
                    ]
                )

            else:

                distance = (
                    (lat - lat_value) ** 2
                    +
                    (lon - lon_value) ** 2
                )

                flat_index = int(
                    np.nanargmin(distance)
                )

                nearest_lat = float(
                    np.ravel(lat)[flat_index]
                )

                nearest_lon = float(
                    np.ravel(lon)[flat_index]
                )

                value = float(
                    np.ravel(values)[flat_index]
                )

        except (ValueError, IndexError, TypeError):

            self._hide_hover_info()

            return

        # ---------------------------------------------------------
        # Format information
        # ---------------------------------------------------------

        variable = self._view_data.get(
            "variable",
            "Value"
        )

        units = self._view_data.get(
            "units",
            ""
        )

        timestamp = self._view_data.get(
            "timestamp",
            "--"
        )

        if np.isfinite(value):

            value_text = (
                f"{value:.4f} {units}"
            ).strip()

        else:

            value_text = "N/A"

        # ---------------------------------------------------------
        # Tooltip
        # ---------------------------------------------------------

        tooltip = "\n".join(
            [
                "Spatial Inspection",
                f"Time: {timestamp}",
                f"Latitude: {nearest_lat:.3f}°",
                f"Longitude: {nearest_lon:.3f}°",
                f"{variable}: {value_text}",
            ]
        )

        self._hud.set_text(
            tooltip
        )

        # ---------------------------------------------------------
        # Keep tooltip next to cursor
        # ---------------------------------------------------------

        self._hud.xy = (
            event.xdata,
            event.ydata,
        )

        canvas_width = self.canvas.get_width_height()[0]

        if event.x is not None and event.x > canvas_width * 0.72:

            self._hud.set_position(
                (-14, 14)
            )

            self._hud.set_ha(
                "right"
            )

        else:

            self._hud.set_position(
                (14, 14)
            )

            self._hud.set_ha(
                "left"
            )

        # ---------------------------------------------------------
        # Show tooltip
        # ---------------------------------------------------------

        self._hud.set_visible(
            True
        )

        self.canvas.draw_idle()

    def _hide_hover_info(self):
        """Hide the weather inspection tooltip."""

        if self._hud is not None:

            self._hud.set_visible(
                False
            )

            self.canvas.draw_idle()

    def _set_active_layer(self, category):
        for layer_category, button in self._layer_buttons.items():
            button.setStyleSheet(self._button_style(layer_category == category))

    def _button_style(self, active):
        border = C["cyan"] if active else C["soft_border"]
        background = "#1f3546" if active else C["card"]
        color = "#ffffff" if active else C["txt"]
        return (
            f"QPushButton{{background:{background};border:1px solid {border};"
            f"border-radius:4px;color:{color};font-size:10px;font-weight:bold;}}"
            f"QPushButton:hover{{border-color:{C['cyan']};}}"
        )

    def _layer_button_clicked(self, category, checked):
        self.layer_requested.emit(category)
        self.layer_toggled.emit(category, checked)

    def _region_press(self, event):
        if event.button != 1 or event.inaxes is not self._axis:
            return
        self._region_start = self._event_lon_lat(event)

    def _region_release(self, event):
        if self._region_start is None or event.button != 1 or event.inaxes is not self._axis:
            self._region_start = None
            return
        end = self._event_lon_lat(event)
        start = self._region_start
        self._region_start = None
        if start[0] is None or end[0] is None:
            return
        lon_min, lon_max = sorted([start[0], end[0]])
        lat_min, lat_max = sorted([start[1], end[1]])
        if abs(lon_max - lon_min) < 0.05 or abs(lat_max - lat_min) < 0.05:
            return
        self.region_selected.emit(
            {"lon_min": lon_min, "lon_max": lon_max, "lat_min": lat_min, "lat_max": lat_max}
        )

    def _projection_for(self, view_data):
        projection_name = self._projection_name
        if projection_name == "PlateCarree":
            return ccrs.PlateCarree()
        if projection_name == "Mercator":
            return ccrs.Mercator()
        if projection_name == "Orthographic":
            lon = np.asarray(view_data["lon"], dtype=float)
            lat = np.asarray(view_data["lat"], dtype=float)
            return ccrs.Orthographic(
                central_longitude=float(np.nanmean(lon)),
                central_latitude=float(np.nanmean(lat)),
            )
        if self._projection_kind(view_data) == "regional":
            return ccrs.PlateCarree()
        lon = np.asarray(view_data["lon"], dtype=float)
        lat = np.asarray(view_data["lat"], dtype=float)
        central_lon = float(np.nanmean(lon))
        central_lat = float(np.nanmean(lat))
        return ccrs.Orthographic(central_longitude=central_lon, central_latitude=central_lat)

    def _projection_kind(self, view_data):
        lon = np.asarray(view_data["lon"], dtype=float)
        lat = np.asarray(view_data["lat"], dtype=float)
        lon_span = float(np.nanmax(lon) - np.nanmin(lon))
        lat_span = float(np.nanmax(lat) - np.nanmin(lat))
        return "global" if lon_span >= 120 or lat_span >= 70 else "regional"

    def _event_lon_lat(self, event):
        if ccrs is None or not hasattr(self._axis, "projection"):
            return float(event.xdata), float(event.ydata)
        try:
            lon_value, lat_value = ccrs.PlateCarree().transform_point(
                float(event.xdata),
                float(event.ydata),
                self._axis.projection,
            )
            if not np.isfinite(lon_value) or not np.isfinite(lat_value):
                return None, None
            return lon_value, lat_value
        except Exception:
            return None, None

    def _feature_ready(self, category, name):
        if shapereader is None:
            return False
        key = (category, name)
        if key not in self._feature_cache:
            try:
                shapereader.natural_earth(
                    resolution="110m",
                    category=category,
                    name=name,
                )
                self._feature_cache[key] = True
            except Exception:
                self._feature_cache[key] = False
        return self._feature_cache[key]
