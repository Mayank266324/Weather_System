from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from src.visualization.widgets.dashboard_visuals import C, STYLE, Sidebar, apply_palette, font
from src.visualization.widgets.data_grid import DataSliceGrid
from src.visualization.widgets.dataset_summary import DatasetSummaryPanel
from src.visualization.widgets.metadata_viewer import MetadataViewer
from src.visualization.widgets.metrics_panel import MetricsPanel
from src.visualization.widgets.satellite_panel import SatelliteLayerPanel
from src.visualization.forecast_plotter import ForecastPanel
from src.visualization.spatial_plotter import ScientificMapPanel
from src.visualization.time_series_plotter import PlotPanel


class ExpandableSection(QFrame):
    """Compact section container with optional expanded view."""

    def __init__(self, title, widget):
        super().__init__()

        self.widget = widget

        self.setObjectName("sectionFrame")

        self.setStyleSheet(
            f"""
            QFrame#sectionFrame {{
                background: #111B2B;
                border: 1px solid {C['border']};
                border-radius: 12px;
            }}

            QLabel {{
                background: transparent;
                border: none;
                color: {C['txt']};
            }}
            """
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            12, 10, 12, 10
        )

        layout.setSpacing(7)

        # Header
        title_row = QHBoxLayout()
        title_row.setSpacing(8)

        title_label = QLabel(title)
        title_label.setFont(
            font(11, True)
        )

        title_label.setStyleSheet(
            f"color: {C['txt']};"
        )

        title_row.addWidget(title_label)
        title_row.addStretch()

        expand_button = QPushButton("Expand")
        expand_button.setFixedSize(68, 28)
        expand_button.setCursor(
            Qt.PointingHandCursor
        )

        expand_button.setStyleSheet(
            f"""
            QPushButton {{
                background: #172238;
                color: {C['dim']};
                border: 1px solid {C['border']};
                border-radius: 7px;
                padding: 3px 8px;
                font-size: 10px;
                font-weight: 600;
            }}

            QPushButton:hover {{
                background: #1C2D49;
                color: {C['txt']};
                border-color: {C['blue']};
            }}
            """
        )

        expand_button.clicked.connect(
            lambda: self.open_expanded(title)
        )

        title_row.addWidget(
            expand_button
        )

        layout.addLayout(title_row)

        layout.addWidget(
            widget,
            1
        )

    def open_expanded(self, title):
        dialog = QDialog(self)

        dialog.setWindowTitle(title)
        dialog.resize(1100, 760)

        dialog.setStyleSheet(
            f"""
            QDialog {{
                background: {C['bg']};
                color: {C['txt']};
            }}
            """
        )

        layout = QVBoxLayout(dialog)

        layout.setContentsMargins(
            12, 12, 12, 12
        )

        if hasattr(
            self.widget,
            "expanded_copy"
        ):
            expanded = (
                self.widget.expanded_copy()
            )

            layout.addWidget(
                expanded
            )

        else:
            label = QLabel()

            label.setAlignment(
                Qt.AlignCenter
            )

            label.setPixmap(
                self.widget.grab().scaled(
                    1000,
                    650,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setWidget(label)

            layout.addWidget(
                scroll
            )

        dialog.exec_()


class MainWindow(QMainWindow):
    open_dataset_requested = pyqtSignal()
    close_dataset_requested = pyqtSignal()
    export_metadata_requested = pyqtSignal()
    export_telemetry_requested = pyqtSignal()
    export_dataset_requested = pyqtSignal()
    generate_report_requested = pyqtSignal()
    run_forecast_requested = pyqtSignal(dict)
    variable_selected = pyqtSignal(str)
    weather_layer_selected = pyqtSignal(str)
    weather_layer_toggled = pyqtSignal(str, bool)
    layer_opacity_changed = pyqtSignal(float)
    region_selected = pyqtSignal(dict)
    projection_selected = pyqtSignal(str)
    time_slice_changed = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Weather Analytics Platform")
        self.resize(1640, 980)
        self.setStyleSheet(STYLE)

        self._dataset_loaded = False
        self._current_variable = "--"
        self._current_time_text = "--"
        self._current_dataset_name = "Idle"
        self._hero_stat_labels = {}

        app = QApplication.instance()
        if app is not None:
            app.setFont(font(10))
            apply_palette(app)

        self.map_panel = ScientificMapPanel()
        self.map_panel.layer_requested.connect(self.weather_layer_selected.emit)
        self.map_panel.layer_toggled.connect(self.weather_layer_toggled.emit)
        self.map_panel.opacity_changed.connect(self.layer_opacity_changed.emit)
        self.map_panel.region_selected.connect(self.region_selected.emit)
        self.data_grid = DataSliceGrid()
        self.metrics_panel = MetricsPanel()
        self.metadata_viewer = MetadataViewer()
        self.dataset_summary = DatasetSummaryPanel()
        self.plot_panel = PlotPanel()
        self.plot_panel.set_compact_mode(True)
        self.analysis_plot_panel = PlotPanel()
        self.forecast_panel = ForecastPanel()
        self.satellite_panel = SatelliteLayerPanel()

        self.variable_combo = QComboBox()
        self.variable_combo.setMinimumWidth(240)
        self.variable_combo.setStyleSheet(f"color:{C['txt']};background:{C['card']};")
        self.variable_combo.currentTextChanged.connect(self._emit_variable_selection)
        self.projection_combo = QComboBox()
        self.projection_combo.addItems(["Auto", "PlateCarree", "Mercator", "Orthographic"])
        self.projection_combo.setStyleSheet(f"color:{C['txt']};background:{C['card']};")
        self.projection_combo.currentTextChanged.connect(self._emit_projection_selection)
        self.forecast_combo = QComboBox()
        self.forecast_combo.addItems(["Linear Regression", "Moving Average", "LSTM"])
        self.forecast_combo.setMinimumWidth(140)
        self.forecast_combo.setStyleSheet(f"color:{C['txt']};background:{C['card']};")
        self.forecast_variable_combo = QComboBox()
        self.forecast_variable_combo.setMinimumWidth(150)
        self.forecast_variable_combo.setStyleSheet(f"color:{C['txt']};background:{C['card']};")
        self.forecast_window_spin = QSpinBox()
        self.forecast_window_spin.setRange(1, 96)
        self.forecast_window_spin.setValue(3)
        self.forecast_window_spin.setFixedWidth(72)
        self.forecast_horizon_spin = QSpinBox()
        self.forecast_horizon_spin.setRange(1, 24)
        self.forecast_horizon_spin.setValue(1)
        self.forecast_horizon_spin.setFixedWidth(72)
        self.forecast_steps_spin = QSpinBox()
        self.forecast_steps_spin.setRange(1, 48)
        self.forecast_steps_spin.setValue(3)
        self.forecast_steps_spin.setFixedWidth(72)
        for spin in (self.forecast_window_spin, self.forecast_horizon_spin, self.forecast_steps_spin):
            spin.setStyleSheet(f"color:{C['txt']};background:{C['card']};")

        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setEnabled(False)
        self.time_slider.valueChanged.connect(self._time_control_changed)

        self.time_slice_spin = QSpinBox()
        self.time_slice_spin.setMinimum(0)
        self.time_slice_spin.setMaximum(0)
        self.time_slice_spin.setEnabled(False)
        self.time_slice_spin.setStyleSheet(f"color:{C['txt']};background:{C['card']};")
        self.time_slice_spin.valueChanged.connect(self._time_control_changed)

        self.time_label = QLabel("No dataset time coordinate")
        self.time_label.setStyleSheet(f"color:{C['cyan']};font-weight:700;")

        self._build_menu()
        self._build_layout()
        self._build_status_bar()
        self._update_status_indicators()
        self.statusBar().showMessage("Ready. Open a NetCDF dataset to begin.")

    def _build_menu(self):
        file_menu = self.menuBar().addMenu("FILE")

        open_action = QAction("Open Dataset", self)
        open_action.triggered.connect(self.open_dataset_requested.emit)
        file_menu.addAction(open_action)

        export_action = QAction("Export Metadata", self)
        export_action.triggered.connect(self.export_metadata_requested.emit)
        file_menu.addAction(export_action)

        telemetry_action = QAction("Export Telemetry CSV", self)
        telemetry_action.triggered.connect(self.export_telemetry_requested.emit)
        file_menu.addAction(telemetry_action)

        dataset_action = QAction("Export Processed NetCDF", self)
        dataset_action.triggered.connect(self.export_dataset_requested.emit)
        file_menu.addAction(dataset_action)

        report_action = QAction("Generate HTML/PDF Report", self)
        report_action.triggered.connect(self.generate_report_requested.emit)
        file_menu.addAction(report_action)

        close_action = QAction("Close Dataset", self)
        close_action.triggered.connect(self.close_dataset_requested.emit)
        file_menu.addAction(close_action)

        for menu_name in ["VIEW", "TOOLS", "HELP"]:
            self.menuBar().addMenu(menu_name)

    def _build_layout(self):
        """Build the main application shell."""

        root = QWidget()
        self.setCentralWidget(root)

        main_layout = QHBoxLayout(root)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # =========================================================
        # LEFT NAVIGATION
        # =========================================================
        self.sidebar = Sidebar()

        self.sidebar.buttons["dashboard"].clicked.connect(
            lambda: self.show_module("gis")
        )

        self.sidebar.buttons["time-series"].clicked.connect(
            lambda: self.show_module("analysis")
        )

        self.sidebar.buttons["predictive"].clicked.connect(
            lambda: self.show_module("forecast")
        )

        self.sidebar.buttons["export"].clicked.connect(
            self.export_metadata_requested.emit
        )

        # =========================================================
        # CENTER STACK
        # =========================================================
        self.center_stack = QStackedWidget()

        self.gis_page = self._gis_page()
        self.analysis_page = self._analysis_page()
        self.forecast_page = self._forecast_page()

        self.center_stack.addWidget(self.gis_page)
        self.center_stack.addWidget(self.analysis_page)
        self.center_stack.addWidget(self.forecast_page)

        self.center_stack.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        # =========================================================
        # RIGHT INSIGHTS RAIL
        # =========================================================
        right_panel = QWidget()

        right_panel.setMinimumWidth(340)
        right_panel.setMaximumWidth(390)
        right_panel.setSizePolicy(
            QSizePolicy.Fixed,
            QSizePolicy.Expanding
        )

        right_panel.setStyleSheet(
            f"""
            QWidget {{
                background: #0D1524;
                border-left: 1px solid {C['border']};
            }}
            """
        )

        right_panel_layout = QVBoxLayout(right_panel)
        right_panel_layout.setContentsMargins(0, 0, 0, 0)
        right_panel_layout.setSpacing(0)

        # Scrollable rail
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setFrameShape(QScrollArea.NoFrame)
        right_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        right_scroll.setStyleSheet(
            f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}

            QScrollBar:vertical {{
                background: transparent;
                width: 8px;
                margin: 4px 2px;
            }}

            QScrollBar::handle:vertical {{
                background: #33465D;
                min-height: 32px;
                border-radius: 4px;
            }}

            QScrollBar::handle:vertical:hover {{
                background: {C['blue']};
            }}

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0;
            }}

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
            """
        )

        right_content = QWidget()

        right_layout = QVBoxLayout(right_content)
        right_layout.setContentsMargins(14, 14, 14, 14)
        right_layout.setSpacing(10)

        # ---------------------------------------------------------
        # INSIGHTS HEADER
        # ---------------------------------------------------------
        rail_header = QFrame()

        rail_header.setStyleSheet(
            f"""
            QFrame {{
                background: #111B2B;
                border: 1px solid {C['border']};
                border-radius: 12px;
            }}

            QLabel {{
                background: transparent;
                border: none;
            }}
            """
        )

        header_layout = QVBoxLayout(rail_header)
        header_layout.setContentsMargins(14, 12, 14, 12)
        header_layout.setSpacing(4)

        header_title = QLabel("INSIGHTS")
        header_title.setFont(font(12, True))
        header_title.setStyleSheet(
            f"""
            QLabel {{
                color: {C['txt']};
                letter-spacing: 0.8px;
            }}
            """
        )

        header_subtitle = QLabel(
            "Live metrics and analysis context"
        )
        header_subtitle.setFont(font(9))
        header_subtitle.setStyleSheet(
            f"color: {C['dim']};"
        )

        header_layout.addWidget(header_title)
        header_layout.addWidget(header_subtitle)

        right_layout.addWidget(rail_header)

        # ---------------------------------------------------------
        # METRICS
        # ---------------------------------------------------------
        right_layout.addWidget(
            self._section(
                "Atmospheric Breakdown",
                self.metrics_panel,
                expandable=True
            )
        )

        # ---------------------------------------------------------
        # MULTI-VARIABLE CHART
        # ---------------------------------------------------------
        right_layout.addWidget(
            self._section(
                "Multi-Variable Comparison",
                self.plot_panel,
                expandable=True
            )
        )

        # ---------------------------------------------------------
        # SATELLITE
        # ---------------------------------------------------------
        right_layout.addWidget(
            self._section(
                "Satellite / Raster Feed",
                self.satellite_panel,
                expandable=True
            )
        )

        # ---------------------------------------------------------
        # DATASET INFORMATION
        # ---------------------------------------------------------
        info_tabs = QTabWidget()
        info_tabs.setMinimumHeight(230)

        info_tabs.addTab(
            self.dataset_summary,
            "Summary"
        )

        info_tabs.addTab(
            self.metadata_viewer,
            "Metadata"
        )

        right_layout.addWidget(info_tabs)

        right_scroll.setWidget(right_content)
        right_panel_layout.addWidget(right_scroll)

        # =========================================================
        # CENTER + RIGHT SPLITTER
        # =========================================================
        splitter = QSplitter(Qt.Horizontal)

        splitter.setChildrenCollapsible(False)

        splitter.addWidget(self.center_stack)
        splitter.addWidget(right_panel)

        # Center gets almost all available space.
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)

        # Do not force the old 1160/380 geometry.
        # Qt will respect the fixed right rail width.
        splitter.setSizes([1250, 350])

        # =========================================================
        # FINAL SHELL
        # =========================================================
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(splitter, 1)

        self.show_module("gis")

    def _gis_page(self):
        page = QWidget()

        layout = QVBoxLayout(page)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)

        # ---------------------------------------------------------
        # COMMAND HEADER
        # ---------------------------------------------------------
        layout.addWidget(
            self._page_hero(
                "Operational Weather Command Center",
                "Monitor geospatial weather layers and inspect the selected atmospheric slice.",
                [
                    (
                        "dataset",
                        "Dataset",
                        self._current_dataset_text(),
                        C["blue"],
                    ),
                    (
                        "variable",
                        "Variable",
                        self._current_variable,
                        C["cyan"],
                    ),
                    (
                        "time",
                        "Time Slice",
                        self._current_time_text,
                        C["amber"],
                    ),
                ],
            )
        )

        # ---------------------------------------------------------
        # WORKSPACE CONTROLS
        # ---------------------------------------------------------
        layout.addWidget(self._controls_bar())

        # ---------------------------------------------------------
        # MAP
        # ---------------------------------------------------------
        map_section = self._section(
            "Geospatial Weather Visualization",
            self.map_panel
        )

        layout.addWidget(
            map_section,
            1
        )

        # ---------------------------------------------------------
        # BOTTOM DATA AREA
        # ---------------------------------------------------------
        bottom_split = QSplitter(Qt.Horizontal)
        bottom_split.setChildrenCollapsible(False)

        time_widget = self._time_bar()

        data_widget = self._section(
            "Dataset Slice Inspector",
            self.data_grid
        )

        bottom_split.addWidget(time_widget)
        bottom_split.addWidget(data_widget)

        bottom_split.setSizes([330, 1000])

        layout.addWidget(
            bottom_split,
            0
        )

        return page

    def _analysis_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(14)
        layout.addWidget(
            self._page_hero(
                "Time-Series Analysis Studio",
                "Interpret the selected variable through compact narrative cards while the live comparison plot remains on the insight rail.",
                [
                    ("dataset", "Dataset", self._current_dataset_text(), C["blue"]),
                    ("variable", "Variable", self._current_variable, C["cyan"]),
                    ("time", "Time Slice", self._current_time_text, C["amber"]),
                ],
            )
        )
        layout.addWidget(self._section("Time-Series Comparison", self.analysis_plot_panel), 1)
        return page

    def _forecast_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(14)
        layout.addWidget(
            self._page_hero(
                "Predictive Modeling Studio",
                "Configure a forecasting model, validate its holdout performance, and project future weather values.",
                [
                    ("dataset", "Dataset", self._current_dataset_text(), C["blue"]),
                    ("variable", "Variable", self._current_variable, C["cyan"]),
                    ("time", "Time Slice", self._current_time_text, C["amber"]),
                ],
            )
        )
        forecast_split = QSplitter(Qt.Horizontal)
        control_lane = QWidget()
        control_layout = QVBoxLayout(control_lane)
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.setSpacing(14)
        control_layout.addWidget(self._forecast_controls_bar())
        control_note = QFrame()
        control_note.setStyleSheet(f"background:rgba(26,35,51,204);border:1px solid {C['border']};border-radius:16px;")
        note_layout = QVBoxLayout(control_note)
        note_layout.setContentsMargins(16, 16, 16, 16)
        note_layout.setSpacing(10)
        note_layout.addWidget(QLabel("Forecast Guidance"))
        note_layout.addWidget(QLabel("Choose a variable, align the lookback window, and the forecast panel will update with the latest actual vs predicted trajectory."))
        note_layout.addStretch()
        control_layout.addWidget(control_note)
        control_layout.addStretch()

        forecast_split.addWidget(control_lane)
        forecast_split.addWidget(self._section("Forecast Analysis Workspace", self.forecast_panel, expandable=False))
        forecast_split.setSizes([360, 1030])
        layout.addWidget(forecast_split, 1)
        return page

    def _controls_bar(self):
        frame = QFrame()
        frame.setObjectName("controlsBar")
        frame.setStyleSheet(
            f"""
            QFrame#controlsBar{{
                background:rgba(26,35,51,206);
                border:1px solid {C['border']};
                border-radius:16px;
            }}
            QLabel{{background:transparent;border:none;color:{C['txt']};}}
            """
        )
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(12)

        top_row = QHBoxLayout()
        top_text = QVBoxLayout()
        title = QLabel("Workspace Controls")
        title.setFont(font(13, True))
        subtitle = QLabel("Primary dataset actions stay fixed at the top of the map workspace.")
        subtitle.setStyleSheet(f"color:{C['dim']};font-size:11px;")
        top_text.addWidget(title)
        top_text.addWidget(subtitle)
        top_row.addLayout(top_text)
        top_row.addStretch()

        open_button = QPushButton("Open Dataset")
        open_button.clicked.connect(self.open_dataset_requested.emit)
        export_button = QPushButton("Export Metadata")
        export_button.clicked.connect(self.export_metadata_requested.emit)
        close_button = QPushButton("Close Dataset")
        close_button.clicked.connect(self.close_dataset_requested.emit)
        for button in (open_button, export_button, close_button):
            button.setCursor(Qt.PointingHandCursor)
        top_row.addWidget(open_button)
        top_row.addWidget(export_button)
        top_row.addWidget(close_button)
        layout.addLayout(top_row)

        variable_label = QLabel("Variable")
        variable_label.setStyleSheet(f"color:{C['dim']};font-weight:600;background:transparent;border:none;")
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(12)
        bottom_row.addWidget(variable_label)
        bottom_row.addWidget(self.variable_combo)
        bottom_row.addWidget(QLabel("Projection"))
        bottom_row.addWidget(self.projection_combo)
        bottom_row.addStretch()
        bottom_row.addWidget(QLabel("Active Variable"))
        bottom_row.addWidget(QLabel(self._current_variable))
        layout.addLayout(bottom_row)
        return frame

    def _forecast_controls_bar(self):
        frame = QFrame()
        frame.setObjectName("forecastControlsBar")
        frame.setStyleSheet(
            f"""
            QFrame#forecastControlsBar{{
                background:rgba(26,35,51,206);
                border:1px solid {C['border']};
                border-radius:16px;
            }}
            QLabel{{background:transparent;border:none;color:{C['txt']};}}
            """
        )
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(12)

        top_row = QHBoxLayout()
        title_col = QVBoxLayout()
        title = QLabel("Forecast Controls")
        title.setFont(font(13, True))
        subtitle = QLabel("Set model, window, and horizon before generating the operational forecast.")
        subtitle.setStyleSheet(f"color:{C['dim']};font-size:11px;")
        title_col.addWidget(title)
        title_col.addWidget(subtitle)
        top_row.addLayout(title_col)
        top_row.addStretch()

        run_button = QPushButton("Run Forecast")
        run_button.setMinimumWidth(144)
        run_button.clicked.connect(self._emit_forecast_request)
        top_row.addWidget(run_button)
        layout.addLayout(top_row)

        parameter_row = QGridLayout()
        parameter_row.setHorizontalSpacing(10)
        parameter_row.setVerticalSpacing(8)
        parameter_row.addWidget(QLabel("Variable"), 0, 0)
        parameter_row.addWidget(self.forecast_variable_combo, 0, 1)
        parameter_row.addWidget(QLabel("Model"), 0, 2)
        parameter_row.addWidget(self.forecast_combo, 0, 3)
        parameter_row.addWidget(QLabel("Window"), 1, 0)
        parameter_row.addWidget(self.forecast_window_spin, 1, 1)
        parameter_row.addWidget(QLabel("Horizon"), 1, 2)
        parameter_row.addWidget(self.forecast_horizon_spin, 1, 3)
        parameter_row.addWidget(QLabel("Future Steps"), 1, 4)
        parameter_row.addWidget(self.forecast_steps_spin, 1, 5)
        parameter_row.setColumnStretch(1, 1)
        parameter_row.setColumnStretch(3, 1)
        layout.addLayout(parameter_row)
        return frame

    def _time_bar(self):
        frame = QFrame()
        frame.setObjectName("timeBar")
        frame.setStyleSheet(
            f"""
            QFrame#timeBar{{
                background:rgba(26,35,51,206);
                border:1px solid {C['border']};
                border-radius:16px;
            }}
            QLabel{{background:transparent;border:none;color:{C['txt']};}}
            """
        )
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        header = QHBoxLayout()
        label = QLabel("Time Evolution")
        label.setFont(font(11, True))
        header.addWidget(label)
        header.addStretch()
        header.addWidget(self.time_label)
        layout.addLayout(header)

        control_row = QHBoxLayout()
        control_row.setSpacing(10)
        control_row.addWidget(self.time_slider, 1)
        control_row.addWidget(self.time_slice_spin)
        layout.addLayout(control_row)
        return frame

    def _section(self, title, widget, expandable=False):
        if expandable:
            return ExpandableSection(title, widget)

        frame = QFrame()
        frame.setObjectName("sectionFrame")

        frame.setStyleSheet(
            f"""
            QFrame#sectionFrame {{
                background: #111B2B;
                border: 1px solid {C['border']};
                border-radius: 12px;
            }}

            QLabel {{
                background: transparent;
                border: none;
                color: {C['txt']};
            }}
            """
        )

        layout = QVBoxLayout(frame)

        layout.setContentsMargins(
            12, 10, 12, 10
        )

        layout.setSpacing(8)

        title_label = QLabel(title)

        title_label.setFont(
            font(12, True)
        )

        title_label.setStyleSheet(
            f"""
            QLabel {{
                color: {C['txt']};
                padding-bottom: 2px;
            }}
            """
        )

        layout.addWidget(title_label)
        layout.addWidget(widget, 1)

        return frame

    def _page_hero(self, title, subtitle, stats):
        frame = QFrame()

        frame.setObjectName("pageHero")

        frame.setStyleSheet(
            f"""
            QFrame#pageHero {{
                background: #0F1828;
                border: 1px solid {C['border']};
                border-radius: 14px;
            }}

            QLabel {{
                background: transparent;
                border: none;
            }}
            """
        )

        layout = QVBoxLayout(frame)

        layout.setContentsMargins(
            16, 13, 16, 13
        )

        layout.setSpacing(8)

        # ---------------------------------------------------------
        # TITLE ROW
        # ---------------------------------------------------------
        top_row = QHBoxLayout()
        top_row.setSpacing(12)

        text_column = QVBoxLayout()
        text_column.setSpacing(2)

        title_label = QLabel(title)

        title_label.setFont(
            font(18, True)
        )

        title_label.setStyleSheet(
            f"""
            QLabel {{
                color: {C['txt']};
                letter-spacing: 0.1px;
            }}
            """
        )

        subtitle_label = QLabel(subtitle)

        subtitle_label.setWordWrap(True)
        subtitle_label.setFont(
            font(9)
        )

        subtitle_label.setStyleSheet(
            f"""
            QLabel {{
                color: {C['dim']};
            }}
            """
        )

        text_column.addWidget(
            title_label
        )

        text_column.addWidget(
            subtitle_label
        )

        top_row.addLayout(
            text_column,
            1
        )

        badge = QLabel(
            "WEATHER ANALYTICS"
        )

        badge.setAlignment(
            Qt.AlignCenter
        )

        badge.setStyleSheet(
            f"""
            QLabel {{
                background: #162641;
                color: {C['cyan']};
                border: 1px solid #294363;
                border-radius: 7px;
                padding: 6px 10px;
                font-size: 9px;
                font-weight: 700;
                letter-spacing: 0.4px;
            }}
            """
        )

        top_row.addWidget(
            badge,
            0,
            Qt.AlignTop
        )

        layout.addLayout(
            top_row
        )

        # ---------------------------------------------------------
        # STATUS TILES
        # ---------------------------------------------------------
        stat_row = QHBoxLayout()
        stat_row.setSpacing(8)

        for key, label_text, value_text, accent in stats:
            stat_row.addWidget(
                self._stat_tile(
                    key,
                    label_text,
                    value_text,
                    accent
                ),
                1
            )

        layout.addLayout(
            stat_row
        )

        return frame

    def _stat_tile(self, key, label_text, value_text, accent):
        frame = QFrame()

        frame.setStyleSheet(
            f"""
            QFrame {{
                background: #151F30;
                border: 1px solid {C['border']};
                border-radius: 9px;
            }}

            QLabel {{
                background: transparent;
                border: none;
            }}
            """
        )

        layout = QVBoxLayout(frame)

        layout.setContentsMargins(
            10, 7, 10, 7
        )

        layout.setSpacing(1)

        label = QLabel(
            label_text.upper()
        )

        label.setFont(
            font(8, True)
        )

        label.setStyleSheet(
            f"""
            QLabel {{
                color: {C['dim']};
                letter-spacing: 0.5px;
            }}
            """
        )

        value = QLabel(
            value_text
        )

        value.setFont(
            font(14, True)
        )

        value.setStyleSheet(
            f"""
            QLabel {{
                color: {accent};
            }}
            """
        )

        value.setTextInteractionFlags(
            Qt.TextSelectableByMouse
        )

        layout.addWidget(label)
        layout.addWidget(value)

        self._hero_stat_labels[key] = value

        return frame

    def _current_dataset_text(self):
        return getattr(self, "_current_dataset_name", "Loaded" if self._dataset_loaded else "Idle")

    def _sync_hero_stats(self):
        if "dataset" in self._hero_stat_labels:
            self._hero_stat_labels["dataset"].setText(self._current_dataset_text())
        if "variable" in self._hero_stat_labels:
            self._hero_stat_labels["variable"].setText(self._current_variable)
        if "time" in self._hero_stat_labels:
            self._hero_stat_labels["time"].setText(self._current_time_text)

    def _build_status_bar(self):
        bar = QStatusBar(self)
        bar.setSizeGripEnabled(False)
        bar.setStyleSheet(
            f"""
            QStatusBar{{background:rgba(11,18,32,0.98);border-top:1px solid {C['border']};color:{C['dim']};}}
            QStatusBar::item{{border:none;}}
            QLabel{{color:{C['txt']};background:transparent;border:none;}}
            """
        )
        self.setStatusBar(bar)

        self.status_ready_label = QLabel("READY")
        self.status_dataset_label = QLabel("Dataset: not loaded")
        self.status_variable_label = QLabel("Variable: --")
        self.status_time_label = QLabel("Time slice: --")

        labels = (
            self.status_ready_label,
            self.status_dataset_label,
            self.status_variable_label,
            self.status_time_label,
        )
        for status_label in labels:
            status_label.setStyleSheet(
                f"background:rgba(255,255,255,0.04);border:1px solid {C['border']};border-radius:10px;padding:5px 10px;color:{C['txt']};"
            )
            bar.addPermanentWidget(status_label)

    def _update_status_indicators(self):
        self.status_ready_label.setText("READY")
        self.status_dataset_label.setText("Dataset: loaded" if self._dataset_loaded else "Dataset: not loaded")
        self.status_variable_label.setText(f"Variable: {self._current_variable}")
        self.status_time_label.setText(f"Time slice: {self._current_time_text}")

    def choose_dataset_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Weather Dataset",
            "",
            "Weather Datasets (*.nc *.nc4 *.netcdf *.cdf *.grib *.grb *.grib2 *.grb2 *.grd);;"
            "NetCDF Files (*.nc *.nc4 *.netcdf *.cdf);;"
            "GRIB Files (*.grib *.grb *.grib2 *.grb2);;"
            "GRD Files (*.grd);;"
            "All Files (*)",
        )
        return file_path

    def set_metadata(self, metadata):
        self.metadata_viewer.set_metadata(metadata)

    def set_dataset_summary(self, summary):
        self.dataset_summary.set_summary(summary)
        self.satellite_panel.set_dataset_context(summary)
        self._dataset_loaded = bool(summary)
        if summary:
            self._current_dataset_name = summary.get("dataset_name", "Loaded")
        else:
            self._current_dataset_name = "Idle"
        self._sync_hero_stats()
        self._update_status_indicators()

    def set_variables(self, variables):
        self.variable_combo.blockSignals(True)
        self.variable_combo.clear()
        self.variable_combo.addItems(variables)
        self.variable_combo.blockSignals(False)
        self.forecast_variable_combo.blockSignals(True)
        self.forecast_variable_combo.clear()
        self.forecast_variable_combo.addItems(variables)
        self.forecast_variable_combo.blockSignals(False)
        if variables:
            self.variable_selected.emit(variables[0])
            self._current_variable = variables[0]
            self._sync_hero_stats()
            self._update_status_indicators()

    def set_current_variable(self, variable_name):
        index = self.variable_combo.findText(variable_name)
        if index < 0:
            return
        self.variable_combo.blockSignals(True)
        self.variable_combo.setCurrentIndex(index)
        self.variable_combo.blockSignals(False)
        self._current_variable = variable_name
        self._sync_hero_stats()
        self._update_status_indicators()

    def set_weather_layers(self, layers):
        self.map_panel.set_layers(layers)

    def set_layer_checked(self, category, checked):
        self.map_panel.set_layer_checked(category, checked)

    def set_projection(self, projection_name):
        self.map_panel.set_projection(projection_name)

    def set_time_labels(self, labels):
        self._time_labels = labels
        self.configure_time_slice(len(labels))
        self._set_time_label(0)

    def configure_time_slice(self, size, value=0):
        if not getattr(self, "_time_labels", None) and size:
            self._time_labels = [str(index) for index in range(size)]
        enabled = size > 1
        safe_value = max(0, min(int(value), max(0, size - 1)))
        for control in (self.time_slider, self.time_slice_spin):
            control.blockSignals(True)
            control.setEnabled(enabled)
            control.setMinimum(0)
            control.setMaximum(max(0, size - 1))
            control.setValue(safe_value)
            control.blockSignals(False)
        self._set_time_label(safe_value)

    def current_time_slice(self):
        return self.time_slice_spin.value()

    def set_map_data(self, view_data):
        self.map_panel.render(view_data)

    def set_region_bounds(self, bounds):
        self.map_panel.set_region_bounds(bounds)

    def clear_region_bounds(self):
        self.map_panel.clear_region_bounds()

    def set_metrics(self, metrics):
        self.metrics_panel.set_metrics(metrics)

    def set_grid_rows(self, rows):
        self.data_grid.set_rows(rows)

    def set_slice_statistics(self, statistics):
        self.plot_panel.set_statistics(statistics)

    def set_variable_plot(self, data_array, time_index, comparison_series=None):
        self.plot_panel.plot_variable(data_array, time_index, comparison_series)
        self.analysis_plot_panel.plot_time_series(comparison_series, time_index)

    def set_forecast(self, forecast):
        self.forecast_panel.set_forecast(forecast)
        self.show_module("forecast")

    def reset_dataset_view(self):
        self.metadata_viewer.clear()
        self.dataset_summary.clear()
        self.satellite_panel.clear()
        self.plot_panel.clear()
        self.analysis_plot_panel.clear()
        self.forecast_panel.clear()
        self.map_panel.clear()
        self.map_panel.clear_region_bounds()
        self.map_panel.set_layers([])
        self.metrics_panel.clear()
        self.data_grid.clear()
        self.variable_combo.blockSignals(True)
        self.variable_combo.clear()
        self.variable_combo.blockSignals(False)
        self.forecast_variable_combo.blockSignals(True)
        self.forecast_variable_combo.clear()
        self.forecast_variable_combo.blockSignals(False)
        self.projection_combo.setCurrentText("Auto")
        self.set_time_labels([])
        self.time_label.setText("No dataset time coordinate")
        self._dataset_loaded = False
        self._current_variable = "--"
        self._current_time_text = "--"
        self._update_status_indicators()

    def set_status(self, message):
        self.statusBar().showMessage(message)

    def show_error(self, title, message):
        QMessageBox.critical(self, title, message)

    def show_info(self, title, message):
        QMessageBox.information(self, title, message)

    def _emit_variable_selection(self, variable_name):
        if variable_name:
            self.variable_selected.emit(variable_name)

    def _emit_projection_selection(self, projection_name):
        self.set_projection(projection_name)
        self.projection_selected.emit(projection_name)

    def _emit_forecast_request(self):
        self.run_forecast_requested.emit(
            {
                "variable": self.forecast_variable_combo.currentText(),
                "mode": self.forecast_combo.currentText(),
                "window_size": self.forecast_window_spin.value(),
                "horizon": self.forecast_horizon_spin.value(),
                "future_steps": self.forecast_steps_spin.value(),
            }
        )

    def show_module(self, name):
        if not hasattr(self, "center_stack"):
            return
        mapping = {
            "gis": (self.gis_page, "dashboard"),
            "analysis": (self.analysis_page, "time-series"),
            "forecast": (self.forecast_page, "predictive"),
        }
        page, key = mapping.get(name, mapping["gis"])
        self.center_stack.setCurrentWidget(page)
        self.sidebar.set_active(key)

    def _time_control_changed(self, value):
        sender = self.sender()
        other = self.time_slice_spin if sender is self.time_slider else self.time_slider
        other.blockSignals(True)
        other.setValue(value)
        other.blockSignals(False)
        self._set_time_label(value)
        self.time_slice_changed.emit(value)

    def _set_time_label(self, index):
        labels = getattr(self, "_time_labels", [])
        if labels:
            safe_index = max(0, min(index, len(labels) - 1))
            self._current_time_text = labels[safe_index]
            self.time_label.setText(labels[safe_index])
        else:
            self._current_time_text = "--"
            self.time_label.setText("No dataset time coordinate")
        self._sync_hero_stats()
        self._update_status_indicators()
