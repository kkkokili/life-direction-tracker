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

        load_private_font("font/Mynerve-Regular.ttf")
        load_private_font("font/Schoolbell-Regular.ttf")
        load_private_font("font/TheGirlNextDoor-Regular.ttf")
        load_private_font("font/PatrickHand-Regular.ttf")
        load_private_font("font/ComicRelief-Regular.ttf")
        load_private_font("font/Sniglet-Regular.ttf")


        self.current_page = None


        self.show_life_direction()

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



