'''
NEED TO THINK ABOUT THE BEST WAY TO PASS DATA BETWEEN
TKINTER, SEABORN_PLOTS AND SUMMARY_STATS; MAYBE PICKLE?
Use subprocess call to add support for running external scripts

Re-factor into more meaningful classes
'''

from tkinter import Tk, Label, Button, filedialog, StringVar, OptionMenu, Frame, W, LEFT
from tkinter import ttk
import os
import pandas as pd

from jinja_app import generate_report
from summary_stats import generate_summary

class BasicGUI:
    #CHILD OF ROOT (TOP-LEVEL WINDOW)
    def __init__(self, master):

        self.myContainer = Frame(master)
        self.myContainer.grid(row=0, column=1)

        self.master = master

        master.title("Dataset comparison tool")

        self.label = (Label(self.myContainer, text="Use the buttons to operate the tool!")
                            .grid(row=0, column=0, columnspan=2, pady=10, padx=5))

        self.first_button = Button(self.myContainer, text="Pick the First File", command=self.open_file_1)
        self.first_button.grid(row=1, column=0, sticky=W)

        self.second_button = Button(self.myContainer, text="Pick the Second File", command=self.open_file_2)
        self.second_button.grid(row=2, column=0, sticky=W)

        #Set defaults for testing
        self.filename_1 = 'C:\\Users\\germap01\\Python\\UNSORTED\\Hackathon\\2019\\Working\\data_1.csv'
        self.filename_2 = 'C:\\Users\\germap01\\Python\\UNSORTED\\Hackathon\\2019\\Working\\data_2.csv'
        
        #Create a dropdown

        def populateDropdown():

            common_values = list(generate_summary(self.filename_1, self.filename_2)['Metadata']['common_vars'].keys())
            popupMenu['values']=common_values

        dropdownText = "Choose a common variable to plot"
        dropdownLabel=Label(self.myContainer, text=dropdownText, wraplength=110, anchor=W, justify=LEFT)
        dropdownLabel.grid(row=3, column=0, pady=(5,20), sticky=W)

        self.choices = ['None']
        popupMenu = ttk.Combobox(self.myContainer, values=self.choices, postcommand=populateDropdown)
        popupMenu.grid(row=3, column=1, padx=10, pady=(5,20), sticky=W)
        popupMenu.current(0)

        # on change dropdown value
        def callbackFunc(event):
            self.var_to_plot = popupMenu.get()
    
        popupMenu.bind("<<ComboboxSelected>>", callbackFunc)

        self.jinja_button = Button(self.myContainer, text="MAGIC!", command=self.run_jinja)
        self.jinja_button.grid(row=4, column=0, sticky=W)

        self.close_button = Button(self.myContainer, text="CLOSE APP", command=self.myContainer.quit)
        self.close_button.grid(row=5, column=0, sticky=W)

    #FUNCTIONS:
    def open_file_1(self):
        self.filename_1 = filedialog.askopenfilename(initialdir = os.getcwd(), title = "Select file")
    
    def open_file_2(self):
        self.filename_2 = filedialog.askopenfilename(initialdir = os.getcwd(), title = "Select file")

    def run_jinja(self):
        generate_report(self.filename_1, self.filename_2, self.var_to_plot)

root = Tk()
root.geometry("320x400")
my_gui = BasicGUI(root)

#Position the myContainer in the middle of the Main Window 3x3 grid
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(2, weight=1)

#RUN TKINTER LOOP
root.mainloop()