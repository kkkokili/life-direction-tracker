import tkinter as tk
from services.emoji_service import load_emojis,build_emoji_picker

class ConfigureDialogAddCategory(tk.Toplevel):
    def __init__(self, grandparent,on_save=None):
        super().__init__(grandparent)
        self.grandparent = grandparent

        # ===== 保存回调 =====
        self.on_save = on_save

        self.title("Add Category")
        self.configure(bg="#f7f3ee")
        self.resizable(False, False)
        self.transient(grandparent)
        self.grab_set()

        self.result = {"value": None}

        # ===== emoji 数据与状态 =====
        self.load_emojis = lambda: load_emojis(self)
        self.build_emoji_picker = lambda: build_emoji_picker(self)
        self.selected_icon_path = None

        self.emoji_files = []
        self.emoji_photos = []  # 保存 PhotoImage 引用，防止图片消失
        self.emoji_item_map = {}  # {canvas_item_id: icon_path}
        self.emoji_bg_map = {}  # {icon_path: bg_rect_id}
        self.emoji_img_map = {}  # {icon_path: image_item_id}

        # ===== emoji分批加载控制 =====
        self.load_index = 0

        # ===== emoji加载时页面的规格，根据这个来选择emoji_size, title_size, emoji_cols =====
        self.emoji_preset = "small"

        self.center_to_parent()
        self.build_category_name_input()
        self.build_emoji_title()
        self.build_bottom_buttons()
        self.build_emoji_picker()




    def center_to_parent(self):
        w, h = 420,520

        self.grandparent.update_idletasks()

        x = self.grandparent.winfo_rootx() + (self.grandparent.winfo_width() - w) // 2
        y = self.grandparent.winfo_rooty() + (self.grandparent.winfo_height() - h) // 2

        self.geometry(f"{w}x{h}+{x}+{y}")


    # =========================
    # 3. 中间标题
    # =========================
    def build_emoji_title(self):
        title_wrap = tk.Frame(self, bg="#f7f3ee")
        title_wrap.pack(fill="x", padx=40, pady=(12, 14))

        left_line = tk.Frame(title_wrap, bg="#e3d9d1", height=2)
        left_line.pack(side="left", fill="x", expand=True, padx=(0, 18), pady=18)

        title_label = tk.Label(
            title_wrap,
            text="Select Emoji",
            font=("Microsoft YaHei UI", 10, "bold"),
            fg="#2f2a28",
            bg="#f7f3ee"
        )
        title_label.pack(side="left")

        right_line = tk.Frame(title_wrap, bg="#e3d9d1", height=2)
        right_line.pack(side="left", fill="x", expand=True, padx=(18, 0), pady=18)

    def build_category_name_input(self):
        wrapper = tk.Frame(self, bg="#f7f3ee")
        wrapper.pack(fill="both", padx=16, pady=16)

        tk.Label(
            wrapper,
            text="请输入 category 名称：",
            font=("Microsoft YaHei UI", 11),
            fg="#5b473c",
            bg="#f7f3ee"
        ).pack(anchor="w", pady=(0, 10))

        self.category_name_entry = tk.Entry(
            wrapper,
            font=("Microsoft YaHei UI", 11),
            fg="#4f3f37",
            bg="white",
            relief="solid",
            bd=1,
            highlightthickness=1,
            highlightbackground="#ddd2c8",
            highlightcolor="#ddd2c8"
        )
        self.category_name_entry.pack(fill="x", ipady=6)
        self.category_name_entry.focus_set()

        btn_row = tk.Frame(wrapper, bg="#f7f3ee")
        btn_row.pack(fill="x", pady=(14, 0))


    # =========================
    # 12. 底部按钮
    # =========================
    def build_bottom_buttons(self):
        bottom = tk.Frame(self, bg="#f7f3ee")
        bottom.pack(side="bottom", fill="x", padx=38, pady=(0, 28))

        cancel_btn = tk.Button(
            bottom,
            text="取消",
            font=("Microsoft YaHei UI", 12),
            fg="#2f2a28",
            bg="#f7f3ef",
            activebackground="#f1eae4",
            activeforeground="#2f2a28",
            relief="solid",
            bd=1,
            highlightthickness=1,
            highlightbackground="#e1d7cf",
            cursor="hand2",
            command=self.destroy
        )
        cancel_btn.pack(side="right", ipadx=18, ipady=8, padx=(0, 26))

        save_btn = tk.Button(
            bottom,
            text="保存",
            font=("Microsoft YaHei UI", 12),
            fg="white",
            bg="#e69154",
            activebackground="#d98245",
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.handle_save
        )
        save_btn.pack(side="right", ipadx=18, ipady=9)

    # =========================
    # 13. 保存
    # =========================
    def handle_save(self):
        category_title= self.category_name_entry.get().strip()

        if not category_title:
            self.category_name_entry.focus_set()
            return

        if not self.selected_icon_path:
            return

        if self.on_save:
            self.on_save(category_title, self.selected_icon_path)

        self.destroy()
