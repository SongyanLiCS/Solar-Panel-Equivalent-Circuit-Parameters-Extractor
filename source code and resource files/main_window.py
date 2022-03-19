##################################################################################
# This is the code for the extractor's main window.
# Application version v1.0
# The GUI was developed and tested using Python version 3.9.6 with Tkinter version 8.6.
# The extractor solver was developed using scipy 1.7.3
##################################################################################
# Importing needed packages.
import tkinter as tk
from tkinter import filedialog
import tkinter.ttk as ttk
from PIL import Image, ImageTk
from extractor_state import ExtractorState
import json
from os import getcwd

from short_circuit_window import ShortCircuitWindow
from open_circuit_window import OpenCircuitWindow

# Define the main window's class
class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        # Set the main window parameters.
        self.title("solar panel equivalent circuit parameters extractor".title())
        self.geometry("750x580+300+150")
        # Previously the window was not resaizable.
        #self.resizable(False, False)
        image_icon = tk.PhotoImage(file = "resource files\\solar_panel_icon_png.png")
        self.iconphoto(False, image_icon)

        # The extractor's state class. Used to keep track of the extractor's state
        # and start extracting parameters. 
        self.extractor_state = ExtractorState(self)

        # Set open and save file types
        # Currently the save file type is .json.
        self.open_save_file_extensions = ["*.json"]
        self.osftypes = [    
            (".json", self.open_save_file_extensions), 
        ]

        # The variable that is used to track if a file is opened.
        self.open_file = None

        # Add the menu bar at the top of the window.
        self.menu = tk.Menu(self, bg="lightgrey", fg="black")
        sub_menu_items = ["file", "edit", "tools", "help"]
        self.configure(menu=self.menu)# This adds the menu.
        self.generate_sub_menus(sub_menu_items)

        # Set various items in each sections represented by the LabelFrames.
        self.datasheet_data_items = ["v_oc_stc", "i_sc_stc", "v_mp", "i_mp",
         "temp_coeff_v_perc", "temp_coeff_i_perc", "n_cell"]
        self.environment_data_items = ["temperature_c", "solar_irr"]
        self.iv_curve_data_items = ["di_dv_sc", "di_dv_oc"]
        self.initial_values_items = ["a_init", "r_s_init"]

        self.all_input_items = self.datasheet_data_items + self.environment_data_items + self.iv_curve_data_items\
            + self.initial_values_items

        self.extractor_items = ["i_ph", "a", "i_o", "r_s", "r_sh"]

        self.all_items = self.all_input_items + self.extractor_items
        # Set the text to be shown in each label using Python's dictionary.
        self.label_text_hash_table = {
            # Datasheet data:
            "v_oc_stc": "Open circuit voltage V_oc in STC (V):",
            "i_sc_stc": "Short circuit current I_sc in STC (A):",
            "v_mp": "Max power voltage (V):",
            "i_mp": "Max power current (A):",
            "temp_coeff_v_perc": "Temperature coefficient of V_oc (%/°C):",
            "temp_coeff_i_perc": "Temperature coefficient of I_sc (%/°C):",
            "n_cell": "Number of cells per panel N_cell:",
            # Environment data:
            "temperature_c": "Environment temperature (°C):",
            "solar_irr": "Solar irradiance (W/m\u00B2):",
            # I-V curve tangent slopes:
            "di_dv_sc": "dI/dV near short circuit (A/V):",
            "di_dv_oc": "dI/dV near open circuit (A/V):",
            # Initial values:
            "a_init": "The initial value of the diode ideality factor, a:",
            "r_s_init": "The initial value of R_s (Ω):",
            # Extractor solutions:
            "i_ph": "Photogenerated current I_L (A):",
            "a": "Diode ideality factor, a:",
            "i_o": "Diode reverse saturation current I_o (A):",
            "r_s": "Series resistance R_s (Ω):",
            "r_sh": "Shunt resistance R_sh (Ω):",
        }
        # The organization of the items and the labels' texts may not be optimal here.
        # One may use multiple dictionaries for the labels texts instead of using 
        # multiple lists for the items in each section and a single dicitionary for the texts.

        # Use hash tables to store some widgets and tkinter variables for easy access.
        self.labels = {}
        self.entries = {}
        self.string_vars = {}
        self.buttons = {}
    #
        # Within the top big area, the left most part is for the input and the buttons.
        # grid() is used in this top big area. (2x3 grid)
        # The input area has four sub-sections, 
        # all represented using frames (the first three are label frames).
        # The sub-sections are packed.
        self.create_data_area_state_bar()

        self.create_input_data_frames()
        self.create_input_data_widgets()
        self.create_circuit_frame()
        self.create_extractor_frame()
        self.create_solution_widgets()
        #self.create_error_frame()

        # Add the extract button.
        self.buttons["extract"] = ttk.Button(self.input_area, text="Extract", comman=self.start_extration)
        self.buttons["extract"].pack(fill=tk.BOTH, padx=5, pady=(5,0))

    def create_data_area_state_bar(self):
        # The top big area for showing the data and buttons.
        self.data_frame = tk.Frame(self)
        self.data_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.data_frame.rowconfigure(0, weight=1)
        self.data_frame.columnconfigure(0, weight=1)
        self.data_frame.rowconfigure(1, weight=1)
        self.data_frame.columnconfigure(1, weight=1)
        self.data_frame.columnconfigure(2, weight=1)

        # The bottom state bar.
        self.execution_state = tk.StringVar()
        self.execution_state.set("Ready...")
        self.state_bar = tk.Label(self, textvariable=self.execution_state, bg="lightgrey",
        anchor=tk.E, justify=tk.LEFT,  relief = tk.FLAT)
        self.state_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_extractor_frame(self):
        # The bigger frame contains the frames for the solutions
        self.extractor_frame = tk.Frame(self.data_frame)
        self.extractor_frame.grid(row=1, column=1, rowspan=1, columnspan=1, sticky=tk.NW)
        self.extractor_frame.rowconfigure(0,weight=1)
        self.extractor_frame.columnconfigure(0,weight=1)
        # Create the frame for the solution values.
        self.solution_values_frame = ttk.LabelFrame(self.extractor_frame, text="Extracted parameters")
        self.solution_values_frame.pack(fill=tk.X, expand=1, padx=1, pady=1)
    


    def create_circuit_frame(self):
        # Create the figure frame and the figure itself using the Canvas widget.
        self.diagram_frame = ttk.LabelFrame(self.data_frame, text="Solar panel equivalent circuit")
        self.diagram_frame.grid(row=0, column=1, rowspan=1, columnspan=1, sticky=tk.NW, padx=(1,5), pady=(10,1))
        # Put the canvas.
        self.circuit_canvas = tk.Canvas(self.diagram_frame, bg="white", width=340, height=320)
        self.circuit_canvas.pack(fill=tk.BOTH)
        self.circuit_image = Image.open("resource files\\solar_cell_equivalent_circuit.png")
        self.resized_circuit_image = self.circuit_image.resize((260, 320))
        self.circuit_figure =ImageTk.PhotoImage(self.resized_circuit_image)
        self.circuit_canvas.create_image((170,160), image=self.circuit_figure)

    def create_input_data_frames(self):
        # Put the frame on the left in the data area.
        self.input_area = tk.Frame(self.data_frame)
        self.input_area.grid(row=0, column=0, rowspan=2, columnspan=1, sticky=tk.NW)
        # Pack the LabelFrame for the datasheet data.
        self.datasheet_data = ttk.LabelFrame(self.input_area, text="Solar panel datasheet data")
        self.datasheet_data.grid_rowconfigure(0, weight=1)
        self.datasheet_data.grid_columnconfigure(0, weight=1)
        self.datasheet_data.pack(fill=tk.X, expand=1, padx=5, pady=10)
        # Pack the LabelFrame for the environment data.
        self.environment_data = ttk.LabelFrame(self.input_area, text="Environment data")
        self.environment_data.grid_rowconfigure(0, weight=1)
        self.environment_data.grid_columnconfigure(0, weight=1)
        self.environment_data.pack(fill=tk.X, expand=1, padx=5, pady=10)
        # Pack the LabelFrame for the I-V curve tangent slopes.
        self.iv_curve_data = ttk.LabelFrame(self.input_area, text="I-V curve tangent slopes in STC")
        self.iv_curve_data.grid_rowconfigure(0, weight=1)
        self.iv_curve_data.grid_columnconfigure(0, weight=1)
        self.iv_curve_data.pack(fill=tk.X, expand=1, padx=5, pady=10)
        # Create the frame for the initial values.
        self.initial_values_frame = ttk.LabelFrame(self.input_area, text="Nonlinear solver\'s settings")
        self.initial_values_frame.grid_rowconfigure(0, weight=1)
        self.initial_values_frame.grid_columnconfigure(0, weight=1)
        self.initial_values_frame.pack(fill=tk.X, expand=1, padx=5, pady=10)

    def create_input_data_widgets(self):
        # Create the widgets in the datasheet data section.
        row_num = 0
        for item in self.datasheet_data_items:
            self.labels[item] = tk.Label(self.datasheet_data, text=self.label_text_hash_table[item],
            anchor=tk.E, justify=tk.LEFT)
            self.labels[item].grid(sticky = tk.E, row=row_num, column=0, padx=1, pady=1)
            self.string_vars[item] = tk.StringVar()
            self.string_vars[item].set("")
            self.entries[item] = ttk.Entry(self.datasheet_data, textvariable=self.string_vars[item])
            self.entries[item].grid(row=row_num, column=1,padx=1, pady=1, sticky = tk.E)

            row_num += 1

        # Create the widgets in the environment data section.
        row_num = 0
        for item in self.environment_data_items:
            self.labels[item] = tk.Label(self.environment_data, text=self.label_text_hash_table[item],
            anchor=tk.E, justify=tk.LEFT)
            self.labels[item].grid(sticky = tk.E, row=row_num, column=0, padx=1, pady=1)
            self.string_vars[item] = tk.StringVar()
            self.string_vars[item].set("")
            self.entries[item] = ttk.Entry(self.environment_data, textvariable=self.string_vars[item])
            self.entries[item].grid(row=row_num, column=1,padx=1, pady=1, sticky = tk.E)
            
            row_num += 1
 
        # Create the widgets in the I-V curve slopes data section.
        row_num = 0
        for item in self.iv_curve_data_items:
            # For this section, buttons first.
            self.buttons[item] = ttk.Button(self.iv_curve_data, text="Get")
            self.buttons[item].grid(row=row_num, column=0,padx=1, pady=1, sticky = tk.E)    

            self.labels[item] = tk.Label(self.iv_curve_data, text=self.label_text_hash_table[item],
            anchor=tk.E, justify=tk.LEFT)
            self.labels[item].grid(sticky = tk.E, row=row_num, column=1, padx=1, pady=1)
            self.string_vars[item] = tk.StringVar()
            self.string_vars[item].set("")
            self.entries[item] = ttk.Entry(self.iv_curve_data, textvariable=self.string_vars[item])
            self.entries[item].grid(row=row_num, column=2,padx=1, pady=1, sticky = tk.E)
            
            row_num += 1

        self.buttons["di_dv_sc"].configure(command=self.get_di_dv_sc)
        self.buttons["di_dv_oc"].configure(command=self.get_di_dv_oc)

        # Create the widgets for initial values section.
        row_num = 0

        for item in self.initial_values_items:
            self.labels[item] = tk.Label(self.initial_values_frame, text=self.label_text_hash_table[item],
            anchor=tk.E, justify=tk.LEFT)
            self.labels[item].grid(sticky = tk.E, row=row_num, column=0, padx=1, pady=1)
            self.string_vars[item] = tk.StringVar()
            self.string_vars[item].set("")
            self.entries[item] = ttk.Entry(self.initial_values_frame, textvariable=self.string_vars[item])
            self.entries[item].grid(row=row_num, column=1,padx=1, pady=1, sticky = tk.E)

            row_num += 1


    def get_di_dv_sc(self):
        # Open the window to get di/dv for the short circuit condition
        # using a graphical approximation method.
        get_di_dv_window = ShortCircuitWindow(self)


    def get_di_dv_oc(self):
        # Open the window to get di/dv for the open circuit condition
        # using a graphical approximation method.
        get_di_dv_window = OpenCircuitWindow(self)

    def create_solution_widgets(self):
        # Put the widgets in the solution section (extracted parameters).
        row_num = 0
        for item in self.extractor_items:
            self.labels[item] = tk.Label(self.solution_values_frame, text=self.label_text_hash_table[item],
            anchor=tk.E, justify=tk.LEFT)
            self.labels[item].grid(sticky = tk.E, row=row_num, column=0, padx=1, pady=1)
            self.string_vars[item] = tk.StringVar()
            self.string_vars[item].set("")
            self.entries[item] = ttk.Entry(self.solution_values_frame, textvariable=self.string_vars[item],
            state="readonly")
            self.entries[item].grid(row=row_num, column=1,padx=1, pady=1, sticky = tk.E)

            row_num += 1

    def file_open(self, event=None):
        """
        Ctrl+O
        """
        # Open the open file window so that the user can select a previously saved case file.
        self.execution_state.set("Loading a case file...")
        file_to_open = filedialog.askopenfilename(initialdir = getcwd(),title = "Open a case file",filetypes=self.osftypes)
        if file_to_open:
            
            with open(file_to_open, "r", encoding="utf-8") as file:
                data = json.load(file)


            if "file type" in data.keys() and data["file type"] == "solar panel circuit model parameters":
                for item in self.all_items:
                    self.string_vars[item].set(data[item])

                self.open_file = file_to_open
            else:
                tk.messagebox.showerror(title="Wrong file type", 
                message="The selected JSON file is not for this application.")

        self.execution_state.set("Ready...")

    def file_save(self, event=None):
        """
        Ctrl+S
        """
        # Open a window so that the user can save the current case file to use or view it later.
        self.execution_state.set("Saving a case file...")
        current_file = self.open_file if self.open_file else None
        if not current_file:
            current_file = filedialog.asksaveasfilename(initialdir = getcwd(),title = "Save a case file",filetypes=self.osftypes)
        if current_file:
            data = {}
            data["file type"] = "solar panel circuit model parameters"

            for item in self.all_items:
                data[item] = self.string_vars[item].get()
            
            if current_file[-5:].lower() != ".json":
                current_file += ".json"

            with open(current_file, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

        self.execution_state.set("Ready...")

    def file_save_as(self, event=None):
        """
        """
        # If the user wants to save the case file as an another file, this window will be used.
        self.execution_state.set("Saving a case file...")
        current_file = filedialog.asksaveasfilename(initialdir = getcwd(),title = "Save a case file",filetypes=self.osftypes)
        if current_file:
            data = {}
            data["file type"] = "solar panel circuit model parameters"
            for item in self.all_items:
                data[item] = self.string_vars[item].get()
            
            if current_file[-5:].lower() != ".json":
                current_file += ".json"

            with open(current_file, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

            self.open_file = current_file

        self.execution_state.set("Ready...")

    def file_new(self, event=None):
        """
        Ctrl+N
        """
        # Start a new case.
        self.open_file = None
        for item in self.all_input_items:
            self.string_vars[item].set("")

        for item in self.extractor_items:
            self.string_vars[item].set("")

        self.execution_state.set("Ready...")

    def help_about(self, event=None):
        """
        """
        # Show the about window.
        tk.messagebox.showinfo(title="About", 
            message="Solar panel circuit model parameter extractor GUI v1.0.")

    def is_a_number(self, x):
        try:
            float(x)
            return True
        except ValueError:
            return False

    def start_extration(self, event=None):
        # Start extracting the equivalent circuit parameters.
        # First check if all the input entries are given as numbers.
        self.execution_state.set("Validating input entries...")
        entries_all_valid = True
        for item in self.all_input_items:
            if self.is_a_number(str(self.string_vars[item].get())) is False:
                entries_all_valid = False
                
        if entries_all_valid:
            self.execution_state.set("Beginning extracting...")
            self.extractor_state.extract()
        else:
            self.execution_state.set("Invalid input entries...")
            tk.messagebox.showinfo(title="Invalid input", 
            message="Please provide valid numbers as input data in the entries.\nAll entries in the left column must be provided with valid numbers.")
            self.execution_state.set("Ready...")

    def generate_sub_menus(self, sub_menu_items):
        # Use this method to generate the menu bar show at the top of the main window.
        # The file menu:
        sub_menu = tk.Menu(self.menu, tearoff=0, fg="black")
        sub_menu.add_command(label="New", command=self.file_new, accelerator="Ctrl+N")
        self.bind("<Control-n>", self.file_new)
        sub_menu.add_command(label="Open", command=self.file_open, accelerator="Ctrl+O")
        self.bind("<Control-o>", self.file_open)
        sub_menu.add_command(label="Save", command=self.file_save, accelerator="Ctrl+S")
        self.bind("<Control-s>", self.file_save)
        sub_menu.add_command(label="Save As", command=self.file_save_as)
        sub_menu.add_separator()
        sub_menu.add_command(label="Exit", command=self.destroy, accelerator="")
        self.menu.add_cascade(label="File", menu=sub_menu)

        # The help menu:
        sub_menu = tk.Menu(self.menu, tearoff=0, fg="black")
        sub_menu.add_command(label="About", command=self.help_about, accelerator="")
        self.menu.add_cascade(label="Help", menu=sub_menu)

    def get_input_for_extractor(self):
        # Use this method to pass the input to the extractor (another object of another class).
        input_dict = {}
        for item in self.all_input_items:
            input_dict[item] = float(self.entries[item].get())

        return input_dict

    def disable_input_entries(self):
        # Disable all input entries.
        for item in self.all_input_items:
            self.entries[item].configure(state="disable")

    def enable_input_entries(self):
        # Enable all input entries.
        for item in self.all_input_items:
            self.entries[item].configure(state="enable")

    def set_execution_state(self, a_string):
        # Set the execution state to show the string in a_string
        self.execution_state.set(a_string)

    def set_solution_entries(self, solution):
        # Set the solution entries using the variable "solution" given by the extractor.
        self.string_vars["i_ph"].set("{0:.5f}".format(solution["i_ph"]))
        self.string_vars["a"].set("{0:.5f}".format(solution["a"]))
        self.string_vars["i_o"].set("{:.5e}".format(solution["i_o"]))
        self.string_vars["r_s"].set("{0:.5f}".format(solution["r_s"]))
        self.string_vars["r_sh"].set("{0:.5f}".format(solution["r_sh"]))

    def disable_extraction(self):
        # Disable the extract button.
        self.buttons["extract"].configure(state="disable")

    def enable_extraction(self):
        # Enable the extract button.
        self.buttons["extract"].configure(state="enable")

    def set_di_dv_sc(self, di_dv_sc_str):
        # Set the entry for the slope near the short circuit condition.
        self.string_vars["di_dv_sc"].set(di_dv_sc_str)

    def set_di_dv_oc(self, di_dv_oc_str):
        # Set the entry for the slope near the open circuit condition.
        self.string_vars["di_dv_oc"].set(di_dv_oc_str)

if __name__ == "__main__":
    win = MainWindow()
    win.mainloop()