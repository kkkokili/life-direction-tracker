import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
from dialogs.configue_dialog_add_category import ConfigureDialogAddCategory
from dialogs.configue_dialog_add_seeds import ConfigureDialogAddSeeds

class ConfigureDialogAdd(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.title("Add")
        self.configure(bg="#fbf8f4")
        self.resizable(False, False)
        self.transient(self.parent)
        self.grab_set()
        self.button_canvases = []
        self.texture_imgs = []

        self.center_to_parent()
        self.build_ui()



    def center_to_parent(self):
        w, h = 300, 180

        self.parent.update_idletasks()

        x = self.parent.winfo_rootx() + (self.parent.winfo_width() - w) // 2
        y = self.parent.winfo_rooty() + (self.parent.winfo_height() - h) // 2

        self.geometry(f"{w}x{h}+{x}+{y}")

    def build_ui(self):
        wrap = tk.Frame(self, bg="#fbf8f4")
        wrap.pack(fill="both", expand=True, padx=18, pady=18)

        title = tk.Label(
            wrap,
            text="要添加什么？",
            font=("Microsoft YaHei UI", 12, "bold"),
            fg="#5b473c",
            bg="#fbf8f4"
        )
        title.pack(anchor="w", pady=(0, 12))

        self.create_soft_button(
            wrap,
            text="+ Add Category",
            command=self.handle_add_category
        ).pack(fill="x", pady=(0, 10))

        self.create_soft_button(
            wrap,
            text="+ Add Seed / Step",
            command=self.handle_add_seed
        ).pack(fill="x")

    def create_soft_button(self, parent, text, command):
        canvas = tk.Canvas(
            parent,
            height=48,
            bg="#fbf8f4",
            highlightthickness=0,
            bd=0,
            relief="flat",
            cursor="hand2"
        )
        self.button_canvases.append(canvas)

        def draw():
            canvas.delete("all")
            width = max(canvas.winfo_width(), 1)

            self.round_rect(
                canvas,
                7, 5, width - 1, 45,
                radius=16,
                fill="#e8dcca",
                outline=""
            )

            self.round_rect(
                canvas,
                4, 2, width - 4, 42,
                radius=16,
                fill="#FFFDF6",
                outline="#dbc07a",
                width=1
            )

            self.round_rect(
                canvas,
                6, 5, width - 6, 39,
                radius=12,
                fill="",
                outline="#e3b387",
                dash=(2, 2),
                width=1
            )

            noise_img = self.make_noise_overlay_image(width - 8, 40, opacity=0.30, strength=120)
            canvas.create_image(4, 2, image=noise_img, anchor="nw")

            canvas.create_text(
                width / 2,
                23,
                text=text,
                font=("Microsoft YaHei UI", 11, "bold"),
                fill="#8b6348"
            )

        canvas.bind("<Configure>", lambda event: draw())
        canvas.bind("<Button-1>", lambda event: command())
        return canvas

    def make_noise_overlay_image(self, width, height, opacity=0.16, strength=100):
        width = max(1, int(width))
        height = max(1, int(height))

        img = Image.new("RGBA", (width, height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)

        step = max(1, int(35 / max(1, strength)))
        light_alpha = max(16, min(120, int(255 * opacity)))
        warm_alpha = max(12, min(72, int(255 * opacity * 0.72)))

        for y in range(0, height, step):
            for x in range(0, width, step):
                px = min(width - 1, x + ((x * 17 + y * 31) % step))
                py = min(height - 1, y + ((x * 29 + y * 13) % step))

                if (x // step + y // step) % 2 == 0:
                    draw.point((px, py), fill=(255, 255, 255, light_alpha))
                else:
                    draw.point((px, py), fill=(209, 167, 112, warm_alpha))

                if (x * 5 + y * 7) % (step * 6) == 0:
                    px2 = min(width - 1, x + ((x * 11 + y * 19) % step))
                    py2 = min(height - 1, y + ((x * 23 + y * 3) % step))
                    draw.point((px2, py2), fill=(255, 255, 255, max(8, light_alpha // 2)))

        tk_img = ImageTk.PhotoImage(img)
        self.texture_imgs.append(tk_img)
        return tk_img

    def round_rect(self, canvas, x1, y1, x2, y2, radius=8, **kwargs):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
        ]
        return canvas.create_polygon(points, smooth=True, splinesteps=16, **kwargs)

    def handle_add_category(self):
        parent = self.parent
        self.destroy()
        dialog = ConfigureDialogAddCategory(
            parent,
            on_save=parent.handle_add_category_save
        )
        dialog.after(10, dialog.load_emojis)

    def handle_add_seed(self):
        parent = self.parent
        self.grab_release()
        self.withdraw()
        self.update_idletasks()
        ConfigureDialogAddSeeds(
            parent,
            on_save=parent.handle_add_seed_save
        )
        self.destroy()










