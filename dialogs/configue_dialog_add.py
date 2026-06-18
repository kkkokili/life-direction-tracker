import tkinter as tk
from dialogs.configue_dialog_add_category import ConfigureDialogAddCategory

class ConfigureDialogAdd(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.title("Add")
        self.configure(bg="#f7f3ee")
        self.resizable(False, False)
        self.transient(self.parent)
        self.grab_set()

        self.center_to_parent()
        self.build_ui()



    def center_to_parent(self):
        w, h = 270, 165

        self.parent.update_idletasks()

        x = self.parent.winfo_rootx() + (self.parent.winfo_width() - w) // 2
        y = self.parent.winfo_rooty() + (self.parent.winfo_height() - h) // 2

        self.geometry(f"{w}x{h}+{x}+{y}")

    def build_ui(self):
        wrap = tk.Frame(self, bg="#f7f3ee")
        wrap.pack(fill="both", expand=True, padx=18, pady=18)

        title = tk.Label(
            wrap,
            text="要添加什么？",
            font=("Microsoft YaHei UI", 12, "bold"),
            fg="#5b473c",
            bg="#f7f3ee"
        )
        title.pack(anchor="w", pady=(0, 12))

        btn1 = tk.Button(
            wrap,
            text="＋ Add Category",
            font=("Microsoft YaHei UI", 11),
            fg="#6d5b52",
            bg="#f1e8e0",
            activebackground="#e9ddd2",
            activeforeground="#6d5b52",
            relief="solid",
            bd=1,
            highlightthickness=0,
            padx=12,
            pady=6,
            command=self.handle_add_category
        )
        btn1.pack(fill="x", pady=(0, 8))

        btn2 = tk.Button(
            wrap,
            text="＋ Add Seed / Step",
            font=("Microsoft YaHei UI", 11),
            fg="#6d5b52",
            bg="#f1e8e0",
            activebackground="#e9ddd2",
            activeforeground="#6d5b52",
            relief="solid",
            bd=1,
            highlightthickness=0,
            padx=12,
            pady=6,
            command=self.handle_add_seed
        )
        btn2.pack(fill="x")

    def handle_add_category(self):
        parent = self.parent
        self.destroy()
        dialog = ConfigureDialogAddCategory(
            parent,
            on_save=parent.handle_add_category_save
        )
        dialog.after(10, dialog.load_emojis)

    def handle_add_seed(self):
        print("seed")










