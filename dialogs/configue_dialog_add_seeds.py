import tkinter as tk
import calendar
from copy import deepcopy
from datetime import date
from pathlib import Path

from PIL import Image, ImageOps, ImageTk


class ConfigureDialogAddSeeds(tk.Toplevel):
    def __init__(self, parent, on_save=None, initial_data=None):
        super().__init__(parent)
        self.withdraw()
        self.parent = parent
        self.on_save = on_save
        self.initial_data = initial_data or {}
        self.mode = tk.StringVar(value=self.initial_data.get("mode", "seed"))
        self.item_name_entry = None
        self.item_name_placeholder = "例如：学习 Python 入门"
        default_resources = [
            {"type": "video", "name": "Python入门课程", "meta": "来自 B站", "selected": True},
            {"type": "book", "name": "《Python编程从入门到精通》", "meta": "", "selected": False},
            {"type": "document", "name": "Python官方文档", "meta": "", "selected": False},
        ]
        self.resources = deepcopy(
            self.initial_data["resources"]
            if "resources" in self.initial_data
            else default_resources
        )
        self.resource_list_frame = None
        self.resource_list_canvas = None
        self.resource_list_window = None
        self.resource_icon_imgs = []
        emoji_dir = Path(__file__).resolve().parent.parent / "img" / "emoji"
        self.resource_icon_paths = {
            "online_course": emoji_dir / "1f4bb.png",
            "school_course": emoji_dir / "graduation.png",
        }

        self.title("配置学习资源")
        self.configure(bg="#fbf7f5")
        self.resizable(False, False)
        self.transient(parent)

        self.center_to_parent()
        self.deiconify()
        self.lift()
        self.update()
        self.build_ui()
        self.update_idletasks()
        self.grab_set()

    def center_to_parent(self):
        self.set_window_size(680, 580)

    def set_window_size(self, w, h):
        self.parent.update_idletasks()

        x = self.parent.winfo_rootx() + (self.parent.winfo_width() - w) // 2
        y = self.parent.winfo_rooty() + (self.parent.winfo_height() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def clear_ui(self):
        self.close_date_picker_popup()
        for child in self.winfo_children():
            child.destroy()

    def close_date_picker_popup(self):
        popup = getattr(self, "date_picker_popup", None)
        if popup and popup.winfo_exists():
            popup.destroy()
        self.date_picker_popup = None

    def show_resource_step(self):
        self.close_date_picker_popup()
        self.clear_ui()
        self.title("配置学习资源")
        self.configure(bg="#fbf7f5")
        self.set_window_size(680, 580)
        self.build_ui()

    def prepare_step_window(self, title, width, height):
        self.clear_ui()
        self.title(title)
        self.configure(bg="#fbf7f5")
        self.set_window_size(width, height)

    def build_ui(self):
        self.build_header()
        self.build_mode_tabs()
        self.build_item_name_input()
        self.build_description()
        self.build_bottom_buttons()
        self.build_resource_panel()

    def build_header(self):
        header = tk.Frame(self, bg="#fbf7f5", height=54)
        header.pack(fill="x")
        header.pack_propagate(False)

        title = tk.Label(
            header,
            text="配置学习资源",
            font=("Microsoft YaHei UI", 16, "bold"),
            fg="#4b382f",
            bg="#fbf7f5"
        )
        title.place(relx=0.5, rely=0.5, anchor="center")


        line = tk.Frame(self, bg="#eadfd7", height=1)
        line.pack(fill="x")

    def build_mode_tabs(self):
        tabs = tk.Frame(self, bg="#eadfd7")
        tabs.pack(anchor="center", pady=(14, 18))

        self.seed_btn = self.make_tab_button(tabs, "种子 (Seed)", "seed")
        self.seed_btn.pack(side="left", padx=(1, 0), pady=1)

        self.step_btn = self.make_tab_button(tabs, "步骤 (Step Action)", "step")
        self.step_btn.pack(side="left", padx=(0, 1), pady=1)

        self.refresh_tabs()

    def make_tab_button(self, parent, text, value):
        return tk.Button(
            parent,
            text=text,
            font=("Microsoft YaHei UI", 12, "bold"),
            fg="#6d5b52",
            relief="flat",
            bd=0,
            padx=28,
            pady=7,
            cursor="hand2",
            takefocus=0,
            highlightthickness=0,
            command=lambda: self.select_mode(value)
        )

    def select_mode(self, value):
        self.mode.set(value)
        self.refresh_tabs()

    def refresh_tabs(self):
        for value, btn in (("seed", self.seed_btn), ("step", self.step_btn)):
            selected = self.mode.get() == value
            btn.configure(
                bg="#f1e4dc" if selected else "#fbf7f5",
                activebackground="#ead8ce" if selected else "#f5eee9"
            )

    def build_item_name_input(self):
        wrap = tk.Frame(self, bg="#fbf7f5")
        wrap.pack(fill="x", padx=46, pady=(0, 14))

        label = tk.Label(
            wrap,
            text="事项名称",
            font=("Microsoft YaHei UI", 10, "bold"),
            fg="#6d5b52",
            bg="#fbf7f5"
        )
        label.pack(anchor="w", pady=(0, 7))

        entry_box = tk.Frame(wrap, bg="#e1d7cf")
        entry_box.pack(fill="x")

        self.item_name_entry = tk.Entry(
            entry_box,
            font=("Microsoft YaHei UI", 11),
            fg="#9b8a80",
            bg="white",
            relief="flat",
            bd=0,
            highlightthickness=0,
            insertbackground="#5c4335"
        )
        self.item_name_entry.pack(fill="x", padx=1, pady=1, ipady=9)
        initial_name = self.initial_data.get("name", "").strip()
        if initial_name:
            self.item_name_entry.insert(0, initial_name)
            self.item_name_entry.configure(fg="#4f3f37")
        else:
            self.item_name_entry.insert(0, self.item_name_placeholder)
        self.item_name_entry.bind("<FocusIn>", self.clear_item_name_placeholder)
        self.item_name_entry.bind("<FocusOut>", self.restore_item_name_placeholder)

    def clear_item_name_placeholder(self, event=None):
        if self.item_name_entry.get() == self.item_name_placeholder:
            self.item_name_entry.delete(0, tk.END)
            self.item_name_entry.configure(fg="#4f3f37")

    def restore_item_name_placeholder(self, event=None):
        if not self.item_name_entry.get().strip():
            self.item_name_entry.insert(0, self.item_name_placeholder)
            self.item_name_entry.configure(fg="#9b8a80")

    def get_item_name(self):
        value = self.item_name_entry.get().strip()
        if value == self.item_name_placeholder:
            return ""
        return value

    def build_description(self):
        desc = tk.Label(
            self,
            text="可长期重复使用的重构资源",
            font=("Microsoft YaHei UI", 11),
            fg="#7a5f50",
            bg="#fbf7f5"
        )
        desc.pack(anchor="w", padx=46, pady=(0, 16))

    def build_resource_panel(self):
        panel = tk.Frame(
            self,
            bg="#fffdfb",
            highlightthickness=1,
            highlightbackground="#eadfd7"
        )
        panel.pack(fill="x", padx=46, pady=(0, 8))

        title = tk.Label(
            panel,
            text="学习资源:",
            font=("Microsoft YaHei UI", 12, "bold"),
            fg="#5b473c",
            bg="#fffdfb"
        )
        title.pack(anchor="w", padx=16, pady=(14, 12))

        list_wrap = tk.Frame(panel, bg="#fffdfb", height=132)
        list_wrap.pack(fill="x", padx=16)
        list_wrap.pack_propagate(False)

        self.resource_list_canvas = tk.Canvas(
            list_wrap,
            bg="#fffdfb",
            bd=0,
            highlightthickness=0,
            yscrollincrement=24
        )
        self.resource_list_canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(
            list_wrap,
            orient="vertical",
            command=self.resource_list_canvas.yview
        )
        scrollbar.pack(side="right", fill="y")

        self.resource_list_canvas.configure(yscrollcommand=scrollbar.set)
        self.resource_list_frame = tk.Frame(self.resource_list_canvas, bg="#fffdfb")
        self.resource_list_window = self.resource_list_canvas.create_window(
            0,
            0,
            window=self.resource_list_frame,
            anchor="nw"
        )
        self.resource_list_frame.bind("<Configure>", self.update_resource_scrollregion)
        self.resource_list_canvas.bind("<Configure>", self.resize_resource_list_window)
        self.resource_list_canvas.bind("<Enter>", self.bind_resource_mousewheel)
        self.resource_list_canvas.bind("<Leave>", self.unbind_resource_mousewheel)
        self.render_resource_rows()

        add_btn = tk.Button(
            panel,
            text="＋  添加新资源",
            font=("Microsoft YaHei UI", 12),
            fg="#a76f4e",
            bg="#fff8f3",
            activebackground="#f8ece4",
            activeforeground="#7a4f35",
            relief="flat",
            bd=0,
            padx=16,
            pady=9,
            anchor="w",
            cursor="hand2",
            takefocus=0,
            highlightthickness=1,
            highlightbackground="#ead8ce",
            highlightcolor="#e5b98f",
            default="disabled",
            command=self.open_add_resource_dialog
        )
        add_btn.pack(fill="x", padx=16, pady=(8, 14))

    def update_resource_scrollregion(self, event=None):
        self.resource_list_canvas.configure(
            scrollregion=self.resource_list_canvas.bbox("all")
        )

    def resize_resource_list_window(self, event):
        self.resource_list_canvas.itemconfig(
            self.resource_list_window,
            width=event.width
        )

    def bind_resource_mousewheel(self, event=None):
        self.resource_list_canvas.bind_all("<MouseWheel>", self.on_resource_mousewheel)

    def unbind_resource_mousewheel(self, event=None):
        self.resource_list_canvas.unbind_all("<MouseWheel>")

    def on_resource_mousewheel(self, event):
        self.resource_list_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def get_resource_icon(self, resource_type):
        icons = {
            "video": ("▶", "#db8a52", 12),
            "book": ("📖", "#db8a52", 13),
            "document": ("▤", "#5ea6bc", 12),
        }
        return icons.get(resource_type, ("•", "#db8a52", 12))

    def load_resource_icon_image(self, resource_type):
        icon_path = self.resource_icon_paths.get(resource_type)
        if not icon_path or not icon_path.exists():
            return None

        icon_sizes = {
            "online_course": 18,
            "school_course": 20,
        }
        size = icon_sizes.get(resource_type, 20)

        img = Image.open(icon_path).convert("RGBA")
        alpha = img.getchannel("A")
        bbox = alpha.getbbox()
        if bbox:
            img = img.crop(bbox)

        img = ImageOps.contain(img, (size, size), Image.LANCZOS)
        tk_img = ImageTk.PhotoImage(img)
        self.resource_icon_imgs.append(tk_img)
        return tk_img

    def render_resource_rows(self):
        for child in self.resource_list_frame.winfo_children():
            child.destroy()
        self.resource_icon_imgs.clear()

        for resource in self.resources:
            self.make_resource_row(self.resource_list_frame, resource)
        self.update_resource_scrollregion()

    def make_resource_row(self, parent, resource):
        selected = resource.get("selected", False)
        bg = "#fff1eb" if selected else "#fffdfb"
        resource_type = resource.get("type")

        row = tk.Frame(parent, bg=bg)
        row.pack(fill="x", pady=(0, 5))

        icon_cell = tk.Frame(row, bg=bg, width=34, height=28)
        icon_cell.pack(side="left")
        icon_cell.pack_propagate(False)

        icon_img = self.load_resource_icon_image(resource_type)
        if icon_img:
            icon_label = tk.Label(icon_cell, image=icon_img, bg=bg, bd=0)
            icon_label.place(relx=0.5, rely=0.5, anchor="center")
        else:
            icon, icon_color, icon_size = self.get_resource_icon(resource_type)
            icon_label = tk.Label(
                icon_cell,
                text=icon,
                font=("Microsoft YaHei UI", icon_size, "bold"),
                fg=icon_color,
                bg=bg,
                bd=0
            )
            icon_label.place(relx=0.5, rely=0.5, anchor="center")

        name_label = tk.Label(
            row,
            text=resource.get("name", "未命名资源"),
            font=("Microsoft YaHei UI", 12, "bold" if selected else "normal"),
            fg="#4f3f37",
            bg=bg
        )
        name_label.pack(side="left", padx=(8, 0))

        meta = resource.get("meta", "")
        if meta:
            meta_label = tk.Label(
                row,
                text=meta,
                font=("Microsoft YaHei UI", 10),
                fg="#9b8a80",
                bg=bg
            )
            meta_label.pack(side="left", padx=(12, 0))

        menu = tk.Label(
            row,
            text="⋯",
            font=("Microsoft YaHei UI", 18, "bold"),
            fg="#8a7264",
            bg=bg
        )
        menu.pack(side="right", padx=(8, 10))

    def add_resource(self, resource):
        resource["selected"] = False
        self.resources.append(resource)
        self.render_resource_rows()

    def open_add_resource_dialog(self):
        ConfigureDialogAddResource(self, self.add_resource)

    def build_bottom_buttons(self):
        bottom = tk.Frame(self, bg="#fbf7f5", height=58)
        bottom.pack(side="bottom", fill="x", padx=28, pady=(0, 18))
        bottom.pack_propagate(False)

        done_btn = tk.Button(
            bottom,
            text="Next",
            font=("Microsoft YaHei UI", 12, "bold"),
            fg="white",
            bg="#e87945",
            activebackground="#d96836",
            activeforeground="white",
            relief="flat",
            bd=0,
            width=11,
            height=2,
            cursor="hand2",
            takefocus=0,
            highlightthickness=0,
            default="disabled",
            command=self.handle_done
        )
        done_btn.pack(side="right", padx=(12, 0), pady=8)

        cancel_btn = tk.Button(
            bottom,
            text="取消",
            font=("Microsoft YaHei UI", 12),
            fg="#4f3f37",
            bg="#f4ebe4",
            activebackground="#f1e8e0",
            activeforeground="#4f3f37",
            relief="flat",
            bd=0,
            width=11,
            height=2,
            cursor="hand2",
            takefocus=0,
            highlightthickness=0,
            default="disabled",
            command=self.destroy
        )
        cancel_btn.pack(side="right", pady=8)

    def handle_done(self):
        payload = {
            "mode": self.mode.get(),
            "item_name": self.get_item_name(),
            "resources": self.resources,
            "execution": self.initial_data.get("execution", {}),
            "dependency": self.initial_data.get("dependency", {})
        }
        self.initial_data["mode"] = payload["mode"]
        self.initial_data["name"] = payload["item_name"]
        self.initial_data["resources"] = payload["resources"]
        self.initial_data["execution"] = payload["execution"]
        self.initial_data["dependency"] = payload["dependency"]

        if self.mode.get() == "step":
            ConfigureStepDependencyDialog(
                self,
                payload,
                on_save=self.finish_save
            )
        else:
            ConfigureSeedExecutionDialog(
                self,
                payload,
                on_save=self.finish_save
            )

    def finish_save(self, payload):
        if self.on_save:
            self.on_save(payload)
        self.destroy()


class ConfigureSeedExecutionDialog(tk.Frame):
    def __init__(self, parent, payload, on_save=None):
        parent.prepare_step_window("配置执行方式", 740, 620)
        super().__init__(parent, bg="#fbf7f5", takefocus=1)
        self.parent = parent
        self.payload = payload
        self.on_save = on_save
        initial = payload.get("execution", {})
        self.frequency = tk.StringVar(value=initial.get("frequency", "daily"))
        self.daily_time = tk.StringVar(value=initial.get("daily_time", "slots"))
        self.weekly_count = tk.StringVar(value=str(initial.get("weekly_count", "1")))
        self.fixed_time_start = tk.StringVar(value=initial.get("fixed_time_start", "07:00"))
        self.fixed_time_end = tk.StringVar(value=initial.get("fixed_time_end", "09:00"))
        self.start_date = tk.StringVar(value=initial.get("start_date", "2024/4/24"))
        self.end_date = tk.StringVar(value=initial.get("end_date", "2024/5/20"))
        self.day_vars = {}
        self.day_checks = []
        self.fixed_day_vars = {}
        self.fixed_day_buttons = {}

        self.pack(fill="both", expand=True)
        self.build_ui()
        self.bind_background_blur()

    def center_to_parent(self):
        self.parent.set_window_size(740, 620)

    def build_ui(self):
        card = tk.Frame(
            self,
            bg="#fffdfb",
            highlightthickness=1,
            highlightbackground="#eadfd7",
            highlightcolor="#eadfd7",
            bd=0
        )
        card.pack(fill="both", expand=True, padx=38, pady=18)

        tk.Label(
            card,
            text="这个种子如何执行？",
            font=("Microsoft YaHei UI", 18, "bold"),
            fg="#4b382f",
            bg="#fffdfb"
        ).pack(pady=(18, 14))

        self.build_daily_section(card)
        self.build_fixed_time_section(card)
        self.build_weekly_count_section(card)
        self.build_date_range_section(card)
        self.build_bottom_buttons(card)
        self.select_frequency(self.frequency.get())

    def make_radio(self, parent, text, value):
        return tk.Radiobutton(
            parent,
            text=text,
            variable=self.frequency,
            value=value,
            font=("Microsoft YaHei UI", 12, "bold"),
            fg="#5c4335",
            bg="#fffdfb",
            activebackground="#fffdfb",
            selectcolor="white",
            relief="flat",
            bd=0,
            command=lambda selected=value: self.select_frequency(selected)
        )

    def build_daily_section(self, parent):
        section = tk.Frame(parent, bg="#fffdfb")
        section.pack(fill="x", padx=48, pady=(0, 12))
        self.make_radio(section, "每天", "daily").pack(anchor="w")

        inner = tk.Frame(section, bg="#fff7f3", highlightthickness=1, highlightbackground="#eadfd7")
        inner.pack(fill="x", padx=34, pady=(8, 0))

        tk.Radiobutton(
            inner,
            text="任意时间完成",
            variable=self.daily_time,
            value="anytime",
            font=("Microsoft YaHei UI", 10),
            fg="#6d5b52",
            bg="#fff7f3",
            activebackground="#fff7f3",
            selectcolor="white",
            tristatevalue="__tristate__",
            command=lambda: self.select_daily_time("anytime")
        ).pack(side="left", padx=(14, 20), pady=10)

        tk.Radiobutton(
            inner,
            text="指定多个时段：",
            variable=self.daily_time,
            value="slots",
            font=("Microsoft YaHei UI", 10),
            fg="#6d5b52",
            bg="#fff7f3",
            activebackground="#fff7f3",
            selectcolor="white",
            tristatevalue="__tristate__",
            command=lambda: self.select_daily_time("slots")
        ).pack(side="left", padx=(0, 12), pady=10)

        saved_slots = self.payload.get("execution", {}).get("daily_slots", ["evening"])
        for label, value in (("早上", "morning"), ("中午", "noon"), ("晚上", "evening")):
            var = tk.BooleanVar(value=value in saved_slots)
            self.day_vars[value] = var
            check = tk.Checkbutton(
                inner,
                text=label,
                variable=var,
                font=("Microsoft YaHei UI", 10),
                fg="#5c4335",
                bg="#fff7f3",
                activebackground="#fff7f3",
                selectcolor="white"
            )
            check.pack(side="left", padx=5)
            check.bind("<Button-1>", lambda event: self.select_frequency("daily"))
            self.day_checks.append(check)

        self.refresh_daily_slot_checks()

    def refresh_daily_slot_checks(self):
        enabled = self.daily_time.get() == "slots"
        for check in self.day_checks:
            check.configure(
                state="normal" if enabled else "disabled",
                fg="#5c4335" if enabled else "#b9a99e"
            )

    def build_fixed_time_section(self, parent):
        section = tk.Frame(parent, bg="#fffdfb")
        section.pack(fill="x", padx=48, pady=(0, 12))
        self.make_radio(section, "固定时间", "fixed_time").pack(anchor="w")

        row = tk.Frame(section, bg="#fffdfb")
        row.pack(anchor="w", padx=34, pady=(6, 0))
        tk.Label(row, text="每周：", font=("Microsoft YaHei UI", 10), fg="#6d5b52", bg="#fffdfb").pack(side="left")
        saved_fixed_days = self.payload.get("execution", {}).get("fixed_days", ["周一"])
        for day in ("周一", "周二", "周三", "周四", "周五", "周六", "周日"):
            self.fixed_day_vars[day] = tk.BooleanVar(value=day in saved_fixed_days)
            label = tk.Label(
                row,
                text=day,
                font=("Microsoft YaHei UI", 10, "bold"),
                fg="#6d5b52",
                bg="#ead8c8" if self.fixed_day_vars[day].get() else "#f4ebe4",
                padx=12,
                pady=4,
                cursor="hand2"
            )
            label.pack(side="left", padx=4)
            label.bind("<Button-1>", lambda event, d=day: self.toggle_fixed_day(d))
            self.fixed_day_buttons[day] = label

        time_row = tk.Frame(section, bg="#fffdfb")
        time_row.pack(anchor="w", padx=34, pady=(10, 0))
        tk.Label(
            time_row,
            text="时间：",
            font=("Microsoft YaHei UI", 10),
            fg="#6d5b52",
            bg="#fffdfb"
        ).pack(side="left")
        self.make_time_spinbox(
            time_row,
            self.fixed_time_start
        ).pack(side="left", padx=(8, 4), ipady=3)
        tk.Label(
            time_row,
            text="—",
            font=("Microsoft YaHei UI", 10),
            fg="#b3937a",
            bg="#fffdfb"
        ).pack(side="left")
        self.make_time_spinbox(
            time_row,
            self.fixed_time_end
        ).pack(side="left", padx=(4, 0), ipady=3)

    def build_weekly_count_section(self, parent):
        section = tk.Frame(parent, bg="#fffdfb")
        section.pack(fill="x", padx=48, pady=(0, 12))
        self.make_radio(section, "每周完成 N 次", "weekly_count").pack(anchor="w")
        row = tk.Frame(section, bg="#fffdfb")
        row.pack(anchor="w", padx=34, pady=(4, 0))
        tk.Label(row, text="每周", font=("Microsoft YaHei UI", 10), fg="#6d5b52", bg="#fffdfb").pack(side="left")
        weekly_entry = tk.Entry(row, textvariable=self.weekly_count, width=5, relief="flat", bg="#fff7f3", font=("Microsoft YaHei UI", 10))
        weekly_entry.pack(side="left", padx=8, ipady=4)
        weekly_entry.bind("<FocusIn>", lambda event: self.select_frequency("weekly_count"))
        tk.Label(row, text="次", font=("Microsoft YaHei UI", 10), fg="#6d5b52", bg="#fffdfb").pack(side="left")
        tk.Label(
            section,
            text="时间不固定，完成即可",
            font=("Microsoft YaHei UI", 9),
            fg="#c1afa5",
            bg="#fffdfb"
        ).pack(anchor="w", padx=34, pady=(5, 0))

    def make_time_spinbox(self, parent, variable):
        spinbox = tk.Spinbox(
            parent,
            textvariable=variable,
            values=self.get_time_values(),
            width=7,
            wrap=True,
            relief="flat",
            bd=0,
            bg="#fff7f3",
            buttonbackground="#fff7f3",
            fg="#4f3f37",
            font=("Microsoft YaHei UI", 10),
            insertbackground="#5c4335",
            command=lambda: self.select_frequency("fixed_time")
        )
        spinbox.bind("<FocusIn>", lambda event: self.select_frequency("fixed_time"))
        spinbox.bind("<FocusOut>", lambda event, var=variable: self.normalize_time_var(var))
        spinbox.bind("<Return>", lambda event, var=variable: self.normalize_time_var(var))
        return spinbox

    def bind_background_blur(self):
        for widget in self.winfo_children():
            self.bind_background_blur_for_widget(widget)

    def bind_background_blur_for_widget(self, widget):
        if isinstance(widget, tk.Frame):
            widget.bind("<Button-1>", lambda event: self.focus_set(), add="+")

        for child in widget.winfo_children():
            self.bind_background_blur_for_widget(child)

    def get_time_values(self):
        values = []
        for hour in range(24):
            for minute in range(0, 60, 15):
                values.append(f"{hour:02d}:{minute:02d}")
        return values

    def normalize_time_var(self, variable):
        variable.set(self.normalize_time_value(variable.get()))

    def normalize_time_value(self, value):
        text = str(value).strip()
        if ":" in text:
            hour_text, minute_text = text.split(":", 1)
        else:
            hour_text, minute_text = text, "00"

        try:
            hour = int(hour_text)
        except ValueError:
            hour = 0

        try:
            minute = int(minute_text)
        except ValueError:
            minute = 0

        hour = max(0, min(23, hour))
        minute = max(0, min(59, minute))
        return f"{hour:02d}:{minute:02d}"

    def toggle_fixed_day(self, day):
        self.select_frequency("fixed_time")
        self.fixed_day_vars[day].set(not self.fixed_day_vars[day].get())
        self.refresh_fixed_day_buttons()

    def select_daily_time(self, value):
        self.select_frequency("daily")
        self.daily_time.set(value)
        self.refresh_daily_slot_checks()

    def select_frequency(self, value):
        previous = self.frequency.get()
        self.frequency.set(value)

        if value != "daily":
            self.daily_time.set("none")
            for var in self.day_vars.values():
                var.set(False)

        if value != "fixed_time":
            for var in self.fixed_day_vars.values():
                var.set(False)
            self.fixed_time_start.set("")
            self.fixed_time_end.set("")

        if value != "weekly_count":
            self.weekly_count.set("")

        if value == "daily" and previous != "daily":
            self.daily_time.set("anytime")
        elif value == "fixed_time" and previous != "fixed_time":
            self.fixed_time_start.set("07:00")
            self.fixed_time_end.set("09:00")
        elif value == "weekly_count" and previous != "weekly_count":
            self.weekly_count.set("1")

        self.refresh_daily_slot_checks()
        self.refresh_fixed_day_buttons()

    def refresh_fixed_day_buttons(self):
        for day, label in self.fixed_day_buttons.items():
            selected = self.fixed_day_vars[day].get()
            label.configure(
                bg="#ead8c8" if selected else "#f4ebe4",
                fg="#5c4335" if selected else "#6d5b52"
            )

    def build_date_range_section(self, parent):
        section = tk.Frame(parent, bg="#fffdfb")
        section.pack(fill="x", padx=48, pady=(0, 8))
        tk.Label(
            section,
            text="执行时间范围",
            font=("Microsoft YaHei UI", 12, "bold"),
            fg="#5c4335",
            bg="#fffdfb"
        ).pack(anchor="w")
        row = tk.Frame(section, bg="#fffdfb")
        row.pack(anchor="w", padx=34, pady=(8, 0))
        for label, var in (("开始日期：", self.start_date), ("结束日期：", self.end_date)):
            tk.Label(row, text=label, font=("Microsoft YaHei UI", 10, "bold"), fg="#6d5b52", bg="#fffdfb").pack(side="left", padx=(0, 6))
            self.make_date_picker(row, var).pack(side="left", padx=(0, 28), ipady=4)

    def make_date_picker(self, parent, variable):
        box = tk.Frame(
            parent,
            bg="#fff7f3",
            highlightthickness=0,
            cursor="hand2"
        )
        entry = tk.Entry(
            box,
            textvariable=variable,
            width=12,
            relief="flat",
            bg="#fff7f3",
            font=("Microsoft YaHei UI", 10),
            cursor="hand2",
            readonlybackground="#fff7f3"
        )
        entry.pack(side="left", padx=(8, 0), ipady=4)
        drop_btn = tk.Label(
            box,
            text="▾",
            font=("Microsoft YaHei UI", 9, "bold"),
            fg="#b98a6b",
            bg="#fff7f3",
            cursor="hand2",
            padx=6
        )
        drop_btn.pack(side="left", fill="y")

        entry.bind("<Button-1>", lambda event, var=variable, widget=entry: self.open_date_picker(var, widget))
        entry.bind("<FocusIn>", lambda event, var=variable, widget=entry: self.open_date_picker(var, widget))
        drop_btn.bind("<Button-1>", lambda event, var=variable, widget=box: self.open_date_picker(var, widget))
        box.bind("<Button-1>", lambda event, var=variable, widget=box: self.open_date_picker(var, widget))
        return box

    def open_date_picker(self, variable, anchor_widget):
        self.parent.close_date_picker_popup()
        self.parent.date_picker_popup = DatePickerPopup(self, variable, anchor_widget)

    def build_bottom_buttons(self, parent):
        bottom = tk.Frame(parent, bg="#fffdfb")
        bottom.pack(side="bottom", fill="x", padx=38, pady=(0, 14))
        self.make_button(bottom, "保存", "#e87945", "white", self.handle_save).pack(side="right")
        self.make_button(bottom, "Back", "#f4ebe4", "#4f3f37", self.parent.show_resource_step).pack(side="right", padx=(0, 12))

    def make_button(self, parent, text, bg, fg, command):
        return tk.Button(
            parent,
            text=text,
            font=("Microsoft YaHei UI", 11, "bold" if text == "保存" else "normal"),
            fg=fg,
            bg=bg,
            activebackground=bg,
            activeforeground=fg,
            relief="flat",
            bd=0,
            width=11,
            height=2,
            cursor="hand2",
            takefocus=0,
            command=command
        )

    def handle_save(self):
        self.parent.close_date_picker_popup()
        frequency = self.frequency.get()
        execution = {
            "frequency": self.frequency.get(),
            "daily_time": "none",
            "daily_slots": [],
            "weekly_count": "",
            "fixed_days": [],
            "fixed_time_start": "",
            "fixed_time_end": "",
            "start_date": self.start_date.get(),
            "end_date": self.end_date.get(),
        }

        if frequency == "daily":
            execution["daily_time"] = self.daily_time.get()
            execution["daily_slots"] = [
                key for key, var in self.day_vars.items()
                if self.daily_time.get() == "slots" and var.get()
            ]
        elif frequency == "fixed_time":
            execution["fixed_days"] = [
                day for day, var in self.fixed_day_vars.items()
                if var.get()
            ]
            execution["fixed_time_start"] = self.normalize_time_value(self.fixed_time_start.get())
            execution["fixed_time_end"] = self.normalize_time_value(self.fixed_time_end.get())
        elif frequency == "weekly_count":
            execution["weekly_count"] = self.weekly_count.get()

        self.payload["execution"] = execution
        if self.on_save:
            self.on_save(self.payload)
        self.destroy()


class DatePickerPopup(tk.Frame):
    def __init__(self, parent, target_var, anchor_widget):
        super().__init__(
            parent,
            width=290,
            height=286,
            bg="#fffdfb",
            highlightthickness=1,
            highlightbackground="#eadfd7",
            highlightcolor="#eadfd7",
            bd=0
        )
        self.parent = parent
        self.target_var = target_var
        self.anchor_widget = anchor_widget
        self.year, self.month, self.selected_day = self.parse_date(target_var.get())

        self.build_ui()
        self.position_near_anchor()
        self.lift()
        self.bind("<Escape>", lambda event: self.destroy())
        self.focus_force()

    def parse_date(self, value):
        today = date.today()
        try:
            year_text, month_text, day_text = str(value).replace("-", "/").split("/")
            return int(year_text), int(month_text), int(day_text)
        except (ValueError, TypeError):
            return today.year, today.month, today.day

    def position_near_anchor(self):
        self.parent.update_idletasks()
        self.anchor_widget.update_idletasks()
        self.update_idletasks()

        x = self.anchor_widget.winfo_rootx() - self.parent.winfo_rootx()
        y = (
            self.anchor_widget.winfo_rooty()
            - self.parent.winfo_rooty()
            + self.anchor_widget.winfo_height()
            + 4
        )

        popup_w = 290
        popup_h = 286
        x = max(8, min(x, self.parent.winfo_width() - popup_w - 8))
        if y + popup_h > self.parent.winfo_height() - 8:
            y = (
                self.anchor_widget.winfo_rooty()
                - self.parent.winfo_rooty()
                - popup_h
                - 4
            )
        y = max(8, y)

        self.place(x=x, y=y, width=popup_w, height=popup_h)

    def build_ui(self):
        self.container = tk.Frame(
            self,
            bg="#fffdfb",
            bd=0
        )
        self.container.pack(fill="both", expand=True)
        self.render_calendar()

    def render_calendar(self):
        for child in self.container.winfo_children():
            child.destroy()

        header = tk.Frame(self.container, bg="#fffdfb")
        header.pack(fill="x", padx=10, pady=(8, 6))

        self.make_nav_button(header, "<<", self.prev_year, width=4).pack(side="left", padx=(0, 3))
        self.make_nav_button(header, "<", self.prev_month).pack(side="left")
        tk.Label(
            header,
            text=f"{self.year} / {self.month:02d}",
            font=("Microsoft YaHei UI", 10, "bold"),
            fg="#5c4335",
            bg="#fffdfb",
            width=11
        ).pack(side="left", padx=6)
        self.make_nav_button(header, ">", self.next_month).pack(side="left")
        self.make_nav_button(header, ">>", self.next_year, width=4).pack(side="left", padx=(3, 0))

        weekdays = tk.Frame(self.container, bg="#fffdfb")
        weekdays.pack(padx=10)
        for day_name in ("一", "二", "三", "四", "五", "六", "日"):
            tk.Label(
                weekdays,
                text=day_name,
                font=("Microsoft YaHei UI", 9, "bold"),
                fg="#9b806e",
                bg="#fffdfb",
                width=4
            ).pack(side="left")

        grid = tk.Frame(self.container, bg="#fffdfb")
        grid.pack(padx=10, pady=(2, 10))

        month_days = calendar.Calendar(firstweekday=0).monthdayscalendar(self.year, self.month)
        for week in month_days:
            row = tk.Frame(grid, bg="#fffdfb")
            row.pack()
            for day_num in week:
                if day_num == 0:
                    tk.Label(row, text="", bg="#fffdfb", width=4, height=2).pack(side="left")
                    continue

                selected = day_num == self.selected_day
                tk.Label(
                    row,
                    text=str(day_num),
                    font=("Microsoft YaHei UI", 9, "bold" if selected else "normal"),
                    fg="#5c4335",
                    bg="#ead8c8" if selected else "#fffdfb",
                    width=4,
                    height=2,
                    cursor="hand2"
                ).pack(side="left")
                row.winfo_children()[-1].bind(
                    "<Button-1>",
                    lambda event, d=day_num: self.select_day(d)
                )

    def make_nav_button(self, parent, text, command, width=3):
        return tk.Button(
            parent,
            text=text,
            font=("Microsoft YaHei UI", 9, "bold"),
            fg="#6d5b52",
            bg="#f4ebe4",
            activebackground="#ead8c8",
            activeforeground="#6d5b52",
            relief="flat",
            bd=0,
            width=width,
            cursor="hand2",
            command=command
        )

    def prev_year(self):
        self.year -= 1
        self.selected_day = min(self.selected_day, calendar.monthrange(self.year, self.month)[1])
        self.render_calendar()

    def next_year(self):
        self.year += 1
        self.selected_day = min(self.selected_day, calendar.monthrange(self.year, self.month)[1])
        self.render_calendar()

    def prev_month(self):
        self.month -= 1
        if self.month < 1:
            self.month = 12
            self.year -= 1
        self.selected_day = min(self.selected_day, calendar.monthrange(self.year, self.month)[1])
        self.render_calendar()

    def next_month(self):
        self.month += 1
        if self.month > 12:
            self.month = 1
            self.year += 1
        self.selected_day = min(self.selected_day, calendar.monthrange(self.year, self.month)[1])
        self.render_calendar()

    def select_day(self, day_num):
        self.target_var.set(f"{self.year}/{self.month}/{day_num}")
        self.destroy()


class ConfigureStepDependencyDialog(tk.Frame):
    def __init__(self, parent, payload, on_save=None):
        parent.prepare_step_window("配置步骤依赖", 760, 560)
        super().__init__(parent, bg="#fbf7f5")
        self.parent = parent
        self.payload = payload
        self.on_save = on_save
        initial = payload.get("dependency", {})
        self.selected_dependency = tk.StringVar(value=initial.get("depends_on", "none"))
        self.options = self.collect_options()

        self.pack(fill="both", expand=True)
        self.build_ui()

    def center_to_parent(self):
        self.parent.set_window_size(760, 560)

    def collect_options(self):
        configure_dialog = getattr(self.parent, "parent", None)
        current_data = getattr(configure_dialog, "current_data", {}) or {}
        current_name = self.payload.get("item_name", "")
        options = []
        for seed in current_data.get("seeds", []):
            name = seed.get("name", "")
            if name and name != current_name:
                options.append({
                    "id": name,
                    "name": name,
                    "mode": seed.get("mode", "seed")
                })
        return options

    def build_ui(self):
        header = tk.Frame(self, bg="#fbf7f5", height=66)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header,
            text="配置步骤依赖",
            font=("Microsoft YaHei UI", 18, "bold"),
            fg="#4b382f",
            bg="#fbf7f5"
        ).place(relx=0.5, rely=0.5, anchor="center")
        tk.Frame(self, bg="#eadfd7", height=1).pack(fill="x")

        body = tk.Frame(self, bg="#fbf7f5")
        body.pack(fill="both", expand=True, padx=36, pady=28)

        tk.Label(
            body,
            text="按递岗位",
            font=("Microsoft YaHei UI", 14, "bold"),
            fg="#5c4335",
            bg="#fbf7f5"
        ).pack(anchor="w")
        tk.Frame(body, bg="#eadfd7", height=1).pack(fill="x", pady=(16, 20))

        panel = tk.Frame(body, bg="#fffdfb", highlightthickness=1, highlightbackground="#eadfd7")
        panel.pack(fill="x")

        tk.Label(
            panel,
            text="选择前置步骤",
            font=("Microsoft YaHei UI", 13, "bold"),
            fg="#5c4335",
            bg="#fffdfb"
        ).pack(anchor="w", padx=18, pady=(16, 6))
        tk.Label(
            panel,
            text="请选择必须先完成的步骤，完成后才能解锁当前步骤",
            font=("Microsoft YaHei UI", 10),
            fg="#8a7264",
            bg="#fffdfb"
        ).pack(anchor="w", padx=18, pady=(0, 14))
        tk.Frame(panel, bg="#eadfd7", height=1).pack(fill="x")

        self.make_option(panel, "none", "无依赖", selected_bg="#fffdfb")
        if self.options:
            for option in self.options:
                self.make_option(panel, option["id"], option["name"])
        else:
            tk.Label(
                panel,
                text="还没有可选择的前置事项",
                font=("Microsoft YaHei UI", 11),
                fg="#a58d7e",
                bg="#fffdfb"
            ).pack(anchor="w", padx=48, pady=18)

        bottom = tk.Frame(self, bg="#fbf7f5")
        bottom.pack(side="bottom", fill="x", padx=36, pady=(0, 24))
        self.make_button(bottom, "保存", "#e87945", "white", self.handle_save).pack(side="right")
        self.make_button(bottom, "Back", "#f4ebe4", "#4f3f37", self.parent.show_resource_step).pack(side="right", padx=(0, 12))

    def make_option(self, parent, value, text, selected_bg="#fff7f3"):
        row = tk.Frame(parent, bg=selected_bg if self.selected_dependency.get() == value else "#fffdfb")
        row.pack(fill="x", padx=18, pady=(0, 4))
        radio = tk.Radiobutton(
            row,
            variable=self.selected_dependency,
            value=value,
            bg=row["bg"],
            activebackground=row["bg"],
            selectcolor="white",
            command=lambda: self.refresh_options(parent)
        )
        radio.pack(side="left", padx=(4, 10), pady=8)
        tk.Label(
            row,
            text=text,
            font=("Microsoft YaHei UI", 12, "bold" if value != "none" else "normal"),
            fg="#5c4335",
            bg=row["bg"]
        ).pack(side="left", pady=8)
        tk.Label(
            row,
            text="⋯" if value != "none" else "",
            font=("Microsoft YaHei UI", 16, "bold"),
            fg="#9b8a80",
            bg=row["bg"]
        ).pack(side="right", padx=14)

    def refresh_options(self, panel):
        for child in panel.winfo_children()[3:]:
            child.destroy()
        self.make_option(panel, "none", "无依赖", selected_bg="#fffdfb")
        for option in self.options:
            self.make_option(panel, option["id"], option["name"])

    def make_button(self, parent, text, bg, fg, command):
        return tk.Button(
            parent,
            text=text,
            font=("Microsoft YaHei UI", 11, "bold" if text == "保存" else "normal"),
            fg=fg,
            bg=bg,
            activebackground=bg,
            activeforeground=fg,
            relief="flat",
            bd=0,
            width=11,
            height=2,
            cursor="hand2",
            takefocus=0,
            command=command
        )

    def handle_save(self):
        self.payload["dependency"] = {
            "depends_on": self.selected_dependency.get()
        }
        if self.on_save:
            self.on_save(self.payload)
        self.destroy()


