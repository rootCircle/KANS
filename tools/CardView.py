# importing only those functions
# which are needed
from tkinter import *

# from tkinter.ttk import *
from PIL import Image, ImageTk
import tkinter as tk


def cardview(self, diry, irow, icolumn, name, price, desc):
    Photo = Image.open(diry)
    Photo = Photo.resize((100, 100))
    render = ImageTk.PhotoImage(Photo)
    imgbtn = tk.Button(
        self,
        image=render,
        text=name + "\nPrice : " + str(price) + "\n" + desc,
        compound=LEFT,
    )
    imgbtn.config(
        bg="#333333",
        fg="#E8E8E8",
        bd=0,
        activebackground="#3297E9",
        font=("Chiller", 25),
    )
    imgbtn.image = render
    imgbtn.grid(row=irow, column=icolumn, padx=10, pady=10)


# creating tkinter window
root = Tk()


diry = r"Additem.png"

cardview(
    root,
    diry,
    0,
    0,
    "Daffodills",
    100,
    "Beautifulszxcggvbvbvghhhhhhhhhhhhhhhhhhhhhhhhhhhhhh",
)
cardview(
    root,
    diry,
    1,
    0,
    "Daffodills",
    100,
    "Beautifulszxcggvbvbvghhhhhhhhhhhhhhhhhhhhhhhhhhhhhh",
)
cardview(
    root,
    diry,
    2,
    0,
    "Daffodills",
    100,
    "Beautifulszxcggvbvbvghhhhhhhhhhhhhhhhhhhhhhhhhhhhhh",
)
cardview(
    root,
    diry,
    3,
    0,
    "Daffodills",
    100,
    "Beautifulszxcggvbvbvghhhhhhhhhhhhhhhhhhhhhhhhhhhhhh",
)

root.mainloop()
