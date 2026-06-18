import tkinter as tk
from tkinter import Frame
from pathlib import Path
from PIL import Image, ImageTk, ImageOps, ImageDraw

from data.life_direction_repo import direction_cards
from config.theme import (
    BG_MAIN, TEXT_MAIN, TEXT_SOFT, PAPER_BG, PAPER_BORDER, CARD_ADD, CARD_BORDER, CARD_SHADOW,
    BTN_FILL,  BTN_TEXT, TAPE_BEIGE, TAPE_YELLOW, NEXT_BTN_DASH_THICKNESS,
    NEXT_BTN_DASH_LEN, NEXT_BTN_DASH_GAP_LEN,LARGE_TAPE_SKEW,SUB_FONT, TITLE_FONT,ADD_BUTTON_FONT,
    BADGE_FONT,BTN_FONT)
from services.life_direction_service import handle_add_direction,get_card_ui, open_config_dialog


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


        self.card_title_font = ("Microsoft YaHei UI", 20, "bold")
        self.card_status_font = ("Microsoft YaHei UI", 11)


        self.next_btn_img = None
        self.icon_font = ("Segoe UI Emoji", 24)
        self.tape_imgs = []
        # ===== 功能：保存 card 图标图片引用，防止图片不显示 =====
        self.emoji_dir = Path(__file__).resolve().parent.parent / "img" / "emoji"
        self.card_icon_imgs = []

        # ===== panel 区域 =====
        self.panel_x1 = 40
        self.panel_y1 = 150
        self.panel_x2 = 820
        self.panel_y2 = 525

        # ===== panel 内部内容区 =====
        self.inner_pad_x = 35
        self.inner_pad_top = 40

        # ===== card 布局 =====
        self.card_w = 220
        self.card_h = 82
        self.gap_x = 24
        self.gap_y = 24
        self.cols = 3

        #引入的default数据源life_direction_repo的
        self.direction_cards = direction_cards
        self.direction_cards.sort(
            key=lambda c: 0 if c["status"] == "not_configured" else 1
        )

        self.draw_ui()

    def draw_ui(self):
        self.canvas.delete("all")
        self.draw_title()
        self.draw_paper_panel()
        self.draw_cards()
        self.draw_next_button()

    def draw_title(self):
        self.canvas.create_text(
            60, 70,
            text="Life Directions",
            anchor="w",
            font=TITLE_FONT,
            fill=TEXT_MAIN
        )

        self.canvas.create_text(
            60, 108,
            text="Set your life directions to get started",
            anchor="w",
            font=SUB_FONT,
            fill=TEXT_MAIN
        )

    def draw_paper_panel(self):
        x1, y1, x2, y2 = self.panel_x1, self.panel_y1, self.panel_x2, self.panel_y2

        # 阴影
        self.round_rect(
            x1 + 3, y1 + 3, x2 + 3, y2 + 3, 16,
            fill="#ebe3d8", outline=""
        )

        # 主体
        self.round_rect(
            x1, y1, x2, y2, 16,
            fill=PAPER_BG, outline=PAPER_BORDER, width=1
        )

        # 内部细框
        self.canvas.create_rectangle(
            x1 + 20, y1 + 18, x2 - 20, y2 - 26,
            outline="#e2d8cb",
            width=1
        )

        # 左上大胶带
        self.draw_tape(
            x1 + 18, y1 + 34, 60, 22,
            TAPE_BEIGE,
            angle=-18,
            left_cut=20,
            right_cut=8,
            left_bottom_shift=LARGE_TAPE_SKEW
        )

        self.draw_config_badge()

    def draw_config_badge(self):
        configured = sum(1 for c in self.direction_cards if c["status"] != "not_configured")
        total = len(self.direction_cards)

        text = f"{configured} / {total} configured"

        w = 180
        h = 30
        x2 = self.panel_x2 - 34
        y1 = self.panel_y1 + 1
        x1 = x2 - w
        y2 = y1 + h

        # badge外层边框色
        self.round_rect(
            x1, y1, x2, y2, 40,
            fill="#d8c0a6", outline=""
        )

        # badge内层主体色
        self.round_rect(
            x1 + 1, y1 + 1, x2 - 1, y2 - 1, 40,
            fill="#f6eee3", outline=""
        )

        #badge文字
        self.canvas.create_text(
            (x1 + x2) / 2,
            (y1 + y2) / 2,
            text=text,
            font=BADGE_FONT,
            fill="#8a5f3c"
        )

    def draw_cards(self):
        # 最后拼一个 Add Direction 卡片
        cards_to_draw = self.direction_cards + [
            {
                "title": "+ Add Direction",
                "status": "",
                "fill": CARD_ADD,
                "status_color": TEXT_SOFT,
                "tape": TAPE_YELLOW,
                "is_add": True
            }
        ]

        for i, card in enumerate(cards_to_draw):
            x, y = self.get_card_position(i)
            self.draw_single_card(card, x, y,i)

    def get_card_position(self, index):
        col = index % self.cols
        row = index // self.cols

        start_x = self.panel_x1 + self.inner_pad_x
        start_y = self.panel_y1 + self.inner_pad_top

        x = start_x + col * (self.card_w + self.gap_x)
        y = start_y + row * (self.card_h + self.gap_y)
        return x, y

    def draw_single_card(self, card, x, y,index):
        w = self.card_w
        h = self.card_h

        # Add card 先单独处理(start)
        if card.get("is_add"):
            bg_id = self.round_rect(
                x, y, x + w, y + h, 12,
                fill=CARD_ADD, outline=CARD_BORDER, width=1
            )

            #内边虚线
            self.canvas.create_rectangle(
                x + 12, y + 10, x + w - 12, y + h - 10,
                outline="#d8c4ae",
                width=1,
                dash=(4, 3)
            )

            self.draw_tape(x + 28, y + 6, 34, 14, TAPE_YELLOW, angle=-8)

            text_id = self.canvas.create_text(
                x + 26, y + h / 2,
                text=card["title"],
                anchor="w",
                font=ADD_BUTTON_FONT,
                fill=TEXT_MAIN
            )

            self.canvas.itemconfig(bg_id, tags=("add_direction",))
            self.canvas.itemconfig(text_id, tags=("add_direction",))
            self.canvas.tag_bind(
                "add_direction",
                "<Button-1>",
                lambda e: handle_add_direction(self, e)
            )
            return
        # Add card 先单独处理(end)

        #处理其他life direction card
        #get_card_ui抽到life_direction_service里面了
        ui = get_card_ui(card)
        fill = ui["fill"]

        card_tag = f"direction_card_{index}"

        # card阴影
        shadow_id = self.round_rect(
            x, y + 4, x + w, y + h + 4, 12,
            fill=CARD_SHADOW, outline=""
        )
        self.canvas.itemconfig(shadow_id, tags=(card_tag,))

        # card卡片主体
        bg_id = self.round_rect(
            x, y, x + w, y + h, 12,
            fill=fill, outline=CARD_BORDER, width=1
        )
        self.canvas.itemconfig(bg_id, tags=(card_tag,))

        # card内层虚线
        dash_id = self.canvas.create_rectangle(
            x + 12, y + 10, x + w - 12, y + h - 10,
            outline="#d8c4ae",
            width=1,
            dash=(4, 3)
        )
        self.canvas.itemconfig(dash_id, tags=(card_tag,))

        # card title
        title_id = self.canvas.create_text(
            x + 100, y + 31,
            text=card["title"],
            anchor="w",
            font=self.card_title_font,
            fill=TEXT_MAIN
        )
        self.canvas.itemconfig(title_id, tags=(card_tag,))

        # card sub title
        status_id = self.canvas.create_text(
            x + 100, y + 60,
            text=ui["status_text"],
            anchor="w",
            font=self.card_status_font,
            fill=ui["status_color"]
        )
        self.canvas.itemconfig(status_id, tags=(card_tag,))

        # ===== 功能：显示 card icon png 图片  =====
        icon_path = card.get("icon_path")

        #一定会有emoji,因为add_direction_dialog 395行的逻辑，所以不用写if了
        try:
            pil_icon = Image.open(icon_path).convert("RGBA")
            pil_icon.thumbnail((49, 49), Image.LANCZOS)

            tk_icon = ImageTk.PhotoImage(pil_icon)
            self.card_icon_imgs.append(tk_icon)

            icon_id = self.canvas.create_image(
                x + 48,
                y + h / 2 - 1,
                image=tk_icon
            )
            self.canvas.itemconfig(icon_id, tags=(card_tag,))
        except Exception:
            print("No icon path")

        # card 小胶带
        if ui.get("tape"):
            self.draw_tape(x + 28, y + 6, 34, 14, ui["tape"], angle=-8)

        self.canvas.tag_bind(card_tag, "<Button-1>", lambda e: open_config_dialog(self, card))



    def draw_next_button(self):
        x, y, w, h = self.panel_x2 - 155, 540, 155, 50

        # 阴影
        self.round_rect(
            x + 2, y +2, x + w + 3, y + h + 3, 40,
            fill="#d8c1ad", outline=""
        )

        # 生成带浅色纹理的深色按钮
        self.next_btn_img = self.make_textured_button_image(
            width=w,
            height=h,
            base_hex=BTN_FILL,
            border_hex="#ad7547",
            radius=16
        )

        btn_id = self.canvas.create_image(
            x, y,
            image=self.next_btn_img,
            anchor="nw"
        )

        text_id = self.canvas.create_text(
            x + w / 2,
            y + h / 2,
            text="Next",
            font=BTN_FONT,
            fill=BTN_TEXT,
            anchor="center"
        )

        self.canvas.tag_bind(btn_id, "<Button-1>", self.handle_next)
        self.canvas.tag_bind(text_id, "<Button-1>", self.handle_next)

    def draw_tape(self, cx, cy, w, h, color, angle=0, left_cut=8, right_cut=8, left_bottom_shift=3):
        x1 = cx - w / 2
        y1 = cy - h / 2
        x2 = cx + w / 2
        y2 = cy + h / 2

        points = [
            x1, y1 + 4,
                x1 + left_cut, y1,
            x2, y1 + 2,
                x2 - right_cut, y2,
                x1 + left_bottom_shift, y2 - 1,
        ]

        self.canvas.create_polygon(
            points,
            fill=color,
            outline=""
        )

        # ===== 只加噪点，不改原来的形状和水平度 =====
        pad = 2
        img_w = int(x2 - x1) + pad * 2
        img_h = int(y2 - y1) + pad * 2

        noise = Image.effect_noise((img_w, img_h), 100).convert("L")
        noise = ImageOps.autocontrast(noise, cutoff=4)
        noise = noise.point(lambda p: int((255 - p) * 0.25))

        texture = Image.new("RGBA", (img_w, img_h), (255, 250, 242, 0))
        texture.putalpha(noise)

        mask = Image.new("L", (img_w, img_h), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.polygon([
            (pad, 4 + pad),
            (left_cut + pad, pad),
            (w + pad, 2 + pad),
            (w - right_cut + pad, h + pad),
            (left_bottom_shift + pad, h - 1 + pad),
        ], fill=255)

        textured = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
        textured.paste(texture, (0, 0), mask)

        tk_img = ImageTk.PhotoImage(textured)
        self.tape_imgs.append(tk_img)

        self.canvas.create_image(
            x1 - pad,
            y1 - pad,
            image=tk_img,
            anchor="nw"
        )

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
        return self.canvas.create_polygon(
            points,
            smooth=True,
            splinesteps=36,
            **kwargs
        )

    def make_textured_button_image(self, width, height, base_hex, border_hex, radius=16):
        base = Image.new("RGBA", (width, height), base_hex)

        # ===== 自己生成浅色细纹，不依赖外部 texture 图 =====
        noise = Image.effect_noise((width, height), 100).convert("L")
        noise = ImageOps.autocontrast(noise, cutoff=4)
        noise = noise.point(lambda p: int((255 - p) * 0.15))

        # 浅色纹理层：白偏米一点
        texture = Image.new("RGBA", (width, height), (255, 250, 242, 0))
        texture.putalpha(noise)

        button = Image.alpha_composite(base, texture)

        # 上方一点微光，像纸面受光
        highlight = Image.new("RGBA", (width, height), (255, 255, 255, 0))
        draw_hi = ImageDraw.Draw(highlight)
        draw_hi.rounded_rectangle(
            (1, 1, width - 2, int(height * 0.52)),
            radius=radius,
            fill=(255, 255, 255, 18)
        )
        button = Image.alpha_composite(button, highlight)

        # 圆角 mask
        mask = Image.new("L", (width, height), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.rounded_rectangle(
            (0, 0, width - 1, height - 1),
            radius=radius,
            fill=255
        )

        rounded = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        rounded.paste(button, (0, 0), mask)

        # 外边框
        draw_rgba = ImageDraw.Draw(rounded)
        draw_rgba.rounded_rectangle(
            (0, 0, width - 1, height - 1),
            radius=radius,
            outline=border_hex,
            width=1
        )


        # 内层虚线（用很多小短线假装虚线）
        dash_color = "#e3b387"
        x1, y1, x2, y2 = 5, 4, width - 6, height - 5
        dash_len = NEXT_BTN_DASH_LEN
        gap_len = NEXT_BTN_DASH_GAP_LEN

        # 上边
        for x in range(x1 + 12, x2 - 12, dash_len + gap_len):
            draw_rgba.line((x, y1, min(x + dash_len, x2 - 12), y1), fill=dash_color, width=NEXT_BTN_DASH_THICKNESS)

        # 下边
        for x in range(x1 + 12, x2 - 12, dash_len + gap_len):
            draw_rgba.line((x, y2, min(x + dash_len, x2 - 12), y2), fill=dash_color, width=NEXT_BTN_DASH_THICKNESS)

        # 左边
        for y in range(y1 + 12, y2 - 12, dash_len + gap_len):
            draw_rgba.line((x1, y, x1, min(y + dash_len, y2 - 12)), fill=dash_color, width=NEXT_BTN_DASH_THICKNESS)

        # 右边
        for y in range(y1 + 12, y2 - 12, dash_len + gap_len):
            draw_rgba.line((x2, y, x2, min(y + dash_len, y2 - 12)), fill=dash_color, width=NEXT_BTN_DASH_THICKNESS)

        return ImageTk.PhotoImage(rounded)

    def handle_next(self, event=None):
        if self.on_next:
            self.on_next()