import math
import random

from PyQt5.QtCore import QPointF, QRectF, Qt, QTimer
from PyQt5.QtGui import (
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPalette,
    QPen,
    QPixmap,
    QRadialGradient,
)
from PyQt5.QtWidgets import (
    QGraphicsDropShadowEffect,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QSlider,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QSizePolicy,
)


C = {
    "bg": "#0B1220",
    "surface": "#111827",
    "panel": "#121C2E",
    "card": "#1A2333",
    "card_soft": "rgba(26,35,51,220)",
    "border": "#263446",
    "border_strong": "#33465D",
    "soft_border": "#263446",
    "blue": "#4F8EF7",
    "cyan": "#22D3EE",
    "green": "#22C55E",
    "amber": "#F59E0B",
    "red": "#EF4444",
    "txt": "#F8FAFC",
    "dim": "#94A3B8",
    "txt_secondary": "#94A3B8",
    "muted": "#64748B",
    "glow": "#17365F",
    "accent_glow": "#17365F",
    "mid": "#111827",
    "surface_mid": "#121C2E",
}


STYLE = f"""
QWidget, QMainWindow {{
    background: {C['bg']};
    color: {C['txt']};
    font-family: "Segoe UI";
    font-size: 12px;
}}

QMenuBar {{
    background: #0B1220;
    color: {C['txt']};
    font-family: "Segoe UI";
    font-size: 11px;
    padding: 3px 8px;
    border-bottom: 1px solid {C['border']};
}}

QMenuBar::item {{
    padding: 5px 9px;
    border-radius: 6px;
}}

QMenuBar::item:selected,
QMenu::item:selected {{
    background: #1A2333;
}}

QMenu {{
    background: {C['surface']};
    color: {C['txt']};
    border: 1px solid {C['border']};
    border-radius: 8px;
    padding: 4px;
}}

QPushButton,
QComboBox,
QSpinBox {{
    background: {C['card']};
    border: 1px solid {C['border']};
    border-radius: 8px;
    color: {C['txt']};
    font-family: "Segoe UI";
    font-size: 11px;
    padding: 6px 10px;
}}

QPushButton[active="true"] {{
    background: #1B2A44;
    border-color: {C['border_strong']};
    color: {C['txt']};
}}

QPushButton:hover,
QComboBox:hover,
QSpinBox:hover {{
    border-color: {C['blue']};
    background: {C['panel']};
}}

QPushButton:pressed {{
    background: #172235;
    color: {C['txt']};
}}

QComboBox::drop-down {{
    border: none;
    width: 22px;
}}

QComboBox QAbstractItemView {{
    background: {C['surface']};
    color: {C['txt']};
    selection-background-color: {C['blue']};
    selection-color: #FFFFFF;
    border: 1px solid {C['border']};
}}

QTableWidget {{
    background: {C['surface']};
    border: 1px solid {C['border']};
    border-radius: 8px;
    color: {C['txt']};
    alternate-background-color: #0F1728;
    selection-background-color: rgba(79,142,247,0.30);
    selection-color: #FFFFFF;
    gridline-color: #263446;
    font-family: "Segoe UI";
    font-size: 10px;
}}

QTableWidget::item {{
    color: {C['txt']};
    padding: 4px 5px;
}}

QTableWidget::item:selected {{
    background: rgba(79,142,247,0.24);
}}

QHeaderView::section {{
    background: #1A2333;
    color: {C['txt']};
    border: none;
    border-right: 1px solid {C['border']};
    border-bottom: 1px solid {C['border']};
    padding: 6px 5px;
    font-family: "Segoe UI";
    font-size: 9px;
    font-weight: 600;
}}

QSlider::groove:horizontal {{
    height: 5px;
    background: rgba(255,255,255,0.08);
    border-radius: 3px;
}}

QSlider::sub-page:horizontal {{
    height: 5px;
    background: qlineargradient(
        x1:0,
        y1:0,
        x2:1,
        y2:0,
        stop:0 {C['blue']},
        stop:1 {C['cyan']}
    );
    border-radius: 3px;
}}

QSlider::handle:horizontal {{
    width: 16px;
    height: 16px;
    background: qradialgradient(
        cx:0.4,
        cy:0.4,
        radius:0.8,
        fx:0.4,
        fy:0.4,
        stop:0 #FFFFFF,
        stop:1 {C['blue']}
    );
    margin: -5px 0;
    border-radius: 8px;
    border: 2px solid rgba(255,255,255,0.30);
}}

QSlider::handle:horizontal:hover {{
    border-color: {C['cyan']};
}}

QStatusBar {{
    background: #0B1220;
    color: {C['dim']};
    border-top: 1px solid {C['border']};
}}

QLabel {{
    color: {C['txt']};
    background: transparent;
    border: none;
}}

QTabWidget::pane {{
    border: 1px solid {C['border']};
    background: {C['panel']};
    border-radius: 10px;
}}

QTabBar::tab {{
    background: #111A2B;
    color: {C['dim']};
    padding: 6px 10px;
    margin-right: 2px;
    border: 1px solid {C['border']};
    border-bottom: none;
    border-top-left-radius: 7px;
    border-top-right-radius: 7px;
}}

QTabBar::tab:selected {{
    background: {C['card']};
    color: {C['txt']};
}}

QScrollBar:vertical {{
    background: transparent;
    width: 7px;
    margin: 4px 2px 4px 0;
}}

QScrollBar::handle:vertical {{
    background: #33465D;
    min-height: 22px;
    border-radius: 3px;
}}

QScrollBar::handle:vertical:hover {{
    background: {C['blue']};
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {{
    background: transparent;
}}
"""


