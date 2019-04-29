from tkinter import Tk, Label, Button, filedialog, StringVar, OptionMenu, Frame, Toplevel, Message, Radiobutton, Listbox
from tkinter import W, E, CENTER, LEFT, EXTENDED, N
from tkinter import ttk
import os
import pandas as pd

from core.jinja_app import generate_report
from core.summary_stats import generate_common_vars, generate_summary
from core.helper_funcs import read_data, dtype_mapping
from core.mp_distributions import controller, worker

class PopUp:
    '''
    Base class for creating a popup window
    '''
    def __init__(self, gui, master):
        #save the master reference for internal use
        self.mainMaster = master
        self.mainGui = gui
        self.toplevel = Toplevel(master)

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

        self.button_font = "Helvetica 9"

class GroupedRadioButton(Radiobutton):
    """
    Extend RadioButton class to add a setter and getter methods for group name
    """
    def set_group_name(self, name):
        self.group = name

    def get_group_name(self):
        return self.group

class DataTypePopUp(PopUp):
    '''
    Pop up window to allow users to amend default data types
    '''
    def __init__(self, gui, master):
        super().__init__(gui, master)

        self.toplevel.title("Data types")

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

    ###########################
    # DATA TYPE CLASS METHODS #
    ###########################

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
        Overwrite dtypes dictionary from main GUI, enable report buttons and exit popup
        """
        self.mainGui.dtypes = {key:value.get() for key, value in self.dtype_radio_dict.items()}
        self.mainGui.dt_confirm.config(text="Done!", font="Helvetica 9 italic")
        self.mainGui.jinja_button.config(state='normal')
        self.mainGui.ridge_button.config(state='normal')
        self.toplevel.destroy()

class RidgePopUp(PopUp):
    '''
    Pop up window to with Ridge Plot options
    '''

    def __init__(self, gui, master):
        super().__init__(gui, master)

        self.toplevel.title('Ridge Plot options')

        self.explainer_text = '''Ridge plot shows a comparison of distributions across selected columns.\n
        Please be aware that computing comparisons for a large number of combinations can be CPU-intensive'''

        self.explainer = Label(self.popup, text=self.explainer_text, font=self.button_font, wraplength=300)
        self.explainer.grid(row=0, column=0, columnspan=2, sticky=W+E)

        #Add a listbox with multiple select
        self.list_label = Label(self.popup, text="Select columns to combine for distribution analysis",
                                font=self.button_font, wraplength=100)
        self.list_label.grid(row=1, column=0, pady=(10,0))

        self.listbox = Listbox(self.popup, selectmode=EXTENDED)
        self.listbox.grid(row=2, column=0)


        self.cat_cols = [key for key in self.mainGui.dtypes.keys() if self.mainGui.dtypes[key] == 'Categorical']

        for i, var in enumerate(self.cat_cols):
            self.listbox.insert(i, var)

        #Add a dropdown to select numerical column for distribution analysis
        self.dropdown_label = Label(self.popup, text="Select numerical value", font=self.button_font)
        self.dropdown_label.grid(row=1, column=1, pady=10)

        self.choices = ['None']
        self.dropdown = ttk.Combobox(self.popup, values=self.choices, postcommand=self.populateDropdown)
        self.dropdown.grid(row=2, column=1, sticky=N)
        self.dropdown.current(0)
        #on change dropdown value
        self.dropdown.bind("<<ComboboxSelected>>", self.callbackFunc)
   
        #Confirm and Exit
        self.confirm_btn = Button(self.popup, text="Confirm", font=self.button_font, command=self.confirm_ridge)
        self.confirm_btn.grid(row=3, column=0)

        #Just exit

    
    ###########################
    # BASIC GUI CLASS METHODS #
    ###########################

    def populateDropdown(self):
        #import the common values from BasicGui
        
        num_cols = [key for key in self.mainGui.dtypes.keys() if self.mainGui.dtypes[key] == 'Continuous']

        self.dropdown['values']=num_cols

    def callbackFunc(self, event):
        #export the callback value to the master (my_gui)
        self.mainGui.ridge_spec['num_col'] = self.dropdown.get()

    def confirm_ridge(self):
        self.mainGui.ridge=True
        self.mainGui.ridge_spec['cols'] = [self.cat_cols[i] for i in self.listbox.curselection()]
        self.mainGui.ridge_spec['indices'] = controller(self.mainGui.filename_1, self.mainGui.filename_2,
                                                self.mainGui.ridge_spec['cols'], self.mainGui.ridge_spec['num_col'])

        self.toplevel.destroy()

class BasicGUI:
    '''
    Main user interface of the tool
    '''

    def __init__(self, master):

        self.button_font = "Helvetica 9"

        self.master = master
        self.ridge = False #Temporary workaround
        self.ridge_spec = {}

        master.title("Dataset comparison tool")

        self.mainContainer = Frame(master)
        self.mainContainer.grid(row=0, column=1)

        #<<<< FIRST ROW OF GUI >>>>#
        #Welcome text

        welcome_text = """This tool generates an HTML report with various metrics to compare two datasets.
        \nFollow the steps below:"""

        self.label = Label(self.mainContainer, text=welcome_text,
                          font="Helvetica 12 italic",
                          wraplength=300,
                          justify=LEFT,
                          anchor=W)
        self.label.grid(row=0, column=0, columnspan=3, pady=20, padx=5, sticky=W)

        #<<<< SECOND ROW OF GUI >>>>#
        #Ask user to select datasets for comparison

        self.step_1 = Label(self.mainContainer, text="Step 1",
                            font="Helvetica 12 bold", fg="green")
        self.step_1.grid(row=1, column=0, rowspan=2, padx=(5, 15), pady=10, sticky=W)

        self.first_button = Button(self.mainContainer, text="Pick the First File", font=self.button_font, command=self.open_file_1)
        self.first_button.grid(row=1, column=1, sticky=W)

        self.file_label_1 = Label(self.mainContainer, text="")
        self.file_label_1.grid(row=2, column=1, columnspan=1, pady=5, padx=5)

        self.second_button = Button(self.mainContainer, text="Pick the Second File", font=self.button_font, command=self.open_file_2)
        self.second_button.grid(row=1, column=2, sticky=W)

        self.file_label_2 = Label(self.mainContainer, text="")
        self.file_label_2.grid(row=2, column=2, columnspan=1, pady=5, padx=5)

        #<<<< THIRD ROW OF GUI >>>>#
        #Ask the user to confirm datatypes

        self.step_2 = Label(self.mainContainer, text="Step 2",
                            font="Helvetica 12 bold", fg="green")
        self.step_2.grid(row=3, column=0, rowspan=2, padx=(5, 15), pady=10, sticky=W)
       
        self.dt_button = Button(self.mainContainer, text="Confirm datatypes", font=self.button_font, state="disabled", command=self.confirm_dt)
        self.dt_button.grid(row=3, column=1, sticky=W)

        self.dt_confirm = Label(self.mainContainer, text="")
        self.dt_confirm.grid(row=4, column=1, columnspan=1, pady=5, padx=5)

        #<<<< FOURTH ROW OF GUI >>>>#
        #Optional elements of the report, like ridge plot or data table

        self.step_3 = Label(self.mainContainer, text="Step 3",
                            font="Helvetica 12 bold", fg="green")
        self.step_3.grid(row=5, column=0, rowspan=2, padx=(5, 15), pady=10, sticky=W)

        self.advanced_options = Label(self.mainContainer, text="Optional Report Features", font="Helvetica 11 italic")
        self.advanced_options.grid(row=5, column=1, columnspan=2, pady=5, padx=5)
        
        self.ridge_button = Button(self.mainContainer, text="Ridge Plot", font=self.button_font, state="disabled", command=self.ridge_plot)
        self.ridge_button.grid(row=6, column=1, sticky=W)

        #<<<< LAST ROW OF GUI >>>>#

        #Magic Button
        self.jinja_button = Button(self.mainContainer, text="GENERATE REPORT",
                                   font=self.button_font, state="disabled",
                                   height=3, command=self.run_jinja)
        self.jinja_button.grid(row=7, column=0, columnspan=3, pady=(20,0))


    ###########################
    # BASIC GUI CLASS METHODS #
    ###########################

    def open_file_1(self):
        self.filename_1 = filedialog.askopenfilename(initialdir = os.getcwd(), title = "Select file")
        self.file_label_1.config(text = "Done!", font="Helvetica 9 italic")
    
    def open_file_2(self):
        '''
        This function has two additional tasks apart from
        specifying the file path(1) to the second dataset.

        - It reads in the files as Pandas dataframes(2).
        - It "readies" the "Confirm Datatypes" button (3)

        Note, dataframes are created once for the life-time of the GUI and passed by reference to other modules
        '''
        #TASK 1
        self.filename_2 = filedialog.askopenfilename(initialdir = os.getcwd(), title = "Select file")
        #TASK 2
        self.df1, self.df2 = read_data(self.filename_1, self.filename_2)
        self.common_values = generate_common_vars(self.df1, self.df2)
        self.dtypes = self.df1[self.common_values].dtypes.to_dict()
        #TASK 3
        self.file_label_2.config(text= "Done!", font="Helvetica 9 italic")
        self.dt_button.config(state='normal')

    def confirm_dt(self):
        #self is the my_gui object (instacne of the BasicGUI class), self.master is root widget 
        DataTypePopUp(self, self.master)

    def clean_up(self):

        img_path = os.path.join(os.getcwd(),'Static', 'Images')

        for item in os.listdir(img_path):
            if item.endswith(".png"):
                os.remove(os.path.join(img_path, item))

    def ridge_plot(self):
        # self.ridge = True
        # self.ridge_spec = {}
        # self.ridge_spec['cols'] = ['loc_name', 'sex_age']
        # self.ridge_spec['num_col'] = 'stays'
        # self.ridge_spec['indices'] = controller(self.filename_1, self.filename_2, ['loc_name', 'sex_age'], 'stays')
        # self.ridge_button.config(bg="pale green3")

        RidgePopUp(self, self.master)
        

    def run_jinja(self):
        self.clean_up()

        if self.ridge:
            generate_report(self.df1, self.df2, self.dtypes, self.ridge_spec)
        else:
            generate_report(self.df1, self.df2, self.dtypes)

        self.jinja_button.config(bg="pale green3")
        os.startfile(os.path.join(os.getcwd(), 'hello.html'))
        #reset tool to null state
        self.ridge=False
        self.file_label_1.config(text="")
        self.file_label_2.config(text="")
        self.dt_confirm.config(text="")
        self.dt_button.config(state="disabled")
        self.ridge_button.config(state="disabled")
        self.jinja_button.config(state="disabled")

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