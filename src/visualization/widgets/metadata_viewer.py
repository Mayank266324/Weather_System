from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem


class MetadataViewer(QTreeWidget):
    """Tree view for dimensions, coordinates, variables, and attributes."""

    def __init__(self):
        super().__init__()
        self.setHeaderLabels(["Property", "Value"])
        self.setColumnWidth(0, 190)
        self.setFont(QFont("Segoe UI", 9))
        self.header().setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.setAlternatingRowColors(True)
        self.setStyleSheet(
            """
            QTreeWidget {
                font-family: "Segoe UI";
                font-size: 12px;
                color: #f8fafc;
                background: #111827;
                alternate-background-color: #121c2e;
                border: 1px solid #263446;
                border-radius: 12px;
                padding: 4px;
            }
            QTreeWidget::item {
                min-height: 24px;
                color: #f8fafc;
                padding: 4px 6px;
            }
            QTreeWidget::item:selected {
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

    def set_metadata(self, metadata):
        self.clear()
        for section, content in metadata.items():
            section_item = QTreeWidgetItem([section.title(), ""])
            self.addTopLevelItem(section_item)
            self._add_value(section_item, content)
            section_item.setExpanded(True)
        self.resizeColumnToContents(0)

    def _add_value(self, parent, value):
        if isinstance(value, dict):
            for key, child_value in value.items():
                item = QTreeWidgetItem([str(key), self._preview(child_value)])
                parent.addChild(item)
                if isinstance(child_value, (dict, list, tuple)):
                    self._add_value(item, child_value)
        elif isinstance(value, (list, tuple)):
            for index, child_value in enumerate(value):
                item = QTreeWidgetItem([str(index), self._preview(child_value)])
                parent.addChild(item)
                if isinstance(child_value, (dict, list, tuple)):
                    self._add_value(item, child_value)

    def _preview(self, value):
        if isinstance(value, dict):
            return f"{len(value)} entries"
        if isinstance(value, (list, tuple)):
            return ", ".join(str(item) for item in value[:6])
        return str(value)
