from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QHeaderView,
)

from src.visualization.widgets.dashboard_visuals import C


class MetricsPanel(QWidget):
    """Dataset-derived live metric summary for the selected time slice."""

    def __init__(self):
        super().__init__()

        self.cards = {}

        # =========================================================
        # TABLE
        # =========================================================
        self.table = QTableWidget(0, 5)

        self.setMinimumHeight(205)

        self.table.setMaximumHeight(92)

        self.table.setHorizontalHeaderLabels(
            ["Metric", "Mean", "Units", "Min", "Max"]
        )

        self.table.setFont(
            QFont("Segoe UI", 8)
        )

        self.table.horizontalHeader().setFont(
            QFont("Segoe UI", 8, QFont.Bold)
        )

        self.table.verticalHeader().hide()

        # ---------------------------------------------------------
        # FIXED TABLE COLUMN SIZING
        # ---------------------------------------------------------
        header = self.table.horizontalHeader()

        header.setStretchLastSection(False)

        header.setSectionResizeMode(
            0,
            QHeaderView.Stretch
        )

        header.setSectionResizeMode(
            1,
            QHeaderView.Fixed
        )

        header.setSectionResizeMode(
            2,
            QHeaderView.Fixed
        )

        header.setSectionResizeMode(
            3,
            QHeaderView.Fixed
        )

        header.setSectionResizeMode(
            4,
            QHeaderView.Fixed
        )

        self.table.setColumnWidth(1, 58)
        self.table.setColumnWidth(2, 52)
        self.table.setColumnWidth(3, 62)
        self.table.setColumnWidth(4, 62)

        # ---------------------------------------------------------
        # TABLE BEHAVIOUR
        # ---------------------------------------------------------
        self.table.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.table.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )

        self.table.setWordWrap(False)

        self.table.verticalHeader().setDefaultSectionSize(
            26
        )

        self.table.setAlternatingRowColors(True)

        # ---------------------------------------------------------
        # TABLE STYLE
        # ---------------------------------------------------------
        self.table.setStyleSheet(
            """
            QTableWidget {
                color: #F8FAFC;
                alternate-background-color: #121C2E;
                background: #111827;
                gridline-color: #263446;
                border: 1px solid #263446;
                border-radius: 9px;
            }

            QTableWidget::item {
                color: #D8E7F2;
                padding: 4px 5px;
                border: none;
            }

            QTableWidget::item:selected {
                background: #17365F;
                color: #FFFFFF;
            }

            QHeaderView::section {
                background: #1A2333;
                color: #F8FAFC;
                border: none;
                border-bottom: 1px solid #263446;
                padding: 5px 4px;
                font-size: 8px;
                font-weight: 600;
            }

            QScrollBar:vertical {
                background: transparent;
                width: 6px;
                margin: 2px;
            }

            QScrollBar::handle:vertical {
                background: #33465D;
                min-height: 20px;
                border-radius: 3px;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
            }
            """
        )

        # =========================================================
        # MAIN LAYOUT
        # =========================================================
        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        layout.setSpacing(7)

        # =========================================================
        # METRIC CARDS
        # =========================================================
        self.card_grid = QGridLayout()

        self.card_grid.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.card_grid.setSpacing(7)

        layout.addLayout(
            self.card_grid
        )

        # =========================================================
        # TABLE
        # =========================================================
        layout.addWidget(
            self.table
        )

        self._build_cards()

    # =============================================================
    # UPDATE METRICS
    # =============================================================

    def set_metrics(self, metrics):

        by_label = {
            metric.get("label", ""): metric
            for metric in metrics
        }

        # ---------------------------------------------------------
        # UPDATE CARDS
        # ---------------------------------------------------------
        for label, card in self.cards.items():

            metric = by_label.get(
                label,
                {}
            )

            value = metric.get(
                "value",
                "N/A"
            )

            units = metric.get(
                "units",
                ""
            )

            card["value"].setText(
                f"{value} {units}".strip()
            )

            card["range"].setText(
                (
                    f"{metric.get('min', 'N/A')} "
                    f"to "
                    f"{metric.get('max', 'N/A')}"
                )
                if metric
                else "No dataset variable"
            )

        # ---------------------------------------------------------
        # UPDATE TABLE
        # ---------------------------------------------------------
        self.table.setRowCount(
            len(metrics)
        )

        for row, metric in enumerate(metrics):

            values = [
                metric.get(
                    "label",
                    ""
                ),

                metric.get(
                    "value",
                    ""
                ),

                metric.get(
                    "units",
                    ""
                ),

                metric.get(
                    "min",
                    ""
                ),

                metric.get(
                    "max",
                    ""
                ),
            ]

            for col, value in enumerate(values):

                item = QTableWidgetItem(
                    str(value)
                )

                item.setForeground(
                    QColor("#D8E7F2")
                )

                self.table.setItem(
                    row,
                    col,
                    item
                )

    # =============================================================
    # CLEAR
    # =============================================================

    def clear(self):

        self.table.setRowCount(
            0
        )

        for card in self.cards.values():

            card["value"].setText(
                "N/A"
            )

            card["range"].setText(
                "No dataset variable"
            )

    # =============================================================
    # BUILD CARDS
    # =============================================================

    def _build_cards(self):

        labels = [
            "Humidity",
            "Pressure",
            "Wind Speed",
            "Precipitation",
        ]

        for index, label in enumerate(labels):

            card = QFrame()

            card.setMinimumHeight(
                68
            )

            card.setMaximumHeight(
                76
            )

            card.setStyleSheet(
                f"""
                QFrame {{
                    background: #1A2333;
                    border: 1px solid {C['border']};
                    border-radius: 11px;
                }}

                QLabel {{
                    background: transparent;
                    border: none;
                }}
                """
            )

            # -----------------------------------------------------
            # CARD LAYOUT
            # -----------------------------------------------------

            card_layout = QVBoxLayout(
                card
            )

            card_layout.setContentsMargins(
                9,
                5,
                9,
                5
            )

            card_layout.setSpacing(
                1
            )

            # -----------------------------------------------------
            # TITLE
            # -----------------------------------------------------

            title = QLabel(
                label
            )

            title.setFont(
                QFont(
                    "Segoe UI",
                    8,
                    QFont.Bold
                )
            )

            title.setStyleSheet(
                f"color: {C['dim']};"
            )

            # -----------------------------------------------------
            # VALUE
            # -----------------------------------------------------

            value = QLabel(
                "N/A"
            )

            value.setAlignment(
                Qt.AlignCenter
            )

            value.setFont(
                QFont(
                    "Segoe UI",
                    12,
                    QFont.Bold
                )
            )

            value.setStyleSheet(
                "color: #F0F6FF;"
            )

            value.setMinimumHeight(
                28
            )

            # -----------------------------------------------------
            # RANGE
            # -----------------------------------------------------

            range_label = QLabel(
                "No dataset variable"
            )

            range_label.setAlignment(
                Qt.AlignCenter
            )

            range_label.setFont(
                QFont(
                    "Segoe UI",
                    7
                )
            )

            range_label.setStyleSheet(
                f"color: {C['muted']};"
            )

            # -----------------------------------------------------
            # ADD TO CARD
            # -----------------------------------------------------

            card_layout.addWidget(
                title
            )

            card_layout.addWidget(
                value
            )

            card_layout.addWidget(
                range_label
            )

            # -----------------------------------------------------
            # GRID POSITION
            # -----------------------------------------------------

            row = index // 2
            column = index % 2

            self.card_grid.addWidget(
                card,
                row,
                column
            )

            self.cards[label] = {
                "value": value,
                "range": range_label,
            }