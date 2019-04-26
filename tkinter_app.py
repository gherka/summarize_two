from tkinter import Tk, Label, Button, filedialog, StringVar, OptionMenu, Frame, Toplevel, Message, Radiobutton
from tkinter import W, E, LEFT
from tkinter import ttk
import os
import pandas as pd

from core.jinja_app import generate_report
from core.summary_stats import generate_common_vars, generate_summary
from core.helper_funcs import read_data, dtype_mapping
from core.mp_distributions import controller, worker

class GroupedRadioButton(Radiobutton):
    """
    Extend RadioButton class to add a setter and getter methods for group name
    """
    def set_group_name(self, name):
        self.group = name

    def get_group_name(self):
        return self.group

class DataTypePopup:
    def __init__(self, gui, master):
        #save the master reference for internal use
        self.mainMaster = master
        self.mainGui = gui
        self.toplevel = Toplevel(master)
        self.toplevel.title("Data types")

        #to take full advantage of the grid system, create a Frame to position it within TopLevel
        self.popup = Frame(self.toplevel)
        self.popup.grid(row=0, column=1)

        #set size of blank "padding" columns for text to run across
        self.popup.grid_columnconfigure(0, minsize=50)
        self.popup.grid_columnconfigure(3, minsize=50)

        #resizing the window pushes the extra space into egde columns
        self.toplevel.grid_rowconfigure(1, weight=1)
        self.toplevel.grid_rowconfigure(2, weight=1)
        self.toplevel.grid_columnconfigure(0, weight=1)
        self.toplevel.grid_columnconfigure(2, weight=1)

        self.popup_headline = "Please confirm data types for each common variable:"
        Label(self.popup, text=self.popup_headline, font=("Helvetica", 12), pady=8, padx=10).grid(row=0, columnspan=5, sticky=W+E)

        self.dtype_radio_dict = {}
        self.dtype_choices = ['Categorical', 'Continuous', 'Timeseries']

        #Create the header row
        for i, val in enumerate(self.dtype_choices):
            #keep the first column empty for row headers
            Label(self.popup, text=f"{val}", pady=10, font=("Helvetica", 10)).grid(row=1, column=i+1)

        #Create radio button "rows" and put grouped radio buttons into a dictionary for group lookup
        self.radio_groups = {}

        for i, var in enumerate(gui.common_values):

            self.radio_groups[var] = []

            self.dtype_radio_dict[var] = StringVar()
            self.dtype_radio_dict[var].set(dtype_mapping(gui.dtypes[var]))

            #first row is headline, second row is headers
            Label(self.popup, text=f"{var}", font=("Helvetica", 10), padx=3).grid(row=i+2, column=0, sticky=W)

            for j, val in enumerate(self.dtype_choices):
            
                btn = GroupedRadioButton(
                                self.popup,
                                text="",
                                variable=self.dtype_radio_dict[var],
                                value=val,
                                background='bisque' if val == self.dtype_radio_dict[var].get() else self.toplevel['bg'],
                                padx=5,
                                pady=5
                                )
                #set the group name and append to the dict
                btn.set_group_name(var)
                self.radio_groups[var].append(btn)

                #bind the button click to a function
                btn.bind("<Button-1>", lambda e, w=btn: self.RadioButtonClick(w))

                #position the radio button
                btn.grid(row=i+2, column=j+1)

        #Create Confirm and Exit button
        Button(self.popup, text="Done", command=self.ConfimDataTypes, padx=5, pady=5).grid(row=i+3, column=4)

    #CLASS FUNCTIONS:
    def RadioButtonClick(self, widget):
        """
        Change background colour of the selected radio button
        """
        for w in self.radio_groups[widget.get_group_name()]:
            
            if w is widget:
                w.configure(background='bisque')
            else:
                w.configure(background=self.toplevel['bg'])

    def ConfimDataTypes(self):
        """
        Overwrite dtypes dictionary from main GUI and exit popup
        """
        self.mainGui.dtypes = {key:value.get() for key, value in self.dtype_radio_dict.items()}
        self.toplevel.destroy()

class BasicGUI:
    def __init__(self, master):

        self.master = master
        self.ridge = False #Temporary workaround
        master.title("Dataset comparison tool")

        self.mainContainer = Frame(master)
        self.mainContainer.grid(row=0, column=1)

        self.label = Label(self.mainContainer, text="Use the buttons to operate the tool!")
        self.label.grid(row=0, column=0, columnspan=2, pady=10, padx=5)

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

        #Ask the user to confirm datatypes
        self.dt_button = Button(self.mainContainer, text="Confirm datatypes", command=self.confirm_dt)
        self.dt_button.grid(row=4, column=0, sticky=W)
        
        #Ridge Plot with Multiprocessing
        self.test_button = Button(self.mainContainer, text="Ridge Plot", command=self.ridge_plot)
        self.test_button.grid(row=5, column=0, sticky=W)

        #Magic Button
        self.jinja_button = Button(self.mainContainer, text="MAGIC!", command=self.run_jinja)
        self.jinja_button.grid(row=6, column=0, sticky=W)

        #Close App Button
        self.close_button = Button(self.mainContainer, text="CLOSE APP", command=self.mainContainer.quit)
        self.close_button.grid(row=7, column=0, sticky=W)


    #CLASS FUNCTIONS:
    def open_file_1(self):
        self.filename_1 = filedialog.askopenfilename(initialdir = os.getcwd(), title = "Select file")
    
    def open_file_2(self):
        self.filename_2 = filedialog.askopenfilename(initialdir = os.getcwd(), title = "Select file")

    def ready_datasets(self):
        #Datasets are read in once for the life-time of the GUI; passed by reference to other modules
        self.df1, self.df2 = read_data(self.filename_1, self.filename_2)
        self.common_values = generate_common_vars(self.df1, self.df2)
        self.dtypes = self.df1[self.common_values].dtypes.to_dict()

    def confirm_dt(self):
        #self is the my_gui object (instacne of the BasicGUI class), self.master is root widget 
        DataTypePopup(self, self.master)

    def clean_up(self):

        img_path = os.path.join(os.getcwd(),'Static', 'Images')

        for item in os.listdir(img_path):
            if item.endswith(".png"):
                os.remove(os.path.join(img_path, item))

    def ridge_plot(self):
        self.ridge = True
        self.ridge_spec = {}
        self.ridge_spec['cols'] = ['loc_name', 'sex_age']
        self.ridge_spec['num_col'] = 'stays'
        self.ridge_spec['indices'] = controller(self.filename_1, self.filename_2, ['loc_name', 'sex_age'], 'stays')

    def run_jinja(self):
        self.clean_up()

        if self.ridge:
            generate_report(self.df1, self.df2, self.dtypes, self.ridge_spec)
        else:
            generate_report(self.df1, self.df2, self.dtypes)


if __name__ == "__main__":

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