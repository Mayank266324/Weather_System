from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from src.visualization.widgets.dashboard_visuals import C


class SatelliteLayerPanel(QWidget):
    """Future raster/satellite overlay workflow without decorative fake imagery."""

    def __init__(self):
        super().__init__()
        self.description = QLabel(
            "Raster overlay slots are prepared for satellite, radar, and reanalysis imagery. "
            "No image layer is currently loaded."
        )
        self.description.setWordWrap(True)
        self.description.setFont(QFont("Segoe UI", 9))
        self.description.setStyleSheet(f"color:{C['txt']};padding:6px;")

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Layer", "Status", "Expected Grid", "Projection"])
        self.table.setFont(QFont("Segoe UI", 9))
        self.table.horizontalHeader().setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().hide()
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(
            """
            QTableWidget {
                color: #f8fafc;
                alternate-background-color: #121c2e;
                background: #111827;
                gridline-color: #263446;
                border: 1px solid #263446;
                border-radius: 12px;
            }
            QTableWidget::item {
                color: #f8fafc;
                padding: 6px 8px;
            }
            QTableWidget::item:selected {
                background: #17365f;
                color: #ffffff;
            }
            QHeaderView::section {
                background: #1a2333;
                color: #f8fafc;
                border: none;
                border-bottom: 1px solid #263446;
                padding: 7px 6px;
                font-weight: 600;
            }
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.description)
        layout.addWidget(self.table)
        self.set_dataset_context({})

    def set_dataset_context(self, summary):
        dimensions = summary.get("dimensions", {}) if summary else {}
        lat_size = dimensions.get("lat") or dimensions.get("latitude") or dimensions.get("y") or ""
        lon_size = dimensions.get("lon") or dimensions.get("longitude") or dimensions.get("x") or ""
        grid = f"{lat_size} x {lon_size}" if lat_size and lon_size else "pending georeferenced raster"
        rows = [
            ["Satellite cloud mask", "not loaded", grid, "PlateCarree / source CRS"],
            ["Radar precipitation", "not loaded", grid, "PlateCarree / source CRS"],
            ["Raster overlay", "not loaded", grid, "dataset CRS metadata"],
        ]
        self.table.setRowCount(len(rows))
        for row_index, row_values in enumerate(rows):
            for col_index, value in enumerate(row_values):
                item = QTableWidgetItem(str(value))
                item.setForeground(QColor("#d8e7f2"))
                self.table.setItem(row_index, col_index, item)
        self.table.resizeColumnsToContents()

    def clear(self):
        self.set_dataset_context({})
