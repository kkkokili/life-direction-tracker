from  tkinter import ttk,Canvas,PhotoImage,Label,Frame
import tkinter as tk

YELLOW = "#f7f5dd"
FONT_NAME = "Courier"
GREEN = "#9bdeac"

# tomato class set up
class tomato(Frame):
    def __init__(self,parent):
        super().__init__(parent,bg=YELLOW)
        self.window=parent
        self.seconds=0
        self.minutes=0
        self.hours=0
        self.img=PhotoImage(file="tomato.png")
        self.canvas=Canvas(self,width=300,height=424,bg=YELLOW,bd=-2)
        self.canvas.create_image(100, 112, image=self.img)
        self.canvas.grid(row=1, column=1)
        self.clock=self.canvas.create_text(102,135,text=f"{self.hours:02d}:{self.minutes:02d}:{self.seconds:02d}",fill="white",font=(FONT_NAME,30,"bold"))
        #start button config
        self.start_button = ttk.Button(self, text="Start", command=self.start)
        self.start_button.grid(column=0, row=2)
        #reset button config
        self.end_button = ttk.Button(self, text="Reset", command=self.end)
        self.end_button.grid(column=2, row=2)
        # Timer Label set up
        self.label = Label(self, text="Timer", font=(FONT_NAME, 30, "bold"), bg=YELLOW, fg=GREEN)
        self.label.grid(column=1, row=0)
        self.label = Label(self, text=" ✔", font=(FONT_NAME, 30, "bold"), bg=YELLOW, fg=GREEN)
        self.label.grid(column=1, row=3)

    # start button func set up
    def start(self):
        if self.seconds < 60:
            self.seconds += 1
            self.canvas.itemconfig(self.clock,
                                   text=f"{self.hours:02d}:{self.minutes:02d}:{self.seconds:02d}")
            self.window.after(1000, self.start)
        elif self.seconds == 60:
            self.minutes += 1
            if self.minutes == 60:
                self.hours += 1
                self.minutes = 0
            self.seconds = 0
            self.canvas.itemconfig(self.clock,
                                   text=f"{self.hours:02d}:{self.minutes:02d}:{self.seconds:02d}")
            self.window.after(1000, self.start)

    def end(self):
        print("End")












