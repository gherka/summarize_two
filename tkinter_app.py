'''
NEED TO THINK ABOUT THE BEST WAY TO PASS DATA BETWEEN
TKINTER, SEABORN_PLOTS AND SUMMARY_STATS; MAYBE PICKLE?
Use subprocess call to add support for running external scripts

Re-factor into more meaningful classes
'''

from tkinter import Tk, Label, Button, filedialog, StringVar, OptionMenu, Frame, W
import os
import pandas as pd

from jinja_app import generate_report


class BasicGUI:
    #CHILD OF ROOT (TOP-LEVEL WINDOW)
    def __init__(self, master):

        self.myContainer = Frame(master)
        self.myContainer.grid(row=0, column=1)

        self.master = master

        master.title("Dataset comparison tool")

        self.label = Label(self.myContainer, text="Use the buttons to operate the tool!").grid(row=0, column=0, pady=10, padx=5)

        self.first_button = Button(self.myContainer, text="Pick the First File", command=self.open_file_1)
        self.first_button.grid(row=1, column=0, sticky=W)

        self.second_button = Button(self.myContainer, text="Pick the Second File", command=self.open_file_2)
        self.second_button.grid(row=2, column=0, sticky=W)

        #Set defaults for testing
        self.filename_1 = 'C:\\Users\\germap01\\Python\\UNSORTED\\Hackathon\\2019\\Working\\data_1.csv'
        self.filename_2 = 'C:\\Users\\germap01\\Python\\UNSORTED\\Hackathon\\2019\\Working\\data_2.csv'
        
        #Create a dropdown
        self.tkvar = StringVar(self.myContainer)
        self.choices = ['Pizza','Lasagne','Fries','Fish','Potatoe']
        self.tkvar.set('Pizza')

        popupMenu = OptionMenu(self.myContainer, self.tkvar, *self.choices)
        Label(self.myContainer, text="Choose a dish").grid(row=3, column=0, sticky=W)
        popupMenu.grid(row=3, column=1, pady=(2,8), sticky=W)

        # on change dropdown value
        def change_dropdown(*args):
            print( self.tkvar.get() )

        # link function to change dropdown
        self.tkvar.trace('w', change_dropdown)

        self.jinja_button = Button(self.myContainer, text="MAGIC!", command=self.run_jinja)
        self.jinja_button.grid(row=4, column=0, sticky=W)

        self.close_button = Button(self.myContainer, text="That's enough magic for now", command=self.myContainer.quit)
        self.close_button.grid(row=5, column=0, sticky=W)

    #FUNCTIONS:
    def open_file_1(self):
        self.filename_1 = filedialog.askopenfilename(initialdir = os.getcwd(), title = "Select file")
    
    def open_file_2(self):
        self.filename_2 = filedialog.askopenfilename(initialdir = os.getcwd(), title = "Select file")

    def run_jinja(self):
        generate_report(self.filename_1, self.filename_2)

root = Tk()
root.geometry("500x500")
my_gui = BasicGUI(root)

#Position the myContainer in the middle of the Main Window 3x3 grid
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(2, weight=1)


#RUN TKINTER LOOP
root.mainloop()