import tkinter as tk
from pages.greeting import Greeting
from font.font_loader import load_private_font
from pages.life_direction import LifeDirection
from config.theme import BG_MAIN

# ---------------------------- CONSTANTS ------------------------------- #

FONT_NAME = "Courier"
WORK_MIN = 25
SHORT_BREAK_MIN = 5
LONG_BREAK_MIN = 20
# ---------------------------- UI SETUP ------------------------------- #
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Xiaotong's Small Timer")
        self.root.geometry("900x700")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_MAIN)

        self.current_page = None
        self.show_loading()
        self.root.update_idletasks()
        self.bring_to_front()
        self.root.after(50, self.bring_to_front)
        self.root.after(1, self.bootstrap)

    def bootstrap(self):
        load_private_font("font/Mynerve-Regular.ttf")
        load_private_font("font/Schoolbell-Regular.ttf")
        load_private_font("font/TheGirlNextDoor-Regular.ttf")
        load_private_font("font/PatrickHand-Regular.ttf")
        load_private_font("font/ComicRelief-Regular.ttf")
        load_private_font("font/Sniglet-Regular.ttf")

        self.show_life_direction()
        self.root.after(1, self.bring_to_front)

    def bring_to_front(self):
        self.root.deiconify()
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after(100, lambda: self.root.attributes("-topmost", False))
        self.root.focus_force()

    def show_loading(self):
        self.clear_page()
        self.current_page = tk.Frame(self.root, bg=BG_MAIN)
        loading = tk.Label(
            self.current_page,
            text="Loading...",
            font=("Microsoft YaHei UI", 13),
            fg="#6d5b52",
            bg=BG_MAIN
        )
        loading.place(relx=0.5, rely=0.5, anchor="center")
        self.current_page.pack(fill="both", expand=True)

    def clear_page(self):
        if self.current_page is not None:
            self.current_page.destroy()
            self.current_page = None

    def show_greeting(self):
        self.clear_page()
        self.current_page = Greeting(self.root, on_finish=self.show_life_direction)
        self.current_page.pack(fill="both", expand=True)

    def show_life_direction(self):
        self.clear_page()
        self.current_page = LifeDirection(self.root)
        self.current_page.pack(fill="both", expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()



