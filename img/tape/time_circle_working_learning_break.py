import sys
import json
import random
import math
from pathlib import Path
from datetime import datetime, timedelta

import psutil
from PySide6.QtCore import Qt, QTimer, QTime, QPropertyAnimation, QPointF, QRectF
from PySide6.QtGui import QAction, QPainter, QPen, QColor, QPainterPath, QBrush, QFont
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel,
    QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTimeEdit,
    QSystemTrayIcon, QMenu,
    QGraphicsOpacityEffect
)


CONFIG_PATH = Path("settings.json")
FRAGMENTS_PATH = Path("time_fragments.jsonl")


DEFAULT_CONFIG = {
    "sleep_time": "22:00",
    "restricted_apps": ["chrome.exe"],
    "goal": "Finish your MVP"
}


AI_LINES = [
    "Use your attention gently.",
    "You still have time today.",
    "A small pause can protect your focus.",
    "Move slowly. You’re still moving.",
    "Your attention deserves intention.",
    "This moment is still yours.",
]


STATE_STYLES = {
    "Working": {
        "ink": "#5E554B",
        "soft": "#D8C3A5",
        "message": "A working circle begins here."
    },
    "Learning": {
        "ink": "#6B5F7A",
        "soft": "#D7CDE5",
        "message": "Learning leaves gentle traces."
    },
    "Break": {
        "ink": "#7A6E62",
        "soft": "#DCCFBF",
        "message": "Rest is also part of the day."
    },
}


def load_config():
    if CONFIG_PATH.exists():
        try:
            config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            for key, value in DEFAULT_CONFIG.items():
                config.setdefault(key, value)
            return config
        except Exception:
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()


