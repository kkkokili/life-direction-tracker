
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageTk
from  tkinter import Label,Frame
from config.theme import BG_MAIN
from services.wake_tracker import decide_getup_time, get_monthly_early_percentage
from services.quote_service import destructure_data, get_random_feedback_quote
import random

#config base_dir path
BASE_DIR = Path(__file__).resolve().parent.parent
IMG_DIR = BASE_DIR / "img"

#控制greeting fade out 节奏
STEPS=40
INTERVAL1=30
INTERVAL2=70

class Greeting(Frame):
    def __init__(self,parent,on_finish=None):
        super().__init__(parent)
        self.on_finish = on_finish
        self.wake_up_time="00:00 AM"
        self.early=True
        self.streak=0
        self.line_index=0
        self.font_greeting = ("Mynerve", 25, "bold")
        self.font_feedback = ("Courier New", 18)
        self.font_quote = ("Courier New", 20)
        q, a = destructure_data()
        quote_text = f"\n“{q}”\n\n— {a}"  # ✅ 两行：quote + author
        author_img = self.__load_author_icon(a)
        # 每条对应的 emoji：第0条有，1/2条没有（先这样）
        self.__decide_greeting_emoji()
        self.line_emojis = [self.emoji_pil_base, None, author_img ]
        self.configure(bg=BG_MAIN)
        # as long as greeting part works, the data dir always exist,decide_getup_time() contains create_data_dir()method
        #as long as the decide_getup_time execute, the self.early and self.wake_up_time will update
        wake_info = decide_getup_time()
        self.wake_up_time = wake_info["wake_time"]
        self.early = wake_info["early"]
        self.streak = wake_info["streak"]

        self.center_label = Label(
            self,
            text="CENTER TEST",
            image=self.emoji_img,
            compound="right",  # 关键！
            bg=BG_MAIN,
            fg="#3f3a34",
            font=("Mynerve", 30, "bold"),
            wraplength=680,
            justify="left"
        )
        # font in quotes fit the window
        self.center_label.place(relx=0.5, rely=0.5, anchor="center", relwidth=1.0)
        self.bind("<Configure>", self._on_resize)

        greeting_text = f"Good {self.part_of_day()}! Xiaotong "
        feedback_text = self.feedback()



        self.lines = [greeting_text, feedback_text, quote_text]
        self.after(1000, self.__fade_out_all)

        # 关键：用 place 放到正中间
        self.center_label.place(relx=0.5, rely=0.5, anchor="center")
        self.center_label.config(text=self.lines[self.line_index])

    def _on_resize(self, event):
        pad = 80  # 左右留白，自己调：60/80/100
        self.center_label.config(wraplength=max(200, event.width - pad))

    def __load_author_icon(self, author):
        path = IMG_DIR / "quotes" / f"{author}.png"
        if path.exists():
            img = Image.open(path).convert("RGBA")

            # 最大边不超过 60x60，自动保持比例
            img.thumbnail((550, 550), Image.LANCZOS)

            return img
        return None

    def __decide_greeting_emoji(self):
        hour = datetime.now().hour

        if 5 <= hour < 17:
            img = Image.open(IMG_DIR / "greeting" / "weather.png").convert("RGBA")
            # 设定你想要的尺寸（比如 28x28）
            img = img.resize((50, 50), Image.LANCZOS)

        elif 17 <= hour < 21:
            img = Image.open(IMG_DIR / "greeting" / "nature.png").convert("RGBA")
            img = img.resize((34, 34), Image.LANCZOS)

        else:
            img = Image.open(IMG_DIR / "greeting" / "half-moon.png").convert("RGBA")
            img = img.resize((34, 34), Image.LANCZOS)
        self.emoji_pil_base = img  # ✅ 保存母版
        self.emoji_img = ImageTk.PhotoImage(img)  # ✅ 初始注册

    def _hex_to_rgb(self, h):
        h = h.lstrip("#")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

    def _rgb_to_hex(self, rgb):
        return "#%02x%02x%02x" % rgb

    def _icon_frame(self, base_rgba: Image.Image):
        # 把原始透明图正确“落到”背景色上，去掉黑边来源
        bg = Image.new("RGBA", base_rgba.size, BG_MAIN)
        return Image.alpha_composite(bg, base_rgba)  # icon_on_bg

    def __fade_out_all(self, step=0, steps=STEPS, interval=INTERVAL1):
        # ✅ 如果当前正在显示的是最后一条：让 fadeout 更慢、更长
        if step == 0 and self.line_index == len(self.lines) - 1:
            steps = STEPS * 2  # 想更长就改倍数：2/3/4...
            interval = INTERVAL1   # 想更慢就改倍数：1.5/2/3...
        elif step == 0 and self.line_index == len(self.lines) - 2:
            steps = STEPS * 4  # 想更长就改倍数：2/3/4...
            interval = INTERVAL2  # 想更慢就改倍数：1.5/2/3...

        # 进度 0~1
        t = step / steps

        # 1) 文字颜色：#222222 -> BG_COLOR
        start_rgb = (74,64,54)
        end_rgb = self._hex_to_rgb(BG_MAIN)
        cur_rgb = (
            int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * t),
            int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * t),
            int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * t),
        )
        self.center_label.config(fg=self._rgb_to_hex(cur_rgb))

        # 2) emoji alpha：255 -> 0（前提：你已经有 self.emoji_pil_base）
        if self.emoji_pil_base is not None:
            icon_on_bg = self._icon_frame(self.emoji_pil_base)
            bg = Image.new("RGBA", icon_on_bg.size, BG_MAIN)

            # t: 0->1，逐渐变成背景
            out = Image.blend(icon_on_bg, bg, t)

            self.emoji_img = ImageTk.PhotoImage(out)
            self.center_label.config(image=self.emoji_img)

        # 下一帧
        if step < steps:
            self.after(interval, self.__fade_out_all, step + 1, steps, interval)
        else:
            self.__play_next()

    def __fade_in_all(self, step=0, steps=STEPS, interval=INTERVAL2):
        # 进度 0 -> 1
        t = step / steps

        # ===== 1) 文字淡入：BG_COLOR -> #222222 =====
        start_rgb = self._hex_to_rgb(BG_MAIN)
        end_rgb = (74,64,54)

        cur_rgb = (
            int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * t),
            int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * t),
            int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * t),
        )

        self.center_label.config(fg=self._rgb_to_hex(cur_rgb))

        # 2) emoji 淡入：alpha 0 -> 255
        if self.emoji_pil_base is not None:
            icon_on_bg = self._icon_frame(self.emoji_pil_base)
            bg = Image.new("RGBA", icon_on_bg.size, BG_MAIN)

            # t: 0->1，逐渐显示图标
            out = Image.blend(bg, icon_on_bg, t)

            self.emoji_img = ImageTk.PhotoImage(out)
            self.center_label.config(image=self.emoji_img)

        # ===== 下一帧 or 结束 =====
        if step < steps:
            next_interval = interval

            # 只有倒数第二页，在最后几帧减慢
            if self.line_index == len(self.lines) - 2 and step >= steps - 6:
                next_interval = interval * 3
            self.after(next_interval, self.__fade_in_all, step + 1, steps, interval)
        else:
            # 淡入结束后，等待 1500ms 再淡出
            self.after(1500, self.__fade_out_all)

    def __play_next(self):
        self.line_index += 1

        if self.line_index >= len(self.lines):
            if self.on_finish:
                self.after(500, self.on_finish)
            return

        self.__set_line()
        self.center_label.config(fg=BG_MAIN)
        self.__fade_in_all()

    def __set_line(self):
        self.center_label.config(text=self.lines[self.line_index])

        # 根据 line_index 切换字体
        if self.line_index ==0:
            self.center_label.config(font=self.font_greeting)
        elif self.line_index ==1:
            self.center_label.config(font=self.font_feedback)
        else:
            self.center_label.config(font=self.font_quote)

        base = self.line_emojis[self.line_index]

        if base is None:
            self.emoji_pil_base = None
            self.center_label.config(image="", compound="none")
        else:
            self.emoji_pil_base = base
            self.emoji_img = ImageTk.PhotoImage(self.emoji_pil_base)

            # ✅ 只有第三行（index == 2）图片在上面
            if self.line_index == 2:
                self.center_label.config(image=self.emoji_img, compound="top")
            else:
                self.center_label.config(image=self.emoji_img, compound="right")


    def part_of_day(self):
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"

    def feedback(self):
        if self.early:
            return f"GET  UP  TIME: {self.wake_up_time}\n\n You’ve already won the first step today :)\n{'Your streak record is '+str(self.streak)if self.streak >= 3 else ''}"
        else:
            monthly_data = get_monthly_early_percentage()
            conservative_progress_rate = monthly_data[0]
            print(conservative_progress_rate)
            consistency_among_logged_days_rate=monthly_data[1]
            feedback=get_random_feedback_quote()+f"\n\nYou’ve already woken up early {conservative_progress_rate}% of the time this month. That’s excellent within a solid range, and you’re doing really well:) \nLife has its ups and downs — it’s a long-distance run.\n\nKeep going."
            return feedback















