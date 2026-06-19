import tkinter as tk
from pathlib import Path
import tkinter.font as tkfont
from dialogs.configue_dialog_add import ConfigureDialogAdd
from PIL import Image, ImageTk, ImageOps, ImageDraw
from config.theme import (
    BG_MAIN,
    CONFIGUE_BTN_FILL,
    CARD_PENDING_ACTIVATION,
    SEED_CARD_BG,
    CONFIGUE_BTN_BORDER,
    CONFIGUE_BTN_TEXT_COLOR
)


class ConfigureDialog(tk.Toplevel):
    def __init__(self, parent, direction_title, on_save=None, initial_data=None):
        super().__init__(parent)
        self.withdraw()

        self.parent = parent
        self.direction_title = direction_title
        self.on_save = on_save
        self.is_edit_mode = False

        # ========= 基础窗口设置 =========
        self.title(f"配置 - {direction_title}")
        self.configure(bg=BG_MAIN)
        self.resizable(False, False)

        self.dialog_width = 920
        self.dialog_height = 620
        self._center_window()

        self.seed_card_base_width = 385

        self.transient(parent)
        self.deiconify()
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.handle_cancel)

        self.texture_imgs = []
        self.tape_imgs = []
        self.bg_imgs = []
        self.category_icon_imgs = []
        self.seed_texture_pil = None
        self._seed_redraw_job = None

        # ========= SQLite-friendly 数据结构 =========
        self.data = initial_data if initial_data else self.get_default_data(direction_title)

        # 容错：如果旧数据没这些字段，就补上
        self.normalize_data()
        self.nav_stack = [(direction_title, self.data)]
        self.current_data = self.data

        # ========= 配色 =========
        self.colors = {
            "panel_bg": "#fbf8f4",
            "panel_border": "#ebe0d6",
            "title": "#5c4335",
            "subtitle": "#8a7264",
            "line": "#eadfd7",

            "btn_bg": "#f4ebe4",
            "btn_active": "#eadcd0",
            "btn_fg": "#7a5f50",
            "btn_border": "#d8c8bc",

            "save_bg": "#ead8cb",
            "save_fg": "#5c4335",
            "save_border": "#d7bfae",

            "category_bg":"#FFFDF6",
            "category_border": "#dbc07a",


            "seed_bg": SEED_CARD_BG,
            "seed_border": "#e6d9cf",

            "delete_bg": "#f6eee8",
            "delete_fg": "#8a634c",
            "delete_border": "#d7c1b2",

            "card_shadow": "#eadfd5",
            "dash_border": "#e3b387",
        }

        self.build_ui()

    # =========================
    # 1. 居中弹窗
    # =========================
    def _center_window(self):
        self.update_idletasks()

        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_w = self.parent.winfo_width()
        parent_h = self.parent.winfo_height()

        x = parent_x + (parent_w - self.dialog_width) // 2
        y = parent_y + (parent_h - self.dialog_height) // 2

        self.geometry(f"{self.dialog_width}x{self.dialog_height}+{x}+{y}")

    # =========================
    # 2. 默认数据
    # =========================
    def get_default_data(self, direction_title):
        defaults = {
            "赚钱": {
                "direction_id": None,
                "direction_title": "赚钱",
                "sections": [
                    {"section_id": None, "name": "找工作", "sort_order": 0,"icon_path": "img/emoji/1f30b.png"},
                    {"section_id": None, "name": "副业", "sort_order": 1,"icon_path": "img/emoji/1f32a-fe0f.png"},
                    {"section_id": None, "name": "兼职", "sort_order": 1,"icon_path": "img/emoji/dollar.png"},
                    {"section_id": None, "name": "创业", "sort_order": 1,"icon_path": "img/emoji/1f5fd.png"},
                ],
                "seeds": [

                ]
            },
            "美白": {
                "direction_id": None,
                "direction_title": "美白",
                "sections": [

                ],
                "seeds": [
                    {"seed_id": None, "section_id": None, "name": "早晚护肤", "sort_order": 0},
                    {"seed_id": None, "section_id": None, "name": "早晚一张面膜", "sort_order": 0},
                    {"seed_id": None, "section_id": None, "name": "每天一个番茄", "sort_order": 1},
                    {"seed_id": None, "section_id": None, "name": "出门涂防晒", "sort_order": 1},
                ]
            },
            "健身": {
                "direction_id": None,
                "direction_title": "健身",
                "sections": [

                ],
                "seeds": [
                    {"seed_id": None, "section_id": None, "name": "每周训练1次私教课", "sort_order": 0, "icon": "☐"},
                    {"seed_id": None, "section_id": None, "name": "每天1小时resistance training", "sort_order": 1, "icon": "☐"},
                    {"seed_id": None, "section_id": None, "name": "吃蛋白粉", "sort_order": 1,
                     "icon": "☐"},
                ]
            },
            "爱好": {
                "direction_id": None,
                "direction_title": "爱好",
                "sections": [
                    {"section_id": None, "name": "音乐", "sort_order": 0,"icon_path": "img/emoji/1f3a7.png"},
                    {"section_id": None, "name": "阅读", "sort_order": 1,"icon_path": "img/emoji/1f4d6.png"},
                ],
                "seeds": [
                    {"seed_id": None, "section_id": None, "name": "练琴 20 分钟", "sort_order": 0, "icon": "☐"},
                    {"seed_id": None, "section_id": None, "name": "读书 20 页", "sort_order": 1, "icon": "☐"},
                ]
            }
        }

        return defaults.get(
            direction_title,
            {
                "direction_id": None,
                "direction_title": direction_title,
                "sections": [
                    {"section_id": None, "name": "分类1", "sort_order": 0,"icon_path":""},
                    {"section_id": None, "name": "分类2", "sort_order": 1,"icon_path":""},
                ],
                "seeds": [
                    {"seed_id": None, "section_id": None, "name": "示例 Seed 1", "sort_order": 0, "icon": "☐"},
                    {"seed_id": None, "section_id": None, "name": "示例 Seed 2", "sort_order": 1, "icon": "☐"},
                ]
            }
        )

    # =========================
    # 3. 数据补齐
    # =========================
    def normalize_data(self):
        if "direction_id" not in self.data:
            self.data["direction_id"] = None
        if "direction_title" not in self.data:
            self.data["direction_title"] = self.direction_title
        if "sections" not in self.data:
            self.data["sections"] = []
        if "seeds" not in self.data:
            self.data["seeds"] = []

        for i, sec in enumerate(self.data["sections"]):
            self.normalize_section(sec, i)

        for i, seed in enumerate(self.data["seeds"]):
            self.normalize_seed(seed, i)

    def normalize_section(self, section, index=0):
        section.setdefault("section_id", None)
        section.setdefault("name", f"分类{index+1}")
        section.setdefault("sort_order", index)
        section.setdefault("icon_path", "")
        section.setdefault("is_configured", False)
        section.setdefault("sections", [])
        section.setdefault("seeds", [])

        for child_index, child in enumerate(section["sections"]):
            self.normalize_section(child, child_index)

        for seed_index, seed in enumerate(section["seeds"]):
            self.normalize_seed(seed, seed_index)

    def normalize_seed(self, seed, index=0):
        seed.setdefault("seed_id", None)
        seed.setdefault("section_id", None)
        seed.setdefault("name", f"Seed {index+1}")
        seed.setdefault("sort_order", index)
        seed.setdefault("icon", "☐")

    def get_category_config_status(self, section):
        if not section.get("is_configured", False):
            return "未配置"

        child_sections = section.get("sections", [])
        if child_sections:
            if all(self.is_category_configured(child) for child in child_sections):
                return ""
            return "未配置完"

        if section.get("seeds", []):
            return ""

        return "未配置完"

    def is_category_configured(self, section):
        return self.get_category_config_status(section) == ""
    # =========================
    # 4. 圆角矩形（canvas）
    # =========================
    def round_rect(self, canvas, x1, y1, x2, y2, r, **kwargs):
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
        return canvas.create_polygon(points, smooth=True, splinesteps=36, **kwargs)

    # =========================
    # 5. 噪点图
    # =========================
    def make_noise_overlay_image(self, width, height, opacity=0.16, strength=100):
        width = max(1, int(width))
        height = max(1, int(height))

        img = Image.new("RGBA", (width, height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)

        step = max(6, int(120 / max(1, strength)))
        alpha = max(8, min(80, int(255 * opacity)))

        for y in range(0, height, step):
            for x in range(0, width, step):
                if (x + y) % (step * 2) == 0:
                    draw.point((x, y), fill=(255, 255, 255, alpha))

        tk_img = ImageTk.PhotoImage(img)
        self.texture_imgs.append(tk_img)
        return tk_img

    def load_category_icon(self, icon_path, size=38):
        if not icon_path:
            return None

        path = Path(icon_path)
        if not path.exists():
            return None

        img = Image.open(path).convert("RGBA")
        img = ImageOps.contain(img, (size, size), Image.LANCZOS)

        tk_img = ImageTk.PhotoImage(img)
        self.category_icon_imgs.append(tk_img)
        return tk_img

    # =========================
    # 6. 纯 canvas action 按钮
    # =========================
    def make_canvas_action_btn(
        self,
        parent,
        text,
        command,
        width=112,
        height=48,
        fill=None,
        border=None,
        text_color=None
    ):
        fill = CONFIGUE_BTN_FILL if fill is None else fill
        border = CONFIGUE_BTN_BORDER if border is None else border
        text_color = CONFIGUE_BTN_TEXT_COLOR if text_color is None else text_color

        wrap = tk.Frame(parent, bg=self.colors["panel_bg"], bd=0, highlightthickness=0)

        canvas = tk.Canvas(
            wrap,
            width=width,
            height=height,
            bg=self.colors["panel_bg"],
            highlightthickness=0,
            bd=0,
            relief="flat"
        )
        canvas.pack()

        shadow_id = self.round_rect(
            canvas, 7, 5, width - 1, height - 3,
            16, fill=self.colors["card_shadow"], outline=""
        )

        bg_id = self.round_rect(
            canvas, 4, 2, width - 4, height - 6,
            16, fill=fill, outline=border, width=1
        )

        dash_id = self.round_rect(
            canvas, 6, 5, width - 6, height - 9,
            12, fill="", outline=self.colors["dash_border"], width=1, dash=(2, 2)
        )

        noise_img = self.make_noise_overlay_image(width - 8, height - 8, opacity=0.16, strength=100)
        noise_id = canvas.create_image(4, 2, image=noise_img, anchor="nw")

        text_id = canvas.create_text(
            width / 2, height / 2 - 1,
            text=text,
            font=("Microsoft YaHei UI", 11, "bold"),
            fill=text_color,
            anchor="center"
        )

        btn_tag = f"btn_{id(canvas)}"
        for item_id in (shadow_id, bg_id, dash_id, noise_id, text_id):
            canvas.itemconfig(item_id, tags=(btn_tag,))

        canvas.tag_bind(btn_tag, "<Button-1>", lambda e: command())
        return wrap

    # =========================
    # 7. 总 UI
    # =========================
    def build_ui(self):
        outer = tk.Frame(self, bg=BG_MAIN)
        outer.pack(fill="both", expand=True, padx=20, pady=20)

        self.panel_canvas = tk.Canvas(
            outer,
            bg=BG_MAIN,
            highlightthickness=0,
            bd=0,
            relief="flat"
        )
        self.panel_canvas.pack(fill="both", expand=True)

        self.body = tk.Frame(
            self.panel_canvas,
            bg=self.colors["panel_bg"],
            bd=0,
            highlightthickness=0
        )

        self.body_window = self.panel_canvas.create_window(
            0, 0,
            anchor="nw",
            window=self.body
        )

        def redraw_panel(event):
            self.panel_canvas.delete("panel_bg")

            w = event.width
            h = event.height

            x1, y1 = 10, 10
            x2, y2 = w - 10, h - 10

            self.round_rect(
                self.panel_canvas,
                x1 - 4, y1 - 3, x2 + 4, y2 + 6,
                32,
                fill="#f8f2ec",
                outline="",
                tags="panel_bg"
            )

            self.round_rect(
                self.panel_canvas,
                x1, y1, x2, y2,
                30,
                fill=self.colors["panel_bg"],
                outline=self.colors["panel_border"],
                width=1,
                tags="panel_bg"
            )

            self.panel_canvas.coords(self.body_window, x1 + 30, y1 + 26)
            self.panel_canvas.itemconfigure(self.body_window, width=(x2 - x1 - 60))


        self.panel_canvas.bind("<Configure>", redraw_panel)
        self.render_all()

    def render_all(self):
        for widget in self.body.winfo_children():
            widget.destroy()

        self.build_top()
        self.build_divider(self.body, pady=(14, 18))

        footer = tk.Frame(self.body, bg=self.colors["panel_bg"])
        footer.pack(side="bottom", fill="x")

        self.build_divider(footer, pady=(16, 18))
        self.render_bottom(footer)

        content_area = tk.Frame(self.body, bg=self.colors["panel_bg"], height=320)
        content_area.pack(fill="x", expand=False)
        content_area.pack_propagate(False)

        self.scroll_canvas = tk.Canvas(
            content_area,
            bg=self.colors["panel_bg"],
            highlightthickness=0,
            bd=0,
            relief="flat"
        )
        self.scroll_canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = tk.Scrollbar(
            content_area,
            orient="vertical",
            command=self.scroll_canvas.yview
        )

        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.content = tk.Frame(self.scroll_canvas, bg=self.colors["panel_bg"])
        self.content_window = self.scroll_canvas.create_window(
            0, 0,
            anchor="nw",
            window=self.content
        )

        self.content.bind("<Configure>", self._on_content_configure)
        self.scroll_canvas.bind("<Configure>", self._on_canvas_configure)
        self.scroll_canvas.bind(
            "<Enter>",
            lambda e: self.scroll_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        )
        self.scroll_canvas.bind(
            "<Leave>",
            lambda e: self.scroll_canvas.unbind_all("<MouseWheel>")
        )

        self.render_categories()
        self.render_seeds()

    def _on_content_configure(self, event):
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))
        self.update_scrollbar_visibility()

    def _on_canvas_configure(self, event):
        self.scroll_canvas.itemconfigure(self.content_window, width=event.width)
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))
        self.update_scrollbar_visibility()

    def update_scrollbar_visibility(self):
        self.update_idletasks()
        bbox = self.scroll_canvas.bbox("all")
        if not bbox:
            self.scrollbar.pack_forget()
            return

        canvas_h = self.scroll_canvas.winfo_height()
        content_h = bbox[3] - bbox[1]

        if content_h > canvas_h + 2:
            if not self.scrollbar.winfo_ismapped():
                self.scrollbar.pack(side="right", fill="y")
        else:
            if self.scrollbar.winfo_ismapped():
                self.scrollbar.pack_forget()

    def _on_mousewheel(self, event):
        try:
            self.scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception:
            pass

    # =========================
    # 8. 顶部
    # =========================
    def jump_to_nav(self, index):
        if index < 0 or index >= len(self.nav_stack):
            return

        self.nav_stack = self.nav_stack[:index + 1]
        self.current_data = self.nav_stack[-1][1]
        self.is_edit_mode = False
        self.render_all()

    def go_back_category(self):
        self.jump_to_nav(len(self.nav_stack) - 2)

    def build_top(self):
        top = tk.Frame(self.body, bg=self.colors["panel_bg"])
        top.pack(fill="x")


        tape2_path = Path(__file__).resolve().parent.parent / "img" / "tape" / "tape2.png"

        tape2_img = self.load_rotated_tape(tape2_path, width=270, angle=0, alpha=1)

        if tape2_img:
            tape2_label = tk.Label(top, image=tape2_img, bg=self.colors["panel_bg"], bd=0, highlightthickness=0)
            tape2_label.place(relx=1.0, x=-280, y=-8, anchor="ne")

        left = tk.Frame(top, bg=self.colors["panel_bg"])
        left.pack(side="left", anchor="nw")

        title_row = tk.Frame(left, bg=self.colors["panel_bg"])
        title_row.pack(anchor="w")

        title_link_font = tkfont.Font(family="Microsoft YaHei UI", size=20, weight="bold")
        title_hover_font = tkfont.Font(family="Microsoft YaHei UI", size=20, weight="bold", underline=True)

        for index, (title, _node) in enumerate(self.nav_stack):
            is_current = index == len(self.nav_stack) - 1

            if is_current:
                title_part = tk.Label(
                    title_row,
                    text=title,
                    font=title_link_font,
                    fg=self.colors["title"],
                    bg=self.colors["panel_bg"]
                )
                title_part.pack(side="left")
            else:
                title_part = tk.Label(
                    title_row,
                    text=title,
                    font=title_link_font,
                    fg="#8a634c",
                    bg=self.colors["panel_bg"],
                    cursor="hand2"
                )
                title_part.pack(side="left")
                title_part.bind("<Button-1>", lambda event, i=index: self.jump_to_nav(i))
                title_part.bind("<Enter>", lambda event, label=title_part: label.configure(font=title_hover_font, fg=self.colors["title"], bg=self.colors["panel_bg"]))
                title_part.bind("<Leave>", lambda event, label=title_part: label.configure(font=title_link_font, fg="#8a634c", bg=self.colors["panel_bg"]))

            if index < len(self.nav_stack) - 1:
                sep = tk.Label(
                    title_row,
                    text=" · ",
                    font=title_link_font,
                    fg="#c49a78",
                    bg=self.colors["panel_bg"]
                )
                sep.pack(side="left")

        subtitle_label = tk.Label(
            left,
            text="专注于这 life direction 的具体事项",
            font=("Microsoft YaHei UI", 10),
            fg=self.colors["subtitle"],
            bg=self.colors["panel_bg"]
        )
        subtitle_label.pack(anchor="w", pady=(8, 0))
        right = tk.Frame(top, bg=self.colors["panel_bg"])
        right.pack(side="right", anchor="ne", pady=(38, 0))

        add_btn = self.make_canvas_action_btn(
            right,
            text="+ Add",
            command=self.handle_add_menu,
            width=112,
            height=48
        )
        add_btn.pack(side="left", padx=(0, 10))

        edit_text = "Done" if self.is_edit_mode else "Edit"
        edit_btn = self.make_canvas_action_btn(
            right,
            text=edit_text,
            command=self.toggle_edit_mode,
            width=112,
            height=48
        )
        edit_btn.pack(side="left")

    def build_divider(self, parent, pady=(8, 8)):
        line = tk.Frame(parent, bg=self.colors["line"], height=1)
        line.pack(fill="x", pady=pady)

    # =========================
    # 9. section 标题
    # =========================
    def render_block_header(self, parent, text):
        row = tk.Frame(parent, bg=self.colors["panel_bg"])
        row.pack(fill="x")

        title = tk.Label(
            row,
            text=text,
            font=("Microsoft YaHei UI", 14, "bold"),
            fg=self.colors["title"],
            bg=self.colors["panel_bg"]
        )
        title.pack(side="left")


        line_wrap = tk.Frame(row, bg=self.colors["panel_bg"], height=40)
        line_wrap.pack(side="left", fill="x", expand=True, padx=(12, 0))
        line_wrap.pack_propagate(False)

        line_canvas = tk.Canvas(
            line_wrap,
            bg=self.colors["panel_bg"],
            height=40,
            highlightthickness=0,
            bd=0,
            relief="flat"
        )
        line_canvas.pack(fill="both", expand=True)

        def draw_dash_line(event):
            line_canvas.delete("all")

            w = event.width
            mid_y = 20

            # 先画虚线
            line_canvas.create_line(
                0, mid_y, w, mid_y,
                fill=self.colors["line"],
                width=1,
                dash=(4, 5)
            )



        line_canvas.bind("<Configure>", draw_dash_line)

    # =========================
    # 10. Categories
    # =========================
    def render_categories(self):
        sections = sorted(
            self.current_data.get("sections", []),
            key=lambda s: s.get("sort_order", 0)
        )

        if not sections:
            return

        block = tk.Frame(self.content, bg=self.colors["panel_bg"])
        block.pack(fill="x", pady=(0, 8))

        self.render_block_header(block, "Categories")

        cards_wrap = tk.Frame(block, bg=self.colors["panel_bg"])
        cards_wrap.pack(fill="x", pady=(12, 0))

        for idx, section in enumerate(sections):
            card = self.draw_category_card(cards_wrap, section)

            row = idx // 2
            col = idx % 2

            if col == 0:
                card.grid(row=row, column=col, sticky="ew", padx=(0, 14), pady=(0, 12))
            else:
                card.grid(row=row, column=col, sticky="ew", padx=(0, 0), pady=(0, 12))

        cards_wrap.grid_columnconfigure(0, weight=1)
        cards_wrap.grid_columnconfigure(1, weight=1)

    def draw_category_card(self, parent, section):
        color = section.get("color", "yellow")

        # if color == "blue":
        #     fill = self.colors["category_blue"]
        #     border = self.colors["category_blue_border"]
        #     icon_text = "✦"
        # else:
        fill = self.colors["category_bg"]
        border = self.colors["category_border"]
        icon_text = "✿"

        card_outer = tk.Frame(parent, bg=self.colors["panel_bg"], bd=0, highlightthickness=0)
        card_outer.grid_propagate(False)

        canvas = tk.Canvas(
            card_outer,
            bg=self.colors["panel_bg"],
            highlightthickness=0,
            bd=0,
            relief="flat",
            height=75
        )
        canvas.pack(fill="both", expand=True)

        content = tk.Frame(canvas, bg=fill)
        left = tk.Frame(content, bg=fill)
        left.pack(side="left", fill="x", expand=True)

        icon_img = self.load_category_icon(section.get("icon_path"))

        if icon_img:
            icon = tk.Label(
                left,
                image=icon_img,
                bg=fill
            )
        else:
            icon = tk.Label(
                left,
                text=icon_text,
                font=("Microsoft YaHei UI", 16, "bold"),
                fg="#7a5f50",
                bg=fill
            )
        icon.pack(side="left", padx=(0, 10))

        title = tk.Label(
            left,
            text=section["name"],
            font=("Microsoft YaHei UI", 16, "bold"),
            fg="#3f3029",
            bg=fill
        )
        title.pack(side="left")

        config_status = self.get_category_config_status(section)
        if config_status:
            status = tk.Label(
                left,
                text=config_status,
                font=("Microsoft YaHei UI", 9, "bold"),
                fg="#9c7357",
                bg="#fff3e8",
                padx=8,
                pady=2
            )
            status.pack(side="left", padx=(10, 0))

        if self.is_edit_mode:
            btn_wrap = tk.Frame(content, bg=fill, width=34, height=34)
            btn_wrap.pack(side="right", padx=(10, 0))
            btn_wrap.pack_propagate(False)

            self.make_round_delete_btn(
                parent=btn_wrap,
                x=0,
                y=0,
                command=lambda s=section: self.delete_section(s),
                size=34,
                fill=self.colors["delete_bg"],
                outline=self.colors["delete_border"],
                text_color=self.colors["delete_fg"]
            )
        else:
            arrow = tk.Label(
                content,
                text="»",
                font=("Microsoft YaHei UI", 19, "bold"),
                fg="#d8b56f",
                bg=fill,
                cursor="hand2"
            )
            arrow.pack(side="right", padx=(12, 6))

            def open_section(event=None, s=section):
                self.open_category_config(s)

            canvas.bind("<Button-1>", open_section)
            content.bind("<Button-1>", open_section)
            title.bind("<Button-1>", open_section)
            arrow.bind("<Button-1>", open_section)

        content_window = canvas.create_window(24, 0, anchor="nw", window=content)

        def redraw(event):
            canvas.delete("shape")

            w = event.width
            h = event.height

            self.round_rect(
                canvas,
                4, 8, w - 4, h - 2,
                12,
                fill=self.colors["card_shadow"],
                outline="",
                tags="shape"
            )

            self.round_rect(
                canvas,
                4, 4, w - 4, h - 6,
                25,
                fill=fill,
                outline=border,
                width=1,
                tags="shape"
            )

            self.round_rect(
                canvas,
                10, 10, w - 10, h - 12,
                25,
                fill="",
                outline=self.colors["dash_border"],
                width=1,
                dash=(4, 3),
                tags="shape"
            )

            noise_img = self.make_noise_overlay_image(w - 8, h - 10, opacity=0.16, strength=100)
            canvas.create_image(
                4, 4,
                image=noise_img,
                anchor="nw",
                tags="shape"
            )

            canvas.coords(content_window, 24, 12)
            canvas.itemconfigure(content_window, width=w - 48, height=h - 24)

        canvas.bind("<Configure>", redraw)
        return card_outer

    # =========================
    # 11. Seeds & Steps
    # =========================
    def render_seeds(self):
        seeds = sorted(
            self.current_data.get("seeds", []),
            key=lambda s: s.get("sort_order", 0)
        )

        if not seeds:
            return

        block = tk.Frame(self.content, bg=self.colors["panel_bg"])
        block.pack(fill="x")

        # 不再单独调用 render_block_header
        # Seeds & Steps 标题、虚线、tape、lined paper 全部放进同一个 canvas 里画
        self.seed_list_canvas = tk.Canvas(
            block,
            bg=self.colors["panel_bg"],
            highlightthickness=0,
            bd=0,
            relief="flat",
            height=300
        )
        self.seed_list_canvas.pack(fill="x", pady=(0, 0))

        self.seed_texture_path = (
                Path(__file__).resolve().parent.parent
                / "img" / "panel-texture" / "lined-paper.png"
        )

        if self.seed_texture_pil is None:
            self.seed_texture_pil = Image.open(self.seed_texture_path).convert("RGBA")

        self.seed_list_canvas.bind("<Configure>", self._on_seed_canvas_configure)

        self.after_idle(self.redraw_seed_list_canvas)

        filler = tk.Frame(block, bg=self.colors["panel_bg"], height=18)
        filler.pack(fill="x")

    def _on_seed_canvas_configure(self, event):
        if self._seed_redraw_job is not None:
            self.after_cancel(self._seed_redraw_job)

        # 合并短时间内多次 Configure
        self._seed_redraw_job = self.after(16, self.redraw_seed_list_canvas)

    def redraw_seed_list_canvas(self):
        self._seed_redraw_job = None

        if not hasattr(self, "seed_list_canvas") or not self.seed_list_canvas.winfo_exists():
            return

        canvas = self.seed_list_canvas
        canvas.delete("all")

        canvas.update_idletasks()
        full_w = canvas.winfo_width()
        if full_w <= 1:
            return

        seeds = sorted(
            self.current_data.get("seeds", []),
            key=lambda s: s.get("sort_order", 0)
        )
        if not seeds:
            canvas.config(height=1)
            return

        # ========= 统一 section 头部 =========
        header_h = 52
        title_x = 0
        title_y = 22

        title_font = ("Microsoft YaHei UI", 14, "bold")
        title_text = "Seeds & Steps"

        title_id = canvas.create_text(
            title_x,
            title_y,
            text=title_text,
            anchor="w",
            font=title_font,
            fill=self.colors["title"]
        )

        title_bbox = canvas.bbox(title_id)
        title_right = title_bbox[2] if title_bbox else 140

        line_start_x = title_right + 14
        line_y = title_y + 1
        line_end_x = max(line_start_x + 40, full_w - 8)

        canvas.create_line(
            line_start_x,
            line_y,
            line_end_x,
            line_y,
            fill=self.colors["line"],
            width=1,
            dash=(4, 5)
        )

        # ========= tape：和虚线、lined paper同属一个canvas =========
        tape1_path = Path(__file__).resolve().parent.parent / "img" / "tape" / "tape1111.png"
        tape_w = 120

        tape_x = line_start_x + 485
        tape_y = -18

        # 防止窗口变窄时 tape 超出右边
        tape_x = min(tape_x, max(line_start_x + 16, full_w - tape_w - 24))

        # ========= lined paper / cards =========
        top_pad = 18
        bottom_pad = 18
        row_gap = 10

        paper_x = 20
        paper_y = header_h - 6
        paper_w = max(120, full_w - 40)

        card_left_x = 0
        card_max_w = max(180, paper_w - 32)

        y = paper_y + top_pad

        layouts = []
        for seed in seeds:
            layout = self._measure_seed_card_layout(seed, card_max_w)
            layout["x"] = card_left_x
            layout["y"] = y
            layouts.append(layout)
            y += layout["h"] + row_gap

        content_h = y - row_gap + bottom_pad
        paper_h = max(120, content_h - paper_y + 10)

        self._draw_tiled_lined_paper(
            canvas=canvas,
            x=paper_x,
            y=paper_y,
            w=paper_w,
            h=paper_h
        )

        # 关键：在 lined paper 画完后、cards 画之前画 tape
        # 这样 tape 下半部分压在 lined paper 上，
        # 上半部分又仍然压着上面的虚线
        self.draw_tape_image(
            canvas=canvas,
            img_path=tape1_path,
            x=tape_x,
            y=tape_y,
            width=tape_w,
            angle=-8,
            alpha=0.8,
            anchor="nw",
            tag="seed_tape"
        )

        for layout in layouts:
            self._draw_one_seed_card(canvas, layout)

        canvas.config(height=paper_y + paper_h + 16)

    def _measure_seed_card_layout(self, seed, max_w):
        base_w = self.seed_card_base_width
        font_name = ("Microsoft YaHei UI", 14)
        text_font = tkfont.Font(font=font_name)

        text = seed["name"]

        left_inner_padding = 24
        right_inner_padding = 24
        outer_extra = 24

        if self.is_edit_mode:
            right_widget_w = 42
            gap_w = 10
        else:
            right_widget_w = 20
            gap_w = 0

        text_pixel_w = text_font.measure(text)

        natural_w = (
            left_inner_padding
            + text_pixel_w
            + gap_w
            + right_widget_w
            + right_inner_padding
            + outer_extra
        )

        preferred_w = max(base_w, natural_w)

        if preferred_w <= max_w:
            card_w = preferred_w
            text_wrap_w = 0
        else:
            card_w = max_w
            text_wrap_w = max(
                120,
                card_w - (
                    left_inner_padding
                    + right_inner_padding
                    + outer_extra
                    + gap_w
                    + right_widget_w
                )
            )

        if text_wrap_w > 0:
            text_lines = self._wrap_text_by_pixels(text, text_font, text_wrap_w)
        else:
            text_lines = [text]

        line_h = max(22, text_font.metrics("linespace"))
        text_h = len(text_lines) * line_h

        card_h = max(64, text_h + 24)

        return {
            "seed": seed,
            "text": text,
            "lines": text_lines,
            "font": font_name,
            "line_h": line_h,
            "w": card_w,
            "h": card_h,
            "text_wrap_w": text_wrap_w,
            "right_widget_w": right_widget_w,
        }

    def _wrap_text_by_pixels(self, text, font, max_width):
        if font.measure(text) <= max_width:
            return [text]

        lines = []
        current = ""

        for ch in text:
            test = current + ch
            if font.measure(test) <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = ch

        if current:
            lines.append(current)

        return lines

    def _draw_tiled_lined_paper(self, canvas, x, y, w, h):
        pil_img = self.seed_texture_pil.copy()

        orig_w, orig_h = pil_img.size
        scale = 1.2
        tile_w = max(1, int(orig_w * scale))
        tile_h = max(1, int(orig_h * scale))
        pil_img = pil_img.resize((tile_w, tile_h), Image.LANCZOS)

        tiled = Image.new("RGBA", (w, h), (255, 255, 255, 0))
        for px in range(0, w, tile_w):
            for py in range(0, h, tile_h):
                tiled.paste(pil_img, (px, py))

        alpha = tiled.getchannel("A")
        alpha = alpha.point(lambda p: int(p * 0.30))
        tiled.putalpha(alpha)

        tk_img = ImageTk.PhotoImage(tiled)
        self.bg_imgs.append(tk_img)

        canvas.create_image(
            x, y,
            image=tk_img,
            anchor="nw"
        )

    def _draw_one_seed_card(self, canvas, layout):
        seed = layout["seed"]
        x = layout["x"]
        y = layout["y"]
        w = layout["w"]
        h = layout["h"]

        self.round_rect(
            canvas,
            x + 4, y + 4, x + w - 4, y + h - 4,
            25,
            fill=self.colors["card_shadow"],
            outline=""
        )

        self.round_rect(
            canvas,
            x + 4, y + 2, x + w - 4, y + h - 6,
            25,
            fill=self.colors["seed_bg"],
            outline=self.colors["seed_border"],
            width=1
        )

        self.round_rect(
            canvas,
            x + 8, y + 7, x + w - 8, y + h - 11,
            15,
            fill="",
            outline=self.colors["dash_border"],
            width=1,
            dash=(2, 2)
        )

        noise_img = self.make_noise_overlay_image(
            max(1, w - 8),
            max(1, h - 10),
            opacity=0.16,
            strength=100
        )
        canvas.create_image(
            x + 4, y + 2,
            image=noise_img,
            anchor="nw"
        )

        text_x = x + 24
        text_y = y + h / 2
        canvas.create_text(
            text_x,
            text_y,
            text="\n".join(layout["lines"]),
            anchor="w",
            justify="left",
            font=layout["font"],
            fill=self.colors["title"],
            width=layout["text_wrap_w"] if layout["text_wrap_w"] > 0 else 0
        )

        if self.is_edit_mode:
            btn_w = 24
            btn_h = 24
            btn_x2 = x + w - 22
            btn_x1 = btn_x2 - btn_w
            btn_y1 = y + (h - btn_h) / 2
            btn_y2 = btn_y1 + btn_h

            btn_tag = f"delete_seed_{id(seed)}"

            self.round_rect(
                canvas,
                btn_x1, btn_y1, btn_x2, btn_y2,
                8,
                fill=self.colors["delete_bg"],
                outline=self.colors["delete_border"],
                width=1,
                tags=(btn_tag,)
            )
            canvas.create_text(
                (btn_x1 + btn_x2) / 2,
                (btn_y1 + btn_y2) / 2 - 1,
                text="✕",
                font=("Microsoft YaHei UI", 11, "bold"),
                fill=self.colors["delete_fg"],
                tags=(btn_tag,)
            )
            canvas.tag_bind(
                btn_tag,
                "<Button-1>",
                lambda e, s=seed: self.delete_seed(s)
            )

    # =========================
    # 12. 底部按钮
    # =========================
    def render_bottom(self, parent):
        bottom = tk.Frame(parent, bg=self.colors["panel_bg"])
        bottom.pack(fill="x")

        btn_wrap = tk.Frame(bottom, bg=self.colors["panel_bg"])
        btn_wrap.pack(side="right")

        cancel_btn = self.make_canvas_action_btn(
            btn_wrap,
            text="取消",
            command=self.handle_cancel,
            width=112,
            height=48,
            fill=self.colors["btn_bg"],
            border=self.colors["btn_border"],
            text_color=self.colors["btn_fg"]
        )
        cancel_btn.pack(side="right")

        save_btn = self.make_canvas_action_btn(
            btn_wrap,
            text="保存",
            command=self.handle_save,
            width=112,
            height=48,
            fill=self.colors["btn_bg"],
            border=self.colors["btn_border"],
            text_color=self.colors["btn_fg"]
        )
        save_btn.pack(side="right", padx=(0, 10))

        if len(self.nav_stack) > 1:
            back_btn = self.make_canvas_action_btn(
                btn_wrap,
                text="Back",
                command=self.go_back_category,
                width=112,
                height=48,
                fill=self.colors["btn_bg"],
                border=self.colors["btn_border"],
                text_color=self.colors["btn_fg"]
            )
            back_btn.pack(side="right", padx=(0, 10))

    # =========================
    # 13. Edit 模式切换
    # =========================
    def toggle_edit_mode(self):
        self.is_edit_mode = not self.is_edit_mode
        self.render_all()

    # =========================
    # 14. Add 菜单
    # =========================
    def handle_add_menu(self):
        dialog=ConfigureDialogAdd(self)

    def open_category_config(self, section):
        self.normalize_section(section)
        self.current_data = section
        self.nav_stack.append((section["name"], section))
        self.is_edit_mode = False
        self.render_all()

    def handle_add_category_save(self, category_title, icon_path):
        next_order = len(self.current_data["sections"])
        self.current_data["sections"].append({
            "section_id": None,
            "name": category_title,
            "sort_order": next_order,
            "icon_path": icon_path,
            "is_configured": False,
            "sections": [],
            "seeds": []
        })
        self.render_all()


    def handle_add_seed(self):
        name = self.ask_text("Add Seed / Step", "请输入 seed / step 名称：")
        if not name:
            return

        next_order = len(self.current_data["seeds"])
        self.current_data["seeds"].append({
            "seed_id": None,
            "section_id": None,
            "name": name,
            "sort_order": next_order,
            "icon": "☐"
        })

        # 只刷新 seed 区，避免整个页面重建导致“卡一下”
        if hasattr(self, "seed_list_canvas") and self.seed_list_canvas.winfo_exists():
            self.redraw_seed_list_canvas()
            self._on_content_configure(None)
        else:
            self.render_all()

    def delete_section(self, section):
        self.data["sections"] = [s for s in self.data["sections"] if s is not section]
        for i, sec in enumerate(self.data["sections"]):
            sec["sort_order"] = i
        self.render_all()

    def delete_seed(self, seed):
        self.data["seeds"] = [s for s in self.data["seeds"] if s is not seed]
        for i, item in enumerate(self.data["seeds"]):
            item["sort_order"] = i

        if hasattr(self, "seed_list_canvas") and self.seed_list_canvas.winfo_exists():
            self.redraw_seed_list_canvas()
            self._on_content_configure(None)
        else:
            self.render_all()

    # =========================
    # 17. 保存 / 取消
    # =========================
    def handle_cancel(self):
        self.destroy()

    def handle_save(self):
        self.current_data["is_configured"] = True

        if len(self.nav_stack) > 1:
            self.go_back_category()
            return

        if self.on_save:
            self.on_save(self.parent,self.direction_title,self.data)
        self.destroy()

    def make_round_delete_btn(self, parent, x, y, command,
                              size=34,
                              fill="#f7f1ea",
                              outline="#7a5c49",
                              text_color="#7a5c49"):
        btn_canvas = tk.Canvas(
            parent,
            width=size,
            height=size,
            bg=parent["bg"],
            highlightthickness=0,
            bd=0
        )
        btn_canvas.place(x=x, y=y)

        pad = 2
        btn_canvas.create_oval(
            pad, pad, size - pad, size - pad,
            fill=fill,
            outline=outline,
            width=1.2,
            tags="circle"
        )

        btn_canvas.create_text(
            size / 2, size / 2 - 1,
            text="−",
            font=("Microsoft YaHei UI", 16, "bold"),
            fill=text_color,
            tags="minus"
        )

        btn_canvas.bind("<Button-1>", lambda e: command())
        btn_canvas.tag_bind("circle", "<Button-1>", lambda e: command())
        btn_canvas.tag_bind("minus", "<Button-1>", lambda e: command())

        return btn_canvas

    def draw_tape_image(
            self,
            canvas,
            img_path,
            x,
            y,
            width=None,
            angle=0,
            alpha=1.0,
            anchor="nw",
            tag="panel_tape"
    ):
        img_path = Path(img_path)
        if not img_path.exists():
            return

        pil_img = Image.open(img_path).convert("RGBA")

        if width is not None:
            scale = width / pil_img.width
            new_h = int(pil_img.height * scale)
            pil_img = pil_img.resize((int(width), new_h), Image.LANCZOS)

        if angle != 0:
            pil_img = pil_img.rotate(angle, expand=True, resample=Image.BICUBIC)

        if alpha < 1.0:
            a = pil_img.getchannel("A")
            a = a.point(lambda p: int(p * alpha))
            pil_img.putalpha(a)

        tk_img = ImageTk.PhotoImage(pil_img)
        self.tape_imgs.append(tk_img)

        canvas.create_image(
            x, y,
            image=tk_img,
            anchor=anchor,
            tags=(tag,)
        )

    def load_rotated_tape(self, img_path, width=None, angle=0, alpha=1.0):
        img_path = Path(img_path)
        if not img_path.exists():
            return None

        pil_img = Image.open(img_path).convert("RGBA")

        if width is not None:
            scale = width / pil_img.width
            new_h = int(pil_img.height * scale)
            pil_img = pil_img.resize((int(width), new_h), Image.LANCZOS)

        if angle != 0:
            pil_img = pil_img.rotate(angle, expand=True, resample=Image.BICUBIC)

        if alpha < 1.0:
            a = pil_img.getchannel("A")
            a = a.point(lambda p: int(p * alpha))
            pil_img.putalpha(a)

        tk_img = ImageTk.PhotoImage(pil_img)
        self.tape_imgs.append(tk_img)
        return tk_img
