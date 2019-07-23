from Tkinter import *

master = Tk()
master.minsize(300, 100)
master.geometry("320x100")


def callback():
    print "click!"


photo = PhotoImage(file="C:/Users/Behemoth/TouchHere.png")
b = Button(master, image=photo, text="Touch", command=callback, height=480, width=800)
b.pack()

mainloop()