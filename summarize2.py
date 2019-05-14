from tkinter import Tk, Label, Button, filedialog, StringVar, OptionMenu, Frame, Toplevel, Message, Radiobutton, Listbox, Scrollbar, Canvas
from tkinter import S, N, W, E, CENTER, LEFT, EXTENDED, FLAT
from tkinter import ttk
import os
import pandas as pd

from core.jinja_app import generate_report
from core.summary_stats import generate_common_columns, generate_summary
from core.helper_funcs import read_data, map_dtype
from core.mp_distributions import launch_controller

class PopUp:
    '''
    Base class for creating a popup window and positioning its contents correctly.
    Keeps the naming convention of inherited objects consistent between different
    popups as they refer to the same things.
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
        self.popup.grid_columnconfigure(2, minsize=50)

        #resizing the window pushes the extra space into egde columns
        self.toplevel.grid_rowconfigure(1, weight=1)
        self.toplevel.grid_rowconfigure(2, weight=1)
        self.toplevel.grid_columnconfigure(0, weight=1)
        self.toplevel.grid_columnconfigure(2, weight=1)

        #set font defaults
        self.button_font = "Helvetica 9"

class DataTypePopUp(PopUp):
    '''
    Popup window to allow users to amend default data types.
    '''
    def __init__(self, gui, master):
        super().__init__(gui, master)
        '''
        This function uses a number of dictionaries, internal and external:

        INTERNAL:
            self.dtype_radio_dict:
            has the form of {'column_name':'column_dtype'}

            self.radio_groups:
            has the form of {'column_name':[Button1 (Categorical), Button2, Button3], }

        EXTERNAL:
            mainGui.dtypes:
            is the exported copy of self.dtype_radio_dict
    
        '''    
        self.toplevel.title("Data types")
        self.dtype_radio_dict = {}
        self.radio_groups = {}
        self.dtype_choices = ["Categorical", "Continuous", "Timeseries"]

        self.popup_headline = "Please confirm data types for each common variable:"
        Label(self.popup, text=self.popup_headline, font=("Helvetica", 12), pady=8, padx=10).grid(row=0, columnspan=5, sticky=W+E)

        #SCROLLBAR CHECK
        if len(gui.common_columns) > 10:
            #canvas_frame is the parent of the canvas object which is the parent of canvas_popup frame; 
            canvas_frame = Frame(self.popup, bd=2, relief=FLAT)
            canvas_frame.grid(row=1, column=1,sticky=N)

            yscrollbar = Scrollbar(canvas_frame)
            yscrollbar.grid(row=0, column=1, sticky=N+S, padx=10)

            canvas = Canvas(canvas_frame, bd=0, scrollregion=(0, 0, 400, 1000),
                            yscrollcommand=yscrollbar.set, width=600, height=400)
            canvas.grid(row=0, column=0, sticky=N+S+E+W)

            yscrollbar.config(command=canvas.yview)

            canvas_popup = Frame(canvas)

            self.btn_frame = canvas_popup
            canvas_popup_id = canvas.create_window(0, 0, window=self.btn_frame, anchor=N+W)
        else:
            self.btn_frame = self.popup

        #Create the header row
        for i, dtype in enumerate(self.dtype_choices):
            #keep the first column empty for row headers (columns=i+1, i.e starting from 1, not 0)
            Label(self.btn_frame, text=f"{dtype}", pady=10, font=("Helvetica", 10)).grid(row=1, column=i+1)           

        #Create radio button "rows" and group radio buttons together based on their common column
        #For each common column the nested loop runs three times (once for each dtype)
        for i, col in enumerate(gui.common_columns):
            
            self.radio_groups[col] = []

            #set initial column_dtypes and use tk's StringVar() to keep track of any user changes
            self.dtype_radio_dict[col] = StringVar()
            self.dtype_radio_dict[col].set(map_dtype(gui.dtypes[col]))

            #first row is headline, second row is headers (row=i+2)
            Label(self.btn_frame, text=f"{col}", font=("Helvetica", 10), padx=3).grid(row=i+2, column=0, sticky=W)

            for j, dtype in enumerate(self.dtype_choices):
            
                btn = Radiobutton(
                                self.btn_frame,
                                text="",
                                variable=self.dtype_radio_dict[col],
                                value=dtype,
                                background="bisque" if dtype == self.dtype_radio_dict[col].get() else self.toplevel["bg"],
                                padx=5,
                                pady=5
                                )
                #set the group name as instance attribute and append each radio button (3x) to the dict
                btn.group_col = col
                self.radio_groups[col].append(btn)

                #bind the button click to a function
                btn.bind("<Button-1>", lambda e, w=btn: self.RadioButtonClick(w))

                #position the radio button
                btn.grid(row=i+2, column=j+1)

        #Create Confirm and Exit button
        Button(self.btn_frame, text="Done", command=self.ConfimDataTypes, padx=5, pady=5).grid(row=i+3, column=3)

        #Resize the canvas scrollable area and width after the buttons are drawn
        if len(gui.common_columns) > 10:
            Tk.update(self.btn_frame)
            canvas.config(scrollregion=(0,0, 400, self.btn_frame.winfo_height() + 100 ))
            canvas.config(width=self.btn_frame.winfo_width())

    ###########################
    # DATA TYPE CLASS METHODS #
    ###########################

    def RadioButtonClick(self, widget):
        '''
        Change background colour of the selected radio button
        by looping through all three radio buttons that share
        the same group_col name and checking which one matches
        the widget (radio button) that triggered the function call.
        '''
        for w in self.radio_groups[widget.group_col]:
            
            if w is widget:
                w.configure(background="bisque")
            else:
                w.configure(background=self.toplevel["bg"])

    def ConfimDataTypes(self):
        '''
        Overwrite dtypes dictionary from main GUI, enable report buttons and exit popup

        Due to how tkinter stores user selections (StringVar()) for radio-buttons,
        we need to .get() them first and then create a dictionary for export.
        '''
        self.mainGui.dtypes = {key:value.get() for key, value in self.dtype_radio_dict.items()}
        self.mainGui.dt_confirm.config(text="Done!", font="Helvetica 9 italic")
        self.mainGui.jinja_button.config(state="normal")
        self.mainGui.ridge_button.config(state="normal")
        self.toplevel.destroy()

class RidgePopUp(PopUp):
    '''
    Pop up window to with Ridge Plot options
    '''

    def __init__(self, gui, master):
        super().__init__(gui, master)

        self.toplevel.title("Ridge Plot options")

        self.explainer_text = '''Ridge plot shows a comparison of distributions across selected columns.\n
        Please be aware that computing comparisons for a large number of combinations can be CPU-intensive'''

        self.explainer = Label(self.popup, text=self.explainer_text, font=self.button_font, wraplength=300)
        self.explainer.grid(row=0, column=0, columnspan=2, sticky=W+E)

        #Add a dropdown to select numerical column for distribution analysis
        self.dropdown_label = Label(self.popup, text="Select numerical value", font=self.button_font)
        self.dropdown_label.grid(row=1, column=0, pady=10)

        self.choices = ["None"]
        self.dropdown = ttk.Combobox(self.popup, values=self.choices, postcommand=self.populateDropdown)
        self.dropdown.grid(row=2, column=0, sticky=N)
        self.dropdown.current(0)
        #on change dropdown value
        self.dropdown.bind("<<ComboboxSelected>>", self.callbackFunc)

        #Add a listbox with multiple select
        self.list_label = Label(self.popup, text="Select columns to combine for distribution analysis",
                                font=self.button_font, wraplength=150)
        self.list_label.grid(row=1, column=1, pady=(10,0))

        self.listbox = Listbox(self.popup, selectmode=EXTENDED)
        self.listbox.grid(row=2, column=1)

        self.cat_cols = [key for key in self.mainGui.dtypes.keys() if self.mainGui.dtypes[key] == "Categorical"]

        for i, var in enumerate(self.cat_cols):
            self.listbox.insert(i, var)
   
        #Confirm and Exit
        self.confirm_btn = Button(self.popup, text="Confirm", font=self.button_font, command=self.confirm_ridge)
        self.confirm_btn.grid(row=3, column=0)

    #############################
    # RIDGE POPUP CLASS METHODS #
    #############################

    def populateDropdown(self):
        '''
        Import Continuous common column names from BasicGui.
        Remember that the form of mainGui.dtypes is {'column_name':'column_dtype'}
        '''
        num_cols = [key for key in self.mainGui.dtypes.keys() if self.mainGui.dtypes[key] == "Continuous"]

        self.dropdown["values"]=num_cols

    def callbackFunc(self, event):
        '''
        Export the user selected numerical column name to the master (mainGui)
        '''
        self.mainGui.ridge_spec["num_col"] = self.dropdown.get()

    def confirm_ridge(self):
        '''
        Update the ridge_spec dictionary in the mainGui with user selections
        and indicate to the report generator that a Ridge Plot needs to be built.
        '''
        self.mainGui.ridge=True
        self.mainGui.ridge_spec["cols"] = [self.cat_cols[i] for i in self.listbox.curselection()]
        #launch the multiprocessing script
        self.mainGui.ridge_spec["indices"] = launch_controller(self.mainGui.filename_1, self.mainGui.filename_2,
                                                self.mainGui.ridge_spec["cols"], self.mainGui.ridge_spec["num_col"])
        #indicate the success by turning the ridge button green
        self.mainGui.ridge_button.config(bg="pale green3")
        self.toplevel.destroy()

class BasicGUI:
    '''
    Main user interface of the tool
    '''

    def __init__(self, master):

        self.button_font = "Helvetica 9"
        
        self.master = master
        self.ridge = False
        self.reset = False
        self.ridge_spec = {}

        master.title("Dataset comparison tool")

        self.mainContainer = Frame(master)
        self.mainContainer.grid(row=0, column=1)

        #<<<< FIRST ROW OF GUI >>>>#

        welcome_text = '''This tool generates an HTML report with various metrics to compare two datasets.
        \nFollow the steps below:'''

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
        #Optional elements of the report, like ridge plot or data table (TO DO)

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

    def reset_tool(self):
        '''
        After user re-selects a file, the tool resets to default view
        to avoid buggy situations and to make interaction flow
        more logical by disabling downstream buttons until pre-requisite
        selections had been made.
        '''
        self.ridge=False
        self.file_label_1.config(text="")
        self.file_label_2.config(text="")
        self.dt_confirm.config(text="")
        self.dt_button.config(state="disabled")
        self.ridge_button.config(state="disabled")
        self.ridge_button.config(bg="#f0f0ed")
        self.jinja_button.config(state="disabled")
        self.jinja_button.config(bg="#f0f0ed")

    def open_file_1(self):
        
        if self.reset:
            self.reset_tool()
            self.reset = False

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

        if self.reset:
            self.reset_tool()
            self.reset = False

        #TASK 1
        self.filename_2 = filedialog.askopenfilename(initialdir = os.getcwd(), title = "Select file")
        #TASK 2
        self.df1, self.df2 = read_data(self.filename_1, self.filename_2)
        self.common_columns = generate_common_columns(self.df1, self.df2)
        self.dtypes = self.df1[self.common_columns].dtypes.to_dict()
        #TASK 3
        self.file_label_2.config(text= "Done!", font="Helvetica 9 italic")
        self.dt_button.config(state='normal')


    def confirm_dt(self):
        '''
        Launches the datatypes popup
        self is the my_gui object (instacne of the BasicGUI class),
        self.master is root widget 
        '''
        DataTypePopUp(self, self.master)

    def ridge_plot(self):
        '''
        Launches the ridge plot config popup
        '''
        RidgePopUp(self, self.master)
        

    def run_jinja(self):
        '''
        Main report generating function that ties everything together
        '''

        if self.ridge:
            generate_report(self.df1, self.df2, self.dtypes, self.ridge_spec)
        else:
            generate_report(self.df1, self.df2, self.dtypes)

        #indicate success by turning the button green
        self.jinja_button.config(bg="pale green3")
        #launch the report HTML in the default browser - only on Windows
        os.startfile(os.path.join(os.getcwd(), "report.html"))
        #reset tool to its initial state
        self.reset = True

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