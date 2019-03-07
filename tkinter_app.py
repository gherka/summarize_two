'''
Use subprocess call to add support for running external scripts
'''

from tkinter import Tk, Label, Button, filedialog, StringVar, OptionMenu, Frame, W, LEFT
from tkinter import ttk
import os
import pandas as pd

from jinja_app import generate_report
from summary_stats import generate_summary
from helper_funcs import read_data

class VisRow:
    def __init__(self, master):
        #save the master reference for internal use
        self.mainMaster = master

        self.visContainer = Frame(master.mainContainer)

        self.dropdownText = "Choose a common variable to plot"
        self.dropdownLabel=Label(self.visContainer, text=self.dropdownText, wraplength=110, anchor=W, justify=LEFT)
        self.dropdownLabel.grid(row=0, column=0, pady=(5,20), sticky=W)

        self.choices = ['None']

        self.popupMenu = ttk.Combobox(self.visContainer, values=self.choices, postcommand=self.populateDropdown)
        self.popupMenu.grid(row=0, column=1, padx=10, pady=(5,20), sticky=W)
        self.popupMenu.current(0)

        #on change dropdown value
        self.popupMenu.bind("<<ComboboxSelected>>", self.callbackFunc)

    def populateDropdown(self):
        #import the common values from BasicGui
        self.popupMenu['values']=self.mainMaster.common_values

    def callbackFunc(self, event):
        #export the callback value to the master
        self.mainMaster.var_to_plot = self.popupMenu.get()

class BasicGUI:
    #CHILD OF ROOT (TOP-LEVEL WINDOW)
    def __init__(self, master):

        self.mainContainer = Frame(master)
        self.mainContainer.grid(row=0, column=1)

        self.master = master

        master.title("Dataset comparison tool")

        self.label = (Label(self.mainContainer, text="Use the buttons to operate the tool!")
                            .grid(row=0, column=0, columnspan=2, pady=10, padx=5))

        self.first_button = Button(self.mainContainer, text="Pick the First File", command=self.open_file_1)
        self.first_button.grid(row=1, column=0, sticky=W)

        self.second_button = Button(self.mainContainer, text="Pick the Second File", command=self.open_file_2)
        self.second_button.grid(row=2, column=0, sticky=W)

        #Set defaults for testing; don't forget to press Ready Datasets to read them in
        self.filename_1 = 'C:\\Users\\germap01\\Python\\UNSORTED\\Hackathon\\2019\\Working\\data_1.csv'
        self.filename_2 = 'C:\\Users\\germap01\\Python\\UNSORTED\\Hackathon\\2019\\Working\\data_2.csv'

        #Read in the datasets and generate common values
        self.ready_button = Button(self.mainContainer, text="Read in datasets", command=self.ready_datasets)
        self.ready_button.grid(row=3, column=0, sticky=W)
        
        #Create the first vis row:
        self.visrow_1 = VisRow(self)
        self.visrow_1.visContainer.grid(row=4, column=0, columnspan=2)

        #Magic Button
        self.jinja_button = Button(self.mainContainer, text="MAGIC!", command=self.run_jinja)
        self.jinja_button.grid(row=5, column=0, sticky=W)

        #Close App Button
        self.close_button = Button(self.mainContainer, text="CLOSE APP", command=self.mainContainer.quit)
        self.close_button.grid(row=6, column=0, sticky=W)

    #FUNCTIONS:
    def open_file_1(self):
        self.filename_1 = filedialog.askopenfilename(initialdir = os.getcwd(), title = "Select file")
    
    def open_file_2(self):
        self.filename_2 = filedialog.askopenfilename(initialdir = os.getcwd(), title = "Select file")

    def ready_datasets(self):
        #Datasets are read in once for the life-time of the GUI; passed by reference to other modules
        self.df1, self.df2 = read_data(self.filename_1, self.filename_2)
        self.common_values = list(generate_summary(self.df1, self.df2)['Metadata']['common_vars'].keys())

    def run_jinja(self):
        generate_report(self.df1, self.df2, self.var_to_plot)

root = Tk()
root.geometry("320x400")
my_gui = BasicGUI(root)

#Position the mainContainer in the middle of the root window's 3x3 grid
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(2, weight=1)

#RUN TKINTER LOOP
root.mainloop()