def qc(value):
    return QColor(value)


def font(size, bold=False, family="Segoe UI"):
    weight = QFont.Bold if bold else QFont.Normal
    item = QFont(family, size, weight)
    item.setStyleStrategy(QFont.PreferAntialias)
    return item


def mono_font(size, bold=False):
    return font(size, bold, "Cascadia Mono")


def pen(color, width=1):
    line_pen = QPen(qc(color) if isinstance(color, str) else color, width)
    line_pen.setCapStyle(Qt.RoundCap)
    return line_pen


def label(text, size=9, color=C["txt"], bold=False):
    item = QLabel(text)
    item.setFont(font(size, bold))
    item.setStyleSheet(f"QLabel{{color:{color};background:transparent;border:none;}}")
    return item


def apply_palette(app):
    palette = app.palette()
    palette.setColor(QPalette.Window, qc(C["bg"]))
    palette.setColor(QPalette.WindowText, qc(C["txt"]))
    app.setPalette(palette)


def card_style(object_name="panelCard", radius=6):
    return f"""
    QFrame#{object_name}{{
        background:rgba(26,35,51,210);
        border:1px solid {C['border']};
        border-radius:{radius}px;
    }}
    """


def add_shadow(widget, blur=32, y=8, color=QColor(0, 0, 0, 110)):
    effect = QGraphicsDropShadowEffect(widget)
    effect.setBlurRadius(blur)
    effect.setOffset(0, y)
    effect.setColor(color)
    widget.setGraphicsEffect(effect)