class ConfigureDialogAddResource(tk.Toplevel):
    def __init__(self, parent, on_save=None):
        super().__init__(parent)
        self.withdraw()
        self.parent = parent
        self.on_save = on_save
        self.resource_type = tk.StringVar(value="book")
        self.progress_type = tk.StringVar(value="chapter")
        self.type_detail_entry = None

        self.title("添加学习资源")
        self.configure(bg="#f7f3ee")
        self.resizable(False, False)
        self.transient(parent)

        self.center_to_parent()
        self.deiconify()
        self.lift()
        self.update()
        self.build_ui()
        self.update_idletasks()
        self.grab_set()

    def center_to_parent(self):
        w, h = 620, 650
        self.parent.update_idletasks()

        x = self.parent.winfo_rootx() + (self.parent.winfo_width() - w) // 2
        y = self.parent.winfo_rooty() + (self.parent.winfo_height() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def build_ui(self):
        outer = tk.Frame(
            self,
            bg="#fbf8f4"
        )
        outer.pack(fill="both", expand=True, padx=18, pady=18)

        header = tk.Frame(outer, bg="#fbf8f4")
        header.pack(fill="x", padx=28, pady=(24, 14))

        title = tk.Label(
            header,
            text="添加学习资源",
            font=("Microsoft YaHei UI", 17, "bold"),
            fg="#5c4335",
            bg="#fbf8f4"
        )
        title.pack(side="left")


        self.form = tk.Frame(outer, bg="#fbf8f4")
        self.form.pack(fill="both", expand=True, padx=28)

        self.name_entry = self.build_input("资源名称", "")
        self.build_resource_type_selector()

        self.type_detail_wrap = tk.Frame(self.form, bg="#fbf8f4")
        self.type_detail_wrap.pack(fill="x")
        self.build_type_detail_input()

        self.link_entry = self.build_input("资源链接（可选）", "")
        self.build_progress_selector()
        self.build_bottom_buttons(outer)

    def build_input(self, label_text, placeholder):
        wrap = tk.Frame(self.form, bg="#fbf8f4")
        wrap.pack(fill="x", pady=(0, 13))

        label = tk.Label(
            wrap,
            text=label_text,
            font=("Microsoft YaHei UI", 10, "bold"),
            fg="#5b473c",
            bg="#fbf8f4"
        )
        label.pack(anchor="w", pady=(0, 7))

        entry_box = tk.Frame(wrap, bg="#e1d7cf")
        entry_box.pack(fill="x")

        entry = tk.Entry(
            entry_box,
            font=("Microsoft YaHei UI", 10),
            fg="#4f3f37",
            bg="white",
            relief="flat",
            bd=0,
            highlightthickness=0,
            insertbackground="#5c4335"
        )
        entry.pack(fill="x", padx=1, pady=1, ipady=9)
        if placeholder:
            entry.insert(0, placeholder)
        return entry

    def build_resource_type_selector(self):
        self.type_buttons = {}
        self.build_selector_row(
            title="资源类型",
            choices=[
                ("book", "书"),
                ("video", "视频"),
                ("online_course", "Online Course"),
                ("document", "文档"),
                ("school_course", "学校课程"),
            ],
            variable=self.resource_type,
            button_map=self.type_buttons,
            command=self.refresh_type_buttons
        )
        self.refresh_type_buttons()

    def get_type_detail_config(self):
        configs = {
            "book": ("总章节数", "例如：12"),
            "video": ("总时长（分钟）", "例如：180"),
            "online_course": ("总课数", "例如：36"),
            "document": ("总 section 数", "例如：8"),
            "school_course": ("课程周数", "例如：12"),
        }
        return configs[self.resource_type.get()]

    def apply_resource_type_defaults(self):
        defaults = {
            "book": "chapter",
            "video": "hour",
            "online_course": "chapter",
            "document": "done",
            "school_course": "week",
        }
        self.progress_type.set(defaults[self.resource_type.get()])
        if hasattr(self, "progress_buttons"):
            self.refresh_progress_buttons()

    def build_type_detail_input(self):
        for child in self.type_detail_wrap.winfo_children():
            child.destroy()

        label_text, placeholder = self.get_type_detail_config()
        wrap = tk.Frame(self.type_detail_wrap, bg="#fbf8f4")
        wrap.pack(fill="x", pady=(0, 13))

        label = tk.Label(
            wrap,
            text=label_text,
            font=("Microsoft YaHei UI", 10, "bold"),
            fg="#5b473c",
            bg="#fbf8f4"
        )
        label.pack(anchor="w", pady=(0, 7))

        entry_box = tk.Frame(wrap, bg="#e1d7cf")
        entry_box.pack(fill="x")

        entry = tk.Entry(
            entry_box,
            font=("Microsoft YaHei UI", 10),
            fg="#4f3f37",
            bg="white",
            relief="flat",
            bd=0,
            highlightthickness=0,
            insertbackground="#5c4335"
        )
        entry.pack(fill="x", padx=1, pady=1, ipady=9)
        if placeholder:
            entry.insert(0, placeholder)
        self.type_detail_entry = entry

    def build_progress_selector(self):
        self.progress_buttons = {}
        self.build_selector_row(
            title="进度追踪方式",
            choices=[
                ("chapter", "按章节"),
                ("hour", "按小时数"),
                ("week", "按周数"),
                ("done", "完成/未完成"),
            ],
            variable=self.progress_type,
            button_map=self.progress_buttons,
            command=self.refresh_progress_buttons
        )
        self.refresh_progress_buttons()

    def build_selector_row(self, title, choices, variable, button_map, command):
        wrap = tk.Frame(self.form, bg="#fbf8f4")
        wrap.pack(fill="x", pady=(0, 13))

        label = tk.Label(
            wrap,
            text=title,
            font=("Microsoft YaHei UI", 10, "bold"),
            fg="#5b473c",
            bg="#fbf8f4"
        )
        label.pack(anchor="w", pady=(0, 7))

        row = tk.Frame(wrap, bg="#fbf8f4")
        row.pack(anchor="w")

        for value, text in choices:
            btn = tk.Button(
                row,
                text=text,
                font=("Microsoft YaHei UI", 10, "bold"),
                fg="#6d5b52",
                relief="flat",
                bd=0,
                padx=13,
                pady=7,
                cursor="hand2",
                takefocus=0,
                highlightthickness=0,
                command=lambda v=value: self.select_option(variable, v, command)
            )
            btn.pack(side="left", padx=(0, 8))
            button_map[value] = btn

    def select_option(self, variable, value, refresh_command):
        variable.set(value)
        refresh_command()

        if variable is self.resource_type:
            self.apply_resource_type_defaults()
            self.build_type_detail_input()

    def refresh_type_buttons(self):
        self.refresh_buttons(self.type_buttons, self.resource_type.get())

    def refresh_progress_buttons(self):
        self.refresh_buttons(self.progress_buttons, self.progress_type.get())

    def refresh_buttons(self, buttons, selected_value):
        for value, btn in buttons.items():
            selected = value == selected_value
            btn.configure(
                bg="#ead8cb" if selected else "#f4ebe4",
                activebackground="#dfc7b8" if selected else "#eadcd0",
                fg="#5c4335" if selected else "#7a5f50",
                highlightthickness=0
            )

    def build_bottom_buttons(self, parent):
        bottom = tk.Frame(parent, bg="#fbf8f4")
        bottom.pack(fill="x", padx=28, pady=(10, 24))

        save_btn = tk.Button(
            bottom,
            text="保存",
            font=("Microsoft YaHei UI", 12, "bold"),
            fg="white",
            bg="#e69154",
            activebackground="#d98245",
            activeforeground="white",
            relief="flat",
            bd=0,
            width=8,
            padx=22,
            pady=10,
            cursor="hand2",
            takefocus=0,
            highlightthickness=0,
            default="disabled",
            command=self.handle_save
        )
        save_btn.pack(side="right", padx=(12, 0))

        cancel_btn = tk.Button(
            bottom,
            text="取消",
            font=("Microsoft YaHei UI", 12),
            fg="#4f3f37",
            bg="#f4ebe4",
            activebackground="#eadcd0",
            activeforeground="#4f3f37",
            relief="flat",
            bd=0,
            width=8,
            padx=22,
            pady=10,
            cursor="hand2",
            takefocus=0,
            highlightthickness=0,
            default="disabled",
            command=self.destroy
        )
        cancel_btn.pack(side="right")

    def handle_save(self):
        resource = {
            "name": self.name_entry.get().strip() or "未命名资源",
            "type": self.resource_type.get(),
            "detail_label": self.get_type_detail_config()[0],
            "detail_value": self.type_detail_entry.get().strip() if self.type_detail_entry else "",
            "link": self.link_entry.get().strip(),
            "progress_type": self.progress_type.get(),
            "meta": "",
        }
        print(resource)
        if self.on_save:
            self.on_save(resource)
        self.destroy()
