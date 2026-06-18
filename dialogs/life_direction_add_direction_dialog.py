# pages/add_direction_dialog.py

import tkinter as tk
from PIL import Image, ImageTk, ImageOps
from services.emoji_service import load_emojis,build_emoji_picker
from config.theme import (BG_MAIN)


class AddDirectionDialog(tk.Toplevel):
    """
    功能：
    1. 弹出 Add Direction 小窗口
    2. 让用户输入方向名称
    3. 从 img/emoji 文件夹读取所有 png 图片
    4. 用户点击某张图片后，记录被选中的图片
    5. 点击保存时，把 title 和 icon_path 回传给父页面
    6. emoji 区域使用纯 Canvas 绘制，避免滚动时图片切片
    7. 分批加载 emoji，减少弹窗初次打开卡顿
    """

    def __init__(self, parent, on_save=None):
        super().__init__(parent)
        # ===== 保存回调 =====
        self.on_save = on_save

        # ===== 弹窗基础设置 =====
        self.title("Add Direction")
        self.geometry("600x460")
        self.resizable(False, False)
        self.configure(bg=BG_MAIN)

        # ===== 模态弹窗 =====
        self.transient(parent.winfo_toplevel())#让这个 Toplevel 依附于那个主窗口
        self.grab_set()#在这个弹窗没关掉之前，用户只能先操作这个弹窗，不能去点后面的主窗口。
        self.center_to_parent(parent)

        # ===== emoji 数据与状态 =====
        self.load_emojis = lambda: load_emojis(self)
        self.build_emoji_picker = lambda: build_emoji_picker(self)
        self.selected_icon_path = None

        self.emoji_files = []
        self.emoji_photos = []          # 保存 PhotoImage 引用，防止图片消失
        self.emoji_item_map = {}        # {canvas_item_id: icon_path}
        self.emoji_bg_map = {}          # {icon_path: bg_rect_id}
        self.emoji_img_map = {}         # {icon_path: image_item_id}

        # ===== emoji分批加载控制 =====
        self.load_index = 0

        # ===== emoji加载时页面的规格，根据这个来选择emoji_size, title_size, emoji_cols =====
        self.emoji_preset = "large"

        # ===== 构建界面 =====
        self.build_name_input()
        self.build_emoji_title()
        self.build_bottom_buttons()
        self.build_emoji_picker()


    def center_to_parent(self, parent):
        # 先让 tkinter 把窗口尺寸算出来
        self.update_idletasks()

        dialog_w = self.winfo_width()
        dialog_h = self.winfo_height()

        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()

        x = parent_x + (parent_w - dialog_w) // 2
        y = parent_y + (parent_h - dialog_h) // 2

        self.geometry(f"{dialog_w}x{dialog_h}+{x}+{y}")



    # =========================
    # 2. 名称输入
    # =========================
    def build_name_input(self):
        wrapper = tk.Frame(self, bg=BG_MAIN)
        wrapper.pack(fill="x", padx=38, pady=(2, 10))

        label = tk.Label(
            wrapper,
            text="Direction Name:",
            font=("Microsoft YaHei UI", 10, "bold"),
            fg="#2f2a28",
            bg=BG_MAIN
        )
        label.pack(anchor="w", pady=(0, 12))

        self.name_entry = tk.Entry(
            wrapper,
            font=("Microsoft YaHei UI",9),
            fg="#2f2a28",
            bg="white",
            relief="solid",
            bd=0,
            highlightthickness=1,
            highlightbackground="#e1d7cf",
            highlightcolor="#e1d7cf"
        )
        self.name_entry.pack(fill="x", ipady=10)
        self.name_entry.focus_set()




    # =========================
    # 3. 中间标题
    # =========================
    def build_emoji_title(self):
        title_wrap = tk.Frame(self, bg=BG_MAIN)
        title_wrap.pack(fill="x", padx=40, pady=(12, 14))

        left_line = tk.Frame(title_wrap, bg="#e3d9d1", height=2)
        left_line.pack(side="left", fill="x", expand=True, padx=(0, 18), pady=18)

        title_label = tk.Label(
            title_wrap,
            text="Select Emoji",
            font=("Microsoft YaHei UI", 10, "bold"),
            fg="#2f2a28",
            bg=BG_MAIN
        )
        title_label.pack(side="left")

        right_line = tk.Frame(title_wrap, bg="#e3d9d1", height=2)
        right_line.pack(side="left", fill="x", expand=True, padx=(18, 0), pady=18)

    # =========================
    # 12. 底部按钮
    # =========================
    def build_bottom_buttons(self):
        bottom = tk.Frame(self, bg=BG_MAIN)
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
        cancel_btn.pack(side="right", ipadx=18, ipady=8, padx=(0, 16))

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
        title = self.name_entry.get().strip()

        if not title:
            self.name_entry.focus_set()
            return

        if not self.selected_icon_path:
            return

        if self.on_save:
            self.on_save(title, self.selected_icon_path)

        self.destroy()
