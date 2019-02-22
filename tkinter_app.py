from tkinter import Tk, Label, Button, filedialog
import os
import pandas as pd
from subprocess import call

from jinja_app import generate_report


class MyFirstGUI:
    def __init__(self, master):
        self.master = master
        master.title("A simple GUI")

        self.label = Label(master, text="Best GUI ever!")
        self.label.pack()

        self.first_button = Button(master, text="Pick the First File", command=self.open_file_1)
        self.first_button.pack()

        self.second_button = Button(master, text="Pick the Second File", command=self.open_file_2)
        self.second_button.pack()

        self.jinja_button = Button(master, text="MAGIC!", command=self.run_jinja)
        self.jinja_button.pack()

        self.close_button = Button(master, text="That's enough magic for now", command=master.quit)
        self.close_button.pack()

        
    def open_file_1(self):
        self.filename_1 = filedialog.askopenfilename(initialdir = os.getcwd(), title = "Select file")
    
    def open_file_2(self):
        self.filename_2 = filedialog.askopenfilename(initialdir = os.getcwd(), title = "Select file")

    def run_jinja(self):
        generate_report(self.filename_1, self.filename_2)

root = Tk()
root.geometry("500x500")
my_gui = MyFirstGUI(root)
root.mainloop()