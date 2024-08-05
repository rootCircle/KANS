#from tkinter import *
import tkinter as tk
from PIL import Image, ImageTk
import tkinter as tk
import time
import threading
LOADING_SCREENS = []
LOADING_GIF = "ANIMATION5.gif"

class LoadingPage(tk.Label):
    def __init__(self, master, filename):
        try:
            im = Image.open(filename)
            seq =  []
            try:
                while 1:
                    seq.append(im.copy())
                    im.seek(len(seq)) # skip to next frame
            except EOFError:
                pass # we're done

            try:
                self.delay = im.info['duration']
            except KeyError:
                self.delay = 100

            first = seq[0].convert('RGBA')
            self.frames = [ImageTk.PhotoImage(first)]

            tk.Label.__init__(self, master, image=self.frames[0])

            temp = seq[0]
            for image in seq[1:]:
                temp.paste(image)
                frame = temp.convert('RGBA')
                self.frames.append(ImageTk.PhotoImage(frame))

            self.idx = 0

            self.cancel = self.after(self.delay, self.play)
        except FileNotFoundError as e:
            print("File not found\nQuit Module Use")
            

    def play(self):
        self.config(image=self.frames[self.idx])
        self.idx += 1
        if self.idx == len(self.frames):
            self.idx = 0
        self.cancel = self.after(self.delay, self.play)

    def start(self,grab=True):
        """
        grab will set toplevel active and root window inactive
        """
        LOADING_SCREENS.append(tk.Toplevel())
        screen = LOADING_SCREENS[-1]
        try:
            screen.wm_overrideredirect(True)
        except:
            screen.overrideredirect(True)

        # Eval is threading Unsafe
        #self.eval(f'tk::PlaceWindow {str(screen)} center')

        x = self.winfo_x()
        y = self.winfo_y()
        geo = self.winfo_geometry()
        try:
            screen_width = int(geo[:geo.find("x")])
            screen_height = int(geo[geo.find("x")+1:geo.find("+")])
        except:
            screen_width = 300
            screen_height = 300
        print(x,y,screen_width,screen_height,)
        screen.geometry("+%d+%d" % (x + screen_width//2-100, y + screen_height//2 -100))

        screen.iconphoto(False, Icon)
        screen.resizable(0, 0)
        screen.title("Loading...")
        if grab:
            screen.grab_set()
        self.anim = LoadingPage(screen, LOADING_GIF)
        self.anim.pack()

    def stop_it(self):
        if LOADING_SCREENS:
            screen = LOADING_SCREENS[-1]
            self.anim.after_cancel(self.anim.cancel)
            screen.destroy()
            del LOADING_SCREENS[-1]

    def perform(self,args):
        """
        args should include destination function
        order of args(root ,function,arguments)
        """
        t1 = threading.Thread(target=LoadingPage.start, args=(self,))
        t1.start()
        t2 = threading.Thread(target=LoadingPage.fxn,args=args)
        t2.start()
    
    def fxn(self,*args):
        #Your function here
        #my_function(args)
        args[0](args[1:][0])
        # Don't edit this
        LoadingPage.stop_it(self)
root = tk.Tk()

Icon = tk.PhotoImage(file="logo.png")
tk.Label(root,text="Hello World This is a page.").pack()
LoadingPage.start(root,grab=False)
time.sleep(10)
LoadingPage.stop_it(root)
root.mainloop()

