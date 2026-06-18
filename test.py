import tkinter as tk
from tkinter import Frame
from config.theme import (
    BG_MAIN, TEXT_MAIN, TEXT_SOFT,
    PAPER_BG, PAPER_BORDER,
    CARD_DEFAULT, CARD_RUNNING, CARD_DONE, CARD_ADD,
    CARD_BORDER, CARD_SHADOW,
    BTN_FILL, BTN_SHADOW, BTN_TEXT,
    TAPE_BEIGE, TAPE_ORANGE, TAPE_YELLOW
)

class LifeDirection(Frame):
    def __init__(self, parent, on_next=None):
        super().__init__(parent, bg=BG_MAIN)
        self.on_next = on_next

        self.canvas = tk.Canvas(
            self,
            width=900,
            height=700,
            bg=BG_MAIN,
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        self.title_font = ("Mynerve", 30)
        self.subtitle_font = ("Schoolbell", 18)
        self.card_title_font = ("Microsoft YaHei UI", 20, "bold")
        self.card_status_font = ("Microsoft YaHei UI", 11)
        self.add_font = ("Schoolbell", 18)
        self.button_font = ("Arial", 18, "bold")
        self.icon_font = ("Segoe UI Emoji", 24)

        self.cards = [
            {
                "x": 150, "y": 170, "w": 220, "h": 82,
                "title": "赚钱", "status": "未设置",
                "icon": "🏛", "fill": CARD_DEFAULT,
                "status_color": "#9c7357",
                "tape": None
            },
            {
                "x": 395, "y": 170, "w": 220, "h": 82,
                "title": "美白", "status": "执行中",
                "icon": "✿", "fill": CARD_RUNNING,
                "status_color": "#b17743",
                "tape": TAPE_ORANGE
            },
            {
                "x": 640, "y": 170, "w": 220, "h": 82,
                "title": "爱好", "status": "未设置",
                "icon": "🎸", "fill": CARD_DEFAULT,
                "status_color": "#9c7357",
                "tape": None
            },
            {
                "x": 150, "y": 278, "w": 220, "h": 82,
                "title": "健身", "status": "已完成",
                "icon": "🏋", "fill": CARD_DONE,
                "status_color": "#5d7a43",
                "tape": None
            },
            {
                "x": 395, "y": 278, "w": 220, "h": 82,
                "title": "+ Add Direction", "status": "",
                "icon": "", "fill": CARD_ADD,
                "status_color": TEXT_SOFT,
                "tape": TAPE_YELLOW,
                "is_add": True
            }
        ]

        self.draw_ui()

    def draw_ui(self):
        self.draw_title()
        self.draw_paper_panel()
        self.draw_cards()
        self.draw_next_button()

    def draw_title(self):
        self.canvas.create_text(
            125, 85,
            text="Life Directions",
            anchor="w",
            font=self.title_font,
            fill=TEXT_MAIN
        )

        self.canvas.create_text(
            125, 126,
            text="Set your life directions to get started",
            anchor="w",
            font=self.subtitle_font,
            fill=TEXT_MAIN
        )

    def draw_paper_panel(self):
        x1, y1, x2, y2 = 125, 150, 780, 510

        # 阴影
        self.round_rect(x1 + 4, y1 + 4, x2 + 4, y2 + 4, 16,
                        fill="#e8e0d6", outline="")

        # 纸板主体
        self.round_rect(x1, y1, x2, y2, 16,
                        fill=PAPER_BG, outline=PAPER_BORDER, width=1)

        # 内部细框
        self.canvas.create_rectangle(
            x1 + 20, y1 + 18, x2 - 20, y2 - 26,
            outline="#e2d8cb",
            width=1
        )

        # 左上大胶带
        self.draw_tape(190, 188, 110, 22, TAPE_BEIGE, angle=-18)

    def draw_cards(self):
        for card in self.cards:
            self.draw_single_card(card)

    def draw_single_card(self, card):
        x = card["x"]
        y = card["y"]
        w = card["w"]
        h = card["h"]
        fill = card["fill"]

        # 阴影
        self.round_rect(
            x, y + 4, x + w, y + h + 4, 12,
            fill=CARD_SHADOW, outline=""
        )

        # 卡片主体
        self.round_rect(
            x, y, x + w, y + h, 12,
            fill=fill, outline=CARD_BORDER, width=1
        )

        # 内层虚线（保留但变轻）
        self.canvas.create_rectangle(
            x + 12, y + 10, x + w - 12, y + h - 10,
            outline="#d8c4ae",
            width=1,
            dash=(4, 3)
        )

        # 小胶带
        if card.get("tape"):
            self.draw_tape(x + 28, y + 6, 34, 14, card["tape"], angle=-8)

        if card.get("is_add"):
            self.canvas.create_text(
                x + 30, y + h / 2,
                text=card["title"],
                anchor="w",
                font=self.add_font,
                fill=TEXT_MAIN
            )
            return

        # icon
        self.canvas.create_text(
            x + 42, y + h / 2 + 1,
            text=card["icon"],
            font=self.icon_font,
            fill="#9b6d47"
        )

        # title
        self.canvas.create_text(
            x + 90, y + 33,
            text=card["title"],
            anchor="w",
            font=self.card_title_font,
            fill=TEXT_MAIN
        )

        # status
        self.canvas.create_text(
            x + 90, y + 58,
            text=card["status"],
            anchor="w",
            font=self.card_status_font,
            fill=card["status_color"]
        )

    def draw_next_button(self):
        x, y, w, h = 620, 540, 155, 50

        # 阴影
        self.round_rect(
            x, y + 5, x + w, y + h + 5, 16,
            fill=BTN_SHADOW, outline=""
        )

        # 按钮
        self.round_rect(
            x, y, x + w, y + h, 16,
            fill=BTN_FILL, outline="#ad7547", width=1
        )

        # 按钮内层虚线
        self.round_rect(
            x + 8, y + 7, x + w - 8, y + h - 7, 12,
            fill="", outline="#dba46f", width=1
        )

        text_id = self.canvas.create_text(
            x + w / 2,
            y + h / 2,
            text="Next",
            font=self.button_font,
            fill=BTN_TEXT,
            anchor="center"
        )

        self.canvas.tag_bind(text_id, "<Button-1>", self.handle_next)

    def handle_next(self, event=None):
        if self.on_next:
            self.on_next()

    def draw_tape(self, cx, cy, w, h, color, angle=0):
        # tkinter canvas 不方便直接旋转，这里做一个近似的四边形胶带
        x1 = cx - w / 2
        y1 = cy - h / 2
        x2 = cx + w / 2
        y2 = cy + h / 2

        skew = 8
        self.canvas.create_polygon(
            x1, y1 + 4,
            x1 + skew, y1,
            x2, y1 + 2,
            x2 - skew, y2,
            x1 + 3, y2 - 1,
            fill=color,
            outline=""
        )

        # 加一点透明感的假效果
        self.canvas.create_line(
            x1 + 10, y1 + 4, x2 - 10, y2 - 2,
            fill="#f5e6b8", width=1
        )

    def round_rect(self, x1, y1, x2, y2, r=16, **kwargs):
        points = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1
        ]
        return self.canvas.create_polygon(points, smooth=True, splinesteps=36, **kwargs)