class Globe(QWidget):
    """Procedural weather globe used as a lightweight stand-in for Cartopy."""

    def __init__(self):
        super().__init__()
        self.setMinimumSize(640, 430)
        self.rotation = 0.0
        self.stream_offset = 0.0
        self.texture = self._build_texture(900)
        self.streams = self._make_streams(90)

        timer = QTimer(self)
        timer.timeout.connect(self._tick)
        timer.start(32)

    def _tick(self):
        self.rotation = (self.rotation + 0.22) % 360
        self.stream_offset += 0.025
        self.update()

    def _build_texture(self, size):
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        p = QPainter(pixmap)
        p.setRenderHint(QPainter.Antialiasing)
        rng = random.Random(13)

        center = QPointF(size / 2, size / 2)
        radius = size * 0.48

        ocean = QRadialGradient(size * 0.42, size * 0.34, radius * 1.2)
        ocean.setColorAt(0.0, QColor("#1C6FA6"))
        ocean.setColorAt(0.38, QColor("#0E4067"))
        ocean.setColorAt(1.0, QColor("#07111F"))
        p.setBrush(ocean)
        p.setPen(Qt.NoPen)
        p.drawEllipse(center, radius, radius)

        p.setPen(pen(QColor(255, 255, 255, 14), 1))
        for factor in [0.2, 0.4, 0.6, 0.8]:
            p.drawEllipse(center, radius * factor, radius * factor)
        p.drawLine(QPointF(size * 0.5, size * 0.06), QPointF(size * 0.5, size * 0.94))
        p.drawLine(QPointF(size * 0.06, size * 0.5), QPointF(size * 0.94, size * 0.5))

        continents = [
            [(0.18, 0.44), (0.24, 0.28), (0.37, 0.19), (0.48, 0.26), (0.43, 0.42), (0.32, 0.53)],
            [(0.36, 0.56), (0.45, 0.63), (0.42, 0.84), (0.31, 0.76), (0.26, 0.62)],
            [(0.54, 0.31), (0.70, 0.24), (0.84, 0.34), (0.78, 0.52), (0.61, 0.52)],
            [(0.57, 0.53), (0.72, 0.56), (0.79, 0.78), (0.65, 0.90), (0.55, 0.72)],
            [(0.76, 0.70), (0.88, 0.72), (0.91, 0.84), (0.78, 0.89)],
            [(0.42, 0.13), (0.52, 0.12), (0.58, 0.18), (0.47, 0.21)],
        ]

        for shape in continents:
            path = QPainterPath()
            for index, (x, y) in enumerate(shape):
                point = QPointF(x * size, y * size)
                path.moveTo(point) if index == 0 else path.lineTo(point)
            path.closeSubpath()
            land = QLinearGradient(0, 0, size, size)
            land.setColorAt(0, QColor("#2DD4BF"))
            land.setColorAt(0.48, QColor("#86EFAC"))
            land.setColorAt(1, QColor("#F59E0B"))
            p.setBrush(land)
            p.setPen(pen(QColor(8, 25, 35, 160), 1))
            p.drawPath(path)

        for _ in range(220):
            x = rng.uniform(size * 0.1, size * 0.9)
            y = rng.uniform(size * 0.08, size * 0.9)
            if (x - center.x()) ** 2 + (y - center.y()) ** 2 < (radius * 0.96) ** 2:
                cloud = QColor(235, 250, 255, rng.randint(35, 85))
                p.setPen(pen(cloud, rng.uniform(0.7, 2.0)))
                p.drawLine(QPointF(x, y), QPointF(x + rng.uniform(12, 45), y + rng.uniform(-5, 5)))

        ice = QRadialGradient(size * 0.5, size * 0.12, radius * 0.38)
        ice.setColorAt(0, QColor(255, 255, 255, 235))
        ice.setColorAt(0.8, QColor(225, 245, 255, 90))
        ice.setColorAt(1, QColor(0, 0, 0, 0))
        p.setBrush(ice)
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(size * 0.5, size * 0.14), radius * 0.34, radius * 0.13)

        p.end()
        return pixmap

    def _make_streams(self, count):
        rng = random.Random(23)
        streams = []
        for _ in range(count):
            angle = rng.uniform(0, math.tau)
            distance = rng.uniform(0.1, 0.88)
            length = rng.uniform(0.18, 0.55)
            curves = []
            for step in range(18):
                offset = (step / 17) * length
                theta = angle + offset
                wave = math.sin(step * 0.7 + angle) * 0.035
                curves.append((theta, max(0.03, min(0.92, distance + wave))))
            streams.append(curves)
        return streams

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        width, height = self.width(), self.height()

        bg = QLinearGradient(0, 0, width, height)
        bg.setColorAt(0, QColor("#0B1220"))
        bg.setColorAt(0.6, QColor("#11243A"))
        bg.setColorAt(1, QColor("#08111D"))
        p.fillRect(self.rect(), bg)

        cx = width * 0.49
        cy = height * 0.49
        radius = min(width * 0.36, height * 0.54)

        glow = QRadialGradient(cx, cy, radius * 1.28)
        glow.setColorAt(0.56, QColor(79, 142, 247, 72))
        glow.setColorAt(0.78, QColor(34, 211, 238, 42))
        glow.setColorAt(1, QColor(0, 0, 0, 0))
        p.setPen(Qt.NoPen)
        p.setBrush(glow)
        p.drawEllipse(QPointF(cx, cy), radius * 1.28, radius * 1.28)

        clip = QPainterPath()
        clip.addEllipse(QPointF(cx, cy), radius, radius)
        p.setClipPath(clip)

        p.save()
        p.translate(cx, cy)
        p.rotate(self.rotation)
        target = QRectF(-radius, -radius, radius * 2, radius * 2)
        p.drawPixmap(target, self.texture, QRectF(0, 0, self.texture.width(), self.texture.height()))
        p.restore()

        p.setPen(pen(QColor(34, 211, 238, 150), 1.2))
        for stream in self.streams:
            path = QPainterPath()
            for index, (theta, distance) in enumerate(stream):
                theta += self.stream_offset
                x = cx + math.cos(theta) * distance * radius
                y = cy + math.sin(theta) * distance * radius * 0.55
                path.moveTo(x, y) if index == 0 else path.lineTo(x, y)
            p.drawPath(path)

        p.setClipping(False)
        shade = QRadialGradient(cx - radius * 0.25, cy - radius * 0.35, radius * 1.35)
        shade.setColorAt(0.22, QColor(255, 255, 255, 24))
        shade.setColorAt(0.72, QColor(0, 0, 0, 0))
        shade.setColorAt(1, QColor(0, 0, 0, 150))
        p.setBrush(shade)
        p.setPen(pen(QColor(170, 230, 255, 120), 1.4))
        p.drawEllipse(QPointF(cx, cy), radius, radius)

        p.setFont(font(13, True))
        p.setPen(QColor(C["txt"]))
        p.drawText(int(width * 0.15), int(height * 0.28), "3D GIS Globe")

        self._draw_hud(p, cx + radius * 0.18, cy - radius * 0.44)

    def _draw_hud(self, p, x, y):
        rect = QRectF(x, y, 230, 84)
        p.setPen(pen(QColor(255, 255, 255, 28), 1))
        p.setBrush(QColor(14, 20, 31, 220))
        p.drawRoundedRect(rect, 5, 5)
        p.setPen(QColor(C["txt"]))
        p.setFont(font(9, True))
        p.drawText(int(x + 10), int(y + 18), "mini-HUD")
        p.setFont(font(8))
        lines = [
            "Location: London (51.5074N, 0.1278W)",
            "Altitude: 15m",
            "Temp: 14C",
            "Humidity: 78%",
        ]
        for index, text in enumerate(lines):
            p.drawText(int(x + 10), int(y + 35 + index * 12), text)