def save_config(config):
    CONFIG_PATH.write_text(
        json.dumps(config, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def save_fragment(fragment):
    FRAGMENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with FRAGMENTS_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(fragment, ensure_ascii=False) + "\n")


def get_running_process_names():
    names = set()
    for p in psutil.process_iter(["name"]):
        try:
            name = p.info["name"]
            if name:
                names.add(name.lower())
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return names


def minutes_until_sleep(sleep_time_str):
    now = datetime.now()
    hour, minute = map(int, sleep_time_str.split(":"))

    sleep_dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    if sleep_dt < now:
        sleep_dt += timedelta(days=1)

    diff = sleep_dt - now
    return max(0, int(diff.total_seconds() // 60))


def format_minutes(minutes_left):
    hours = minutes_left // 60
    minutes = minutes_left % 60
    if hours > 0:
        return f"{hours}h {minutes}m left today"
    return f"{minutes}m left today"


def format_duration(seconds):
    minutes = max(0, int(seconds // 60))
    if minutes < 1:
        return "less than 1 minute"
    hours = minutes // 60
    mins = minutes % 60
    if hours > 0:
        return f"{hours}h {mins}m"
    return f"{mins}m"


class StateButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(34)
        self.setStyleSheet("""
            QPushButton {
                border: 1px solid rgba(120, 98, 72, 55);
                border-radius: 17px;
                background: rgba(255, 250, 242, 170);
                color: #7a6e62;
                font-size: 13px;
                padding: 6px 14px;
            }
            QPushButton:checked {
                background: rgba(216, 195, 165, 180);
                color: #4f463d;
                border: 1px solid rgba(120, 98, 72, 105);
            }
            QPushButton:hover {
                background: rgba(242, 232, 215, 210);
            }
        """)


class TimeCircleCanvas(QWidget):
    """A soft drawing canvas for leaving one open time-circle."""

    def __init__(self, on_circle_started=None, on_circle_left_open=None, on_circle_completed=None):
        super().__init__()
        self.setMinimumSize(420, 360)
        self.setCursor(Qt.CrossCursor)
        self.setMouseTracking(True)

        self.on_circle_started = on_circle_started
        self.on_circle_left_open = on_circle_left_open
        self.on_circle_completed = on_circle_completed

        self.current_state = "Working"
        self.points = []
        self.is_drawing = False
        self.has_open_circle = False
        self.has_completed_circle = False
        self.started_at = None
        self.completed_at = None
        self.gesture_count = 0

        self.hover_pos = QPointF(-1000, -1000)

    def set_state(self, state):
        self.current_state = state
        self.update()

    def reset_circle(self):
        self.points = []
        self.is_drawing = False
        self.has_open_circle = False
        self.has_completed_circle = False
        self.started_at = None
        self.completed_at = None
        self.gesture_count = 0
        self.update()

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            return

        self.is_drawing = True

        if not self.has_open_circle and not self.has_completed_circle:
            self.points = [event.position()]
            self.started_at = datetime.now()
            self.has_open_circle = True
            if self.on_circle_started:
                self.on_circle_started(self.current_state, self.started_at)
        elif self.has_open_circle and not self.has_completed_circle:
            self.points.append(event.position())

        self.update()

    def mouseMoveEvent(self, event):
        self.hover_pos = event.position()
        if self.is_drawing:
            self.points.append(event.position())
        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.LeftButton:
            return

        self.is_drawing = False

        if self.has_open_circle and not self.has_completed_circle and len(self.points) > 6:
            self.gesture_count += 1

            if self.gesture_count == 1:
                if self.on_circle_left_open:
                    self.on_circle_left_open(
                        self.current_state,
                        self.started_at,
                        self.points
                    )
            elif self.started_at and self._drawn_enough_to_complete():
                self.completed_at = datetime.now()
                self.has_completed_circle = True
                if self.on_circle_completed:
                    self.on_circle_completed(
                        self.current_state,
                        self.started_at,
                        self.completed_at,
                        self.points
                    )
        self.update()

    def _drawn_enough_to_complete(self):
        """
        Simple demo-friendly rule:
        The second drawing gesture completes the circle once enough points exist.
        This avoids fragile geometric recognition during a hackathon prototype.
        """
        if not self.started_at:
            return False
        elapsed = (datetime.now() - self.started_at).total_seconds()
        return elapsed >= 1 and self.gesture_count >= 2 and len(self.points) > 40

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        self._paint_background(painter)
        self._paint_user_path(painter)

    def load_open_circle(self, state, started_at, points):
        self.current_state = state
        self.started_at = started_at
        self.points = [QPointF(p) for p in points]
        self.is_drawing = False
        self.has_open_circle = True
        self.has_completed_circle = False
        self.completed_at = None
        self.gesture_count = 1
        self.update()

    def _circle_rect(self):
        size = min(self.width(), self.height()) - 105
        x = (self.width() - size) / 2
        y = (self.height() - size) / 2 + 12
        return QRectF(x, y, size, size)

    def _paint_background(self, painter):
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(255, 252, 246, 210)))
        painter.drawRoundedRect(QRectF(8, 8, self.width() - 16, self.height() - 16), 28, 28)

        # Very subtle paper speckles.
        painter.setPen(QPen(QColor(126, 105, 82, 18), 1))
        for i in range(90):
            x = (i * 47) % max(1, self.width())
            y = (i * 83) % max(1, self.height())
            painter.drawPoint(x, y)

    def _paint_guide_circle(self, painter):
        rect = self._circle_rect()
        style = STATE_STYLES[self.current_state]

        guide_pen = QPen(QColor(style["soft"]), 2)
        guide_pen.setStyle(Qt.DashLine)
        guide_pen.setDashPattern([2, 8])
        guide_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(guide_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(rect)

        # A faint half-arc hint to invite the first gesture.
        if not self.points:
            arc_pen = QPen(QColor(120, 98, 72, 45), 4)
            arc_pen.setCapStyle(Qt.RoundCap)
            painter.setPen(arc_pen)
            painter.drawArc(rect, 35 * 16, 145 * 16)

    def _paint_user_path(self, painter):
        if len(self.points) < 2:
            return

        style = STATE_STYLES[self.current_state]

        # Soft shadow / ink bloom.
        shadow_pen = QPen(QColor(90, 72, 55, 35), 11)
        shadow_pen.setCapStyle(Qt.RoundCap)
        shadow_pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(shadow_pen)
        painter.drawPath(self._make_smooth_path())

        ink = QColor(style["ink"])
        ink.setAlpha(205 if not self.has_completed_circle else 225)
        ink_pen = QPen(ink, 5)
        ink_pen.setCapStyle(Qt.RoundCap)
        ink_pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(ink_pen)
        painter.drawPath(self._make_smooth_path())

        if self.has_completed_circle:
            rect = self._circle_rect()
            complete_pen = QPen(QColor(style["soft"]), 2)
            complete_pen.setCapStyle(Qt.RoundCap)
            painter.setPen(complete_pen)
            painter.drawEllipse(rect.adjusted(7, 7, -7, -7))

    def _make_smooth_path(self):
        path = QPainterPath()
        if not self.points:
            return path

        path.moveTo(self.points[0])
        if len(self.points) == 2:
            path.lineTo(self.points[1])
            return path

        for i in range(1, len(self.points) - 1):
            p1 = self.points[i]
            p2 = self.points[i + 1]
            mid = QPointF((p1.x() + p2.x()) / 2, (p1.y() + p2.y()) / 2)
            path.quadTo(p1, mid)
        path.lineTo(self.points[-1])
        return path

    def _paint_center_text(self, painter):
        painter.setPen(QColor(110, 98, 86, 160))
        painter.setFont(QFont("Segoe UI", 11))

        rect = self._circle_rect()
        center = rect.center()

        if not self.has_open_circle:
            text = "draw a half circle"
        elif self.has_open_circle and not self.has_completed_circle:
            text = "left open"
        else:
            seconds = (self.completed_at - self.started_at).total_seconds()
            text = f"{format_duration(seconds)} passed here"

        painter.drawText(
            QRectF(center.x() - 120, center.y() - 18, 240, 36),
            Qt.AlignCenter,
            text
        )



class FloatingFragment(QWidget):
    """A tiny always-on-top desktop fragment that keeps the drawn time trace visible."""

    def __init__(self, points, state, started_at, on_click=None):
        super().__init__()
        self.points = [QPointF(p) for p in points]
        self.state = state
        self.started_at = started_at
        self.on_click = on_click

        self.setFixedSize(150, 150)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.PointingHandCursor)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)

        self.move_to_bottom_right()

    def move_to_bottom_right(self):
        screen = QApplication.primaryScreen().availableGeometry()
        x = screen.right() - self.width() - 28
        y = screen.bottom() - self.height() - 36
        self.move(x, y)

    def set_points(self, points, state=None, started_at=None):
        self.points = [QPointF(p) for p in points]
        if state:
            self.state = state
        if started_at:
            self.started_at = started_at
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.on_click:
            self.on_click()

    def paintEvent(self, event):
        if len(self.points) < 2:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 250, 242, 190))
        painter.drawRoundedRect(QRectF(10, 10, self.width() - 20, self.height() - 20), 34, 34)

        path = self._scaled_path()
        style = STATE_STYLES.get(self.state, STATE_STYLES["Working"])

        shadow_pen = QPen(QColor(80, 62, 48, 35), 9)
        shadow_pen.setCapStyle(Qt.RoundCap)
        shadow_pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(shadow_pen)
        painter.drawPath(path)

        ink = QColor(style["ink"])
        ink.setAlpha(205)
        ink_pen = QPen(ink, 4)
        ink_pen.setCapStyle(Qt.RoundCap)
        ink_pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(ink_pen)
        painter.drawPath(path)

        elapsed_seconds = max(0, int((datetime.now() - self.started_at).total_seconds()))
        painter.setPen(QColor(104, 92, 80, 170))
        painter.setFont(QFont("Segoe UI", 8))
        painter.drawText(
            QRectF(18, self.height() - 34, self.width() - 36, 18),
            Qt.AlignCenter,
            format_duration(elapsed_seconds)
        )

    def _scaled_path(self):
        xs = [p.x() for p in self.points]
        ys = [p.y() for p in self.points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        src_w = max(1, max_x - min_x)
        src_h = max(1, max_y - min_y)
        target = 92
        scale = min(target / src_w, target / src_h)

        offset_x = (self.width() - src_w * scale) / 2 - min_x * scale
        offset_y = 24 + (90 - src_h * scale) / 2 - min_y * scale

        scaled = [
            QPointF(p.x() * scale + offset_x, p.y() * scale + offset_y)
            for p in self.points
        ]

        path = QPainterPath()
        path.moveTo(scaled[0])
        if len(scaled) == 2:
            path.lineTo(scaled[1])
            return path

        for i in range(1, len(scaled) - 1):
            p1 = scaled[i]
            p2 = scaled[i + 1]
            mid = QPointF((p1.x() + p2.x()) / 2, (p1.y() + p2.y()) / 2)
            path.quadTo(p1, mid)
        path.lineTo(scaled[-1])
        return path



class ReminderWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)

        self.overlay = QWidget(self)
        self.overlay.setGeometry(self.rect())
        self.overlay.setStyleSheet("background-color: rgba(18, 18, 22, 105);")

        self.card = QWidget(self)
        self.card.setFixedSize(720, 660)
        self.card.setObjectName("card")
        self.card.setStyleSheet("""
            QWidget#card {
                background-color: rgba(255, 250, 242, 245);
                border-radius: 32px;
                border: 1px solid rgba(120, 98, 72, 35);
            }
        """)

        self.icon_label = QLabel("◐")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet("color: #d2b78b; font-size: 28px;")

        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("""
            color: #2d2a26;
            font-size: 38px;
            font-family: Segoe UI;
            font-weight: 700;
        """)

        self.goal_title = QLabel("Current focus")
        self.goal_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.goal_title.setStyleSheet("""
            color: #a79b8d;
            font-size: 13px;
            font-family: Segoe UI;
            letter-spacing: 1px;
        """)

        self.goal_label = QLabel()
        self.goal_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.goal_label.setWordWrap(True)
        self.goal_label.setStyleSheet("""
            color: #5e554b;
            font-size: 18px;
            font-family: Segoe UI;
            font-weight: 500;
            padding-left: 42px;
            padding-right: 42px;
        """)

        self.prompt_label = QLabel("What kind of time is this?")
        self.prompt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.prompt_label.setStyleSheet("""
            color: #7d7165;
            font-size: 15px;
            font-family: Segoe UI;
        """)

        self.state_buttons = []
        self.selected_state = "Working"
        states_row = QHBoxLayout()
        states_row.setSpacing(8)
        states_row.addStretch()
        for state in STATE_STYLES.keys():
            btn = StateButton(state)
            btn.clicked.connect(lambda checked, s=state: self.set_state(s))
            self.state_buttons.append(btn)
            states_row.addWidget(btn)
        states_row.addStretch()
        self.state_buttons[0].setChecked(True)

        self.message_label = QLabel()
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setWordWrap(True)
        self.message_label.setStyleSheet("""
            color: #6b6257;
            font-size: 16px;
            font-family: Segoe UI;
            font-weight: 400;
        """)

        self.canvas = TimeCircleCanvas(
            on_circle_started=self.circle_started,
            on_circle_left_open=self.circle_left_open,
            on_circle_completed=self.circle_completed
        )

        self.close_btn = QPushButton("let it fade")
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.clicked.connect(self.fade_out)
        self.close_btn.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 16px;
                background: rgba(225, 210, 188, 150);
                color: #6d6256;
                font-size: 14px;
                padding: 8px 18px;
            }
            QPushButton:hover {
                background: rgba(214, 190, 158, 180);
            }
        """)

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(38, 26, 38, 24)
        card_layout.setSpacing(0)
        card_layout.addWidget(self.icon_label)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.time_label)
        card_layout.addSpacing(16)
        card_layout.addWidget(self.goal_title)
        card_layout.addSpacing(6)
        card_layout.addWidget(self.goal_label)
        card_layout.addSpacing(22)
        card_layout.addWidget(self.prompt_label)
        card_layout.addSpacing(12)
        card_layout.addLayout(states_row)
        card_layout.addSpacing(16)
        card_layout.addWidget(self.canvas)
        card_layout.addSpacing(12)
        card_layout.addWidget(self.message_label)
        card_layout.addSpacing(14)

        close_row = QHBoxLayout()
        close_row.addStretch()
        close_row.addWidget(self.close_btn)
        close_row.addStretch()
        card_layout.addLayout(close_row)
        self.card.setLayout(card_layout)

        main_layout = QVBoxLayout(self)
        main_layout.addStretch()
        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(self.card)
        row.addStretch()
        main_layout.addLayout(row)
        main_layout.addStretch()
        self.setLayout(main_layout)

        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        self.fade_in_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out_anim = QPropertyAnimation(self.opacity_effect, b"opacity")

        self.current_app_name = ""
        self.current_goal = ""
        self.floating_fragment = None

    def set_state(self, state):
        self.selected_state = state
        for btn in self.state_buttons:
            btn.setChecked(btn.text() == state)
        self.canvas.set_state(state)
        self.message_label.setText(STATE_STYLES[state]["message"])

    def update_content(self, app_name, minutes_left, goal):
        self.current_app_name = app_name
        self.current_goal = goal or "Choose your next small step"
        self.canvas.reset_circle()
        self.set_state("Working")

        self.goal_label.setText(self.current_goal)
        self.time_label.setText(format_minutes(minutes_left))
        self.message_label.setText(random.choice(AI_LINES))

        self.opacity_effect.setOpacity(0)
        self.show()
        self.raise_()
        self.activateWindow()

        self.fade_in_anim.stop()
        self.fade_in_anim.setDuration(420)
        self.fade_in_anim.setStartValue(0)
        self.fade_in_anim.setEndValue(1)
        self.fade_in_anim.start()

        # It no longer disappears by itself.
        # After the user draws the first trace, the trace becomes a small
        # always-on-top floating fragment on the desktop.

    def circle_started(self, state, started_at):
        self.message_label.setText(f"{state} circle left open at {started_at.strftime('%I:%M %p').lstrip('0')}")

    def circle_left_open(self, state, started_at, points):
        self.message_label.setText("Your time trace is now floating on the desktop.")

        if self.floating_fragment is None:
            self.floating_fragment = FloatingFragment(
                points=points,
                state=state,
                started_at=started_at,
                on_click=self.restore_from_fragment
            )
        else:
            self.floating_fragment.set_points(points, state, started_at)

        self.floating_fragment.show()
        self.floating_fragment.raise_()
        self.fade_out()

    def restore_from_fragment(self):
        if not self.floating_fragment:
            return

        self.opacity_effect.setOpacity(0)
        self.show()
        self.raise_()
        self.activateWindow()

        self.canvas.load_open_circle(
            self.floating_fragment.state,
            self.floating_fragment.started_at,
            self.floating_fragment.points
        )
        self.set_state(self.floating_fragment.state)
        self.message_label.setText("Complete the trace when you are ready.")

        self.fade_in_anim.stop()
        self.fade_in_anim.setDuration(360)
        self.fade_in_anim.setStartValue(0)
        self.fade_in_anim.setEndValue(1)
        self.fade_in_anim.start()

    def circle_completed(self, state, started_at, completed_at, points):
        seconds = (completed_at - started_at).total_seconds()
        duration_text = format_duration(seconds)
        self.message_label.setText(f"This {state.lower()} circle took {duration_text}.")

        if self.floating_fragment:
            self.floating_fragment.hide()
            self.floating_fragment.deleteLater()
            self.floating_fragment = None

        save_fragment({
            "date": started_at.strftime("%Y-%m-%d"),
            "state": state,
            "app": self.current_app_name,
            "goal": self.current_goal,
            "started_at": started_at.isoformat(timespec="seconds"),
            "completed_at": completed_at.isoformat(timespec="seconds"),
            "duration_seconds": int(seconds)
        })

        QTimer.singleShot(1600, self.fade_out)

    def fade_out(self):
        self.fade_out_anim.stop()
        self.fade_out_anim.setDuration(900)
        self.fade_out_anim.setStartValue(self.opacity_effect.opacity())
        self.fade_out_anim.setEndValue(0)
        try:
            self.fade_out_anim.finished.disconnect()
        except TypeError:
            pass
        self.fade_out_anim.finished.connect(self.hide)
        self.fade_out_anim.start()


class SettingsWindow(QWidget):
    def __init__(self, config, on_save_callback):
        super().__init__()

        self.config = config
        self.on_save_callback = on_save_callback

        self.setWindowTitle("Time Circle Settings")
        self.resize(460, 300)
        self.setStyleSheet("""
            QWidget {
                background: #fffaf2;
                color: #5e554b;
                font-family: Segoe UI;
                font-size: 14px;
            }
            QLineEdit, QTimeEdit {
                background: #fffdf8;
                border: 1px solid #dfd1bd;
                border-radius: 10px;
                padding: 8px;
            }
            QPushButton {
                background: #dcc7a7;
                border: none;
                border-radius: 12px;
                padding: 10px;
                color: #4f463d;
            }
            QPushButton:hover {
                background: #d2b98f;
            }
        """)

        self.sleep_time_input = QTimeEdit()
        hour, minute = map(int, self.config["sleep_time"].split(":"))
        self.sleep_time_input.setTime(QTime(hour, minute))
        self.sleep_time_input.setDisplayFormat("HH:mm")

        self.apps_input = QLineEdit()
        self.apps_input.setText(", ".join(self.config["restricted_apps"]))
        self.apps_input.setPlaceholderText("比如 chrome.exe, firefox.exe, steam.exe")

        self.goal_input = QLineEdit()
        self.goal_input.setText(self.config.get("goal", ""))
        self.goal_input.setPlaceholderText("What are you trying to move toward?")

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save)

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)
        layout.addWidget(QLabel("Sleep time"))
        layout.addWidget(self.sleep_time_input)
        layout.addWidget(QLabel("Restricted apps"))
        layout.addWidget(self.apps_input)
        layout.addSpacing(8)
        layout.addWidget(QLabel("Current goal"))
        layout.addWidget(self.goal_input)
        layout.addSpacing(14)
        layout.addWidget(save_btn)
        self.setLayout(layout)

    def save(self):
        sleep_qtime = self.sleep_time_input.time()
        sleep_time = sleep_qtime.toString("HH:mm")

        apps = [
            app.strip()
            for app in self.apps_input.text().split(",")
            if app.strip()
        ]

        self.config["sleep_time"] = sleep_time
        self.config["restricted_apps"] = apps
        self.config["goal"] = self.goal_input.text().strip()

        save_config(self.config)
        self.on_save_callback(self.config)
        self.hide()

    def closeEvent(self, event):
        event.ignore()
        self.hide()


class SleepGuardApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        self.config = load_config()

        self.reminder = ReminderWindow()
        self.settings_window = SettingsWindow(
            self.config,
            self.update_config
        )

        self.tray = QSystemTrayIcon()
        icon = self.app.style().standardIcon(
            self.app.style().StandardPixmap.SP_ComputerIcon
        )
        self.tray.setIcon(icon)
        self.tray.setToolTip("Time Circle")

        self.menu = QMenu()
        self.settings_action = QAction("Settings")
        self.test_action = QAction("Show Time Circle")
        self.pause_action = QAction("Pause")
        self.quit_action = QAction("Quit")

        self.menu.addAction(self.settings_action)
        self.menu.addAction(self.test_action)
        self.menu.addAction(self.pause_action)
        self.menu.addSeparator()
        self.menu.addAction(self.quit_action)
        self.tray.setContextMenu(self.menu)

        self.settings_action.triggered.connect(self.show_settings)
        self.test_action.triggered.connect(self.show_test_circle)
        self.pause_action.triggered.connect(self.toggle_pause)
        self.quit_action.triggered.connect(self.quit)

        self.is_paused = False
        self.last_triggered_app = None

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_restricted_apps)
        self.timer.start(1000)

        self.tray.show()

    def update_config(self, new_config):
        self.config = new_config

    def show_settings(self):
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()

    def show_test_circle(self):
        minutes_left = minutes_until_sleep(self.config["sleep_time"])
        self.reminder.update_content(
            "manual-test",
            minutes_left,
            self.config.get("goal", "")
        )

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_action.setText("Resume")
            self.reminder.hide()
        else:
            self.pause_action.setText("Pause")

    def check_restricted_apps(self):
        if self.is_paused:
            return

        running_names = get_running_process_names()
        restricted_apps = [
            app.lower()
            for app in self.config.get("restricted_apps", [])
        ]

        for app_name in restricted_apps:
            if app_name in running_names:
                if self.last_triggered_app != app_name:
                    minutes_left = minutes_until_sleep(self.config["sleep_time"])
                    self.reminder.update_content(
                        app_name,
                        minutes_left,
                        self.config.get("goal", "")
                    )
                    self.last_triggered_app = app_name
                return

        self.last_triggered_app = None

    def quit(self):
        if self.reminder.floating_fragment:
            self.reminder.floating_fragment.close()
        self.reminder.close()
        self.settings_window.close()
        self.tray.hide()
        self.app.quit()

    def run(self):
        sys.exit(self.app.exec())


if __name__ == "__main__":
    SleepGuardApp().run()