class Sidebar(QWidget):
    """Clean navigation rail for the main application modules."""

    def __init__(self):
        super().__init__()

        self.setFixedWidth(180)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        self.setStyleSheet(
            f"""
            QWidget {{
                background: #0D1524;
                border-right: 1px solid {C['border']};
            }}
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 18, 14, 16)
        layout.setSpacing(8)

        self.buttons = {}

        # ---------------------------------------------------------
        # BRAND / APPLICATION HEADER
        # ---------------------------------------------------------
        brand = QFrame()
        brand.setStyleSheet(
            """
            QFrame {
                background: transparent;
                border: none;
            }
            """
        )

        brand_layout = QVBoxLayout(brand)
        brand_layout.setContentsMargins(6, 4, 6, 14)
        brand_layout.setSpacing(2)

        brand_title = QLabel("WEATHER")
        brand_title.setFont(font(14, True))
        brand_title.setStyleSheet(
            f"""
            QLabel {{
                color: {C['cyan']};
                background: transparent;
                border: none;
                letter-spacing: 1.5px;
            }}
            """
        )

        brand_subtitle = QLabel("ANALYTICS PLATFORM")
        brand_subtitle.setFont(font(8, True))
        brand_subtitle.setStyleSheet(
            f"""
            QLabel {{
                color: {C['dim']};
                background: transparent;
                border: none;
                letter-spacing: 0.8px;
            }}
            """
        )

        brand_layout.addWidget(brand_title)
        brand_layout.addWidget(brand_subtitle)

        layout.addWidget(brand)

        # ---------------------------------------------------------
        # NAVIGATION
        # ---------------------------------------------------------
        items = [
            ("⌂", "Dashboard", "dashboard"),
            ("◫", "Time-Series Analysis", "time-series"),
            ("◈", "Predictive Modeling", "predictive"),
            ("⇧", "Export", "export"),
        ]

        for index, (icon, title, key) in enumerate(items):
            button = QPushButton()

            button.setCursor(Qt.PointingHandCursor)
            button.setCheckable(False)
            button.setFixedHeight(52)
            button.setProperty("navKey", key)
            button.setProperty("active", index == 0)

            button.setStyleSheet(
                f"""
                QPushButton {{
                    background: transparent;
                    color: {C['dim']};
                    border: 1px solid transparent;
                    border-radius: 10px;
                    text-align: left;
                    padding: 0 12px;
                    font-family: "Segoe UI";
                    font-size: 12px;
                    font-weight: 600;
                }}

                QPushButton:hover {{
                    background: #162238;
                    color: {C['txt']};
                    border-color: {C['border']};
                }}

                QPushButton[active="true"] {{
                    background: #172A47;
                    color: {C['txt']};
                    border: 1px solid #31527C;
                }}
                """
            )

            # Create a proper horizontal layout inside the button
            button_layout = QHBoxLayout(button)
            button_layout.setContentsMargins(0, 0, 0, 0)
            button_layout.setSpacing(12)

            icon_label = QLabel(icon)
            icon_label.setFixedWidth(22)
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setFont(font(16, True))
            icon_label.setStyleSheet(
                "QLabel { background: transparent; border: none; color: #22D3EE; }"
            )

            text_label = QLabel(title)
            text_label.setFont(font(11, True))
            text_label.setStyleSheet(
                f"""
                QLabel {{
                    background: transparent;
                    border: none;
                    color: {C['txt']};
                }}
                """
            )

            button_layout.addWidget(icon_label)
            button_layout.addWidget(text_label)
            button_layout.addStretch()

            self.buttons[key] = button
            layout.addWidget(button)

        layout.addStretch(1)

        # ---------------------------------------------------------
        # SETTINGS
        # ---------------------------------------------------------
        settings = QPushButton()

        settings.setCursor(Qt.PointingHandCursor)
        settings.setFixedHeight(50)
        settings.setProperty("active", False)

        settings.setStyleSheet(
            f"""
            QPushButton {{
                background: transparent;
                color: {C['dim']};
                border: 1px solid transparent;
                border-radius: 10px;
                text-align: left;
                padding: 0 12px;
                font-family: "Segoe UI";
                font-size: 12px;
                font-weight: 600;
            }}

            QPushButton:hover {{
                background: #162238;
                color: {C['txt']};
                border-color: {C['border']};
            }}
            """
        )

        settings_layout = QHBoxLayout(settings)
        settings_layout.setContentsMargins(0, 0, 0, 0)
        settings_layout.setSpacing(12)

        settings_icon = QLabel("⚙")
        settings_icon.setFixedWidth(22)
        settings_icon.setAlignment(Qt.AlignCenter)
        settings_icon.setFont(font(15))
        settings_icon.setStyleSheet(
            "QLabel { background: transparent; border: none; color: #94A3B8; }"
        )

        settings_text = QLabel("Settings")
        settings_text.setFont(font(11, True))
        settings_text.setStyleSheet(
            f"QLabel {{ background: transparent; border: none; color: {C['dim']}; }}"
        )

        settings_layout.addWidget(settings_icon)
        settings_layout.addWidget(settings_text)
        settings_layout.addStretch()

        self.buttons["settings"] = settings
        layout.addWidget(settings)

    def set_active(self, key):
        """Update the highlighted navigation item."""

        for name, button in self.buttons.items():
            active = name == key

            button.setProperty("active", active)

            # Force Qt to re-evaluate the dynamic stylesheet property.
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()


class Donut(QWidget):
    def __init__(self, value, title, color):
        super().__init__()
        self.value = value
        self.title = title
        self.color = color
        self.setFixedSize(76, 82)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        cx, cy, radius = self.width() // 2, 34, 29
        p.setPen(pen(QColor(255, 255, 255, 24), 6))
        p.drawArc(cx - radius, cy - radius, radius * 2, radius * 2, 210 * 16, -300 * 16)
        try:
            pct = float(str(self.value).replace("%", "").replace("km", "")) / 100
        except ValueError:
            pct = 0.5
        p.setPen(pen(self.color, 6))
        p.drawArc(cx - radius, cy - radius, radius * 2, radius * 2, 210 * 16, int(-300 * 16 * min(pct, 1)))
        p.setPen(QColor(C["txt"]))
        p.setFont(mono_font(12, True))
        p.drawText(0, 0, self.width(), 62, Qt.AlignCenter, str(self.value))
        p.setFont(font(8))
        p.setPen(QColor(C["dim"]))
        p.drawText(0, 61, self.width(), 18, Qt.AlignCenter, self.title)


class MiniChart(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(120)
        rng = random.Random(3)
        self.temp = [18 - i * 0.08 + math.sin(i / 2.3) * 4 + rng.uniform(-1, 1) for i in range(48)]
        self.dew = [10 + math.sin(i / 3.4) * 4 + rng.uniform(-1.2, 1.2) for i in range(48)]

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        left, right, top, bottom = 38, 12, 22, 26
        pw, ph = w - left - right, h - top - bottom
        vals = self.temp + self.dew
        mn, mx = min(vals) - 2, max(vals) + 3

        p.fillRect(self.rect(), QColor(16, 23, 34))
        p.setPen(pen(QColor(255, 255, 255, 22)))
        for i in range(4):
            y = top + i * ph / 3
            p.drawLine(left, int(y), w - right, int(y))
        p.setFont(font(8))
        p.setPen(QColor(C["dim"]))
        for x, text in [(left, "0h"), (left + pw * 0.25, "6h"), (left + pw * 0.5, "12h"), (left + pw * 0.75, "18h"), (left + pw - 12, "24h")]:
            p.drawText(int(x), h - 5, text)
        p.drawText(6, top + 5, "30")
        p.drawText(12, top + ph - 2, "0")

        def xy(i, value):
            return left + i * pw / (len(self.temp) - 1), top + ph - ((value - mn) / (mx - mn)) * ph

        for values, color in [(self.temp, QColor(C["red"])), (self.dew, QColor(C["blue"]))]:
            path = QPainterPath()
            fill = QPainterPath()
            for i, value in enumerate(values):
                x, y = xy(i, value)
                path.moveTo(x, y) if i == 0 else path.lineTo(x, y)
            fill = QPainterPath(path)
            fill.lineTo(xy(len(values) - 1, min(values) - 4)[0], top + ph)
            fill.lineTo(xy(0, min(values) - 4)[0], top + ph)
            fill.closeSubpath()
            grad = QLinearGradient(0, top, 0, top + ph)
            grad.setColorAt(0, QColor(color.red(), color.green(), color.blue(), 85))
            grad.setColorAt(1, QColor(color.red(), color.green(), color.blue(), 0))
            p.setBrush(grad)
            p.setPen(Qt.NoPen)
            p.drawPath(fill)
            p.setPen(pen(color, 1.8))
            p.setBrush(Qt.NoBrush)
            p.drawPath(path)

        p.setFont(font(8))
        p.setPen(QColor(C["red"]))
        p.drawText(int(w * 0.29), 14, "Temp")
        p.setPen(QColor(C["blue"]))
        p.drawText(int(w * 0.57), 14, "Dew")


class Sat(QWidget):
    def __init__(self, seed, large=False):
        super().__init__()
        self.seed = seed
        self.large = large
        self.setMinimumSize(86 if not large else 170, 52 if not large else 112)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        rng = random.Random(self.seed)
        g = QLinearGradient(0, 0, w, h)
        if self.seed == 40:
            g.setColorAt(0, QColor("#14362A"))
            g.setColorAt(1, QColor("#0B1C15"))
        else:
            g.setColorAt(0, QColor("#51606C"))
            g.setColorAt(1, QColor("#1B232B"))
        p.fillRect(self.rect(), g)
        p.setPen(pen(QColor(235, 240, 240, 68), 1.2))
        for _ in range(42 if self.large else 18):
            x = rng.randint(0, w)
            y = rng.randint(0, h)
            p.drawArc(x - rng.randint(12, 44), y - rng.randint(12, 44), rng.randint(28, 80), rng.randint(20, 65), rng.randint(0, 360) * 16, rng.randint(30, 120) * 16)
        overlay = QRadialGradient(w * 0.18, h * 0.2, max(w, h) * 1.2)
        overlay.setColorAt(0, QColor(255, 255, 255, 26))
        overlay.setColorAt(0.7, QColor(255, 255, 255, 0))
        p.setBrush(overlay)
        p.setPen(Qt.NoPen)
        p.drawRect(self.rect())
        p.setPen(pen(QColor(255, 255, 255, 56), 1))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(0, 0, w - 1, h - 1, 8, 8)


class SectionCard(QFrame):
    """Compact reusable section container."""

    def __init__(self, title):
        super().__init__()

        self.setObjectName("sectionCard")

        self.setStyleSheet(
            f"""
            QFrame#sectionCard {{
                background: #111B2B;
                border: 1px solid {C['border']};
                border-radius: 10px;
            }}
            """
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            11,
            9,
            11,
            9,
        )

        layout.setSpacing(6)

        title_row = QHBoxLayout()
        title_row.setSpacing(6)

        title_row.addWidget(
            label(
                title,
                10,
                C["txt"],
                True,
            )
        )

        title_row.addStretch()

        status = label(
            "●",
            8,
            C["cyan"],
            True,
        )

        title_row.addWidget(
            status
        )

        layout.addLayout(
            title_row
        )

        self.body = layout


class RightPanel(QWidget):
    """
    Compact insights rail.

    Kept as a reusable visualization-side panel.
    The main dashboard may provide its own right rail.
    """

    def __init__(
        self,
        summary_panel=None,
        plot_panel=None,
        controls_widget=None,
    ):
        super().__init__()

        self.setMinimumWidth(330)
        self.setMaximumWidth(390)

        self.setSizePolicy(
            QSizePolicy.Preferred,
            QSizePolicy.Expanding,
        )

        self.setStyleSheet(
            f"""
            QWidget {{
                background: #0D1524;
                border-left: 1px solid {C['border']};
            }}
            """
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            10,
            10,
            10,
            10,
        )

        layout.setSpacing(8)

        # ---------------------------------------------------------
        # HEADER
        # ---------------------------------------------------------

        header = SectionCard(
            "Live Widgets"
        )

        header.body.addWidget(
            label(
                "Weather intelligence, telemetry, and forecast surfaces.",
                9,
                C["dim"],
            )
        )

        layout.addWidget(
            header
        )

        # ---------------------------------------------------------
        # ATMOSPHERIC BREAKDOWN
        # ---------------------------------------------------------

        breakdown = SectionCard(
            "Atmospheric Breakdown"
        )

        row = QHBoxLayout()
        row.setSpacing(4)

        for value, title, color in [
            ("78%", "Humidity", C["blue"]),
            ("3.2", "UV Index", C["amber"]),
            ("10km", "Visibility", C["green"]),
        ]:
            row.addWidget(
                Donut(
                    value,
                    title,
                    color,
                )
            )

        breakdown.body.addLayout(
            row
        )

        layout.addWidget(
            breakdown
        )

        # ---------------------------------------------------------
        # CHART
        # ---------------------------------------------------------

        chart = SectionCard(
            "Multi-Variable Comparison"
        )

        mini_chart = MiniChart()

        mini_chart.setMinimumHeight(
            105
        )

        chart.body.addWidget(
            mini_chart
        )

        layout.addWidget(
            chart
        )

        # ---------------------------------------------------------
        # SATELLITE
        # ---------------------------------------------------------

        sat = SectionCard(
            "Satellite Feed"
        )

        grid = QGridLayout()

        grid.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        grid.setSpacing(5)

        grid.addWidget(
            Sat(10, True),
            0,
            0,
            2,
            1,
        )

        grid.addWidget(
            Sat(30),
            0,
            1,
        )

        grid.addWidget(
            Sat(40),
            1,
            1,
        )

        sat.body.addLayout(
            grid
        )

        layout.addWidget(
            sat
        )

        # ---------------------------------------------------------
        # OPTIONAL PANELS
        # ---------------------------------------------------------

        if controls_widget is not None:

            controls = SectionCard(
                "Dataset Controls"
            )

            controls.body.addWidget(
                controls_widget
            )

            layout.addWidget(
                controls
            )

        if summary_panel is not None:

            summary = SectionCard(
                "Dataset Summary"
            )

            summary.body.addWidget(
                summary_panel
            )

            layout.addWidget(
                summary
            )

        if plot_panel is not None:

            analysis = SectionCard(
                "Variable Analysis"
            )

            analysis.body.addWidget(
                plot_panel
            )

            layout.addWidget(
                analysis,
                1,
            )

        else:
            layout.addStretch(1)


class TelemetryGrid(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(130)
        self.setMaximumHeight(150)
        self.setObjectName("telemetryCard")
        self.setStyleSheet(card_style("telemetryCard", 16))
        add_shadow(self, blur=26, y=7, color=QColor(0, 0, 0, 90))
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)
        title_row = QHBoxLayout()
        title_row.addWidget(label("Data Grid & Telemetry", 12, C["txt"], True))
        title_row.addStretch()
        title_row.addWidget(label("Live", 10, C["green"], True))
        layout.addLayout(title_row)

        self.table = QTableWidget(4, 5)
        self.table.setHorizontalHeaderLabels(["Station ID", "Timestamp", "Barometric Pressure (hPa)", "Wind Speed (m/s)", "Anomalies"])
        header = self.table.horizontalHeader()

        header.setSectionResizeMode(
            0,
            QHeaderView.Fixed,
        )

        header.setSectionResizeMode(
            1,
            QHeaderView.Stretch,
        )

        header.setSectionResizeMode(
            2,
            QHeaderView.Fixed,
        )

        header.setSectionResizeMode(
            3,
            QHeaderView.Fixed,
        )

        header.setSectionResizeMode(
            4,
            QHeaderView.Fixed,
        )

        self.table.setColumnWidth(0, 65)
        self.table.setColumnWidth(2, 105)
        self.table.setColumnWidth(3, 82)
        self.table.setColumnWidth(4, 70)

        self.table.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.table.setWordWrap(False)
        self.table.verticalHeader().hide()
        self.table.setShowGrid(True)
        self.table.setAlternatingRowColors(True)
        rows = [
            ["00000", "2023-02-31 15:36:37.969", "213.50", "1.8", "OK"],
            ["00000", "2023-02-31 15:36:33.891", "213.50", "1.6", "OK"],
            ["00000", "2023-02-31 15:36:33.576", "213.50", "1.4", "OK"],
            ["00000", "2023-02-31 15:36:37.960", "213.50", "1.2", "OK"],
        ]
        for row, values in enumerate(rows):
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                if col == 4:
                    item.setForeground(QColor(C["green"]))
                self.table.setItem(row, col, item)
        layout.addWidget(self.table)

        timer = QTimer(self)
        timer.timeout.connect(self._update_wind)
        timer.start(1000)

    def _update_wind(self):
        row = random.randint(0, 3)
        self.table.item(row, 3).setText(f"{random.uniform(1.0, 2.2):.1f}")


class LayerButtons(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background:rgba(17,24,39,190);border:1px solid {C['border']};border-radius:14px;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)
        for text, color in [("WND", C["cyan"]), ("CLK", C["blue"]), ("TMP", C["red"]), ("HUM", C["green"]), ("RAD", C["amber"]), ("H2O", C["cyan"])]:
            button = QPushButton(text)
            button.setFixedSize(42, 36)
            button.setStyleSheet(
                f"QPushButton{{background:#131B29;border:1px solid {C['border']};border-radius:10px;color:{color};font-size:9px;font-weight:bold;}}"
                f"QPushButton:hover{{border-color:{C['blue']};background:#1A2740;}}"
            )
            layout.addWidget(button)


class GlobePanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("globePanel")
        self.setStyleSheet(card_style("globePanel", 18))
        add_shadow(self, blur=34, y=10, color=QColor(0, 0, 0, 110))
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(12)

        header = QHBoxLayout()
        header.addWidget(label("Atmospheric Globe", 14, C["txt"], True))
        header.addStretch()
        header.addWidget(label("LIVE", 10, C["green"], True))
        root.addLayout(header)

        self.globe = Globe()
        globe_wrap = QWidget()
        globe_wrap.setMinimumHeight(500)
        globe_wrap.setStyleSheet(f"background:rgba(255,255,255,0.02);border:1px solid {C['border']};border-radius:16px;")
        globe_layout = QGridLayout(globe_wrap)
        globe_layout.setContentsMargins(0, 0, 0, 0)
        globe_layout.addWidget(self.globe, 0, 0)
        globe_layout.addWidget(LayerButtons(), 0, 0, Qt.AlignHCenter | Qt.AlignBottom)

        root.addWidget(globe_wrap, 1)
        root.addWidget(self._time_slider())

    def _time_slider(self):
        wrapper = QWidget()
        wrapper.setStyleSheet(f"background:rgba(17,24,39,200);border:1px solid {C['border']};border-radius:14px;")
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(8)
        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 72)
        slider.setValue(32)
        layout.addWidget(slider)
        ticks = QHBoxLayout()
        for text in ["0h", "-12h", "-32h", "-45h", "-72h"]:
            ticks.addWidget(label(text, 8, C["dim"]))
            if text != "-72h":
                ticks.addStretch()
        layout.addLayout(ticks)
        return wrapper


class CenterDashboard(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        layout.addWidget(GlobePanel(), 1)
        layout.addWidget(TelemetryGrid())
