# Define the window class for approximating the slope di/dv near the short circuit condition
# using a graphical approximation method.

import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image, ImageTk
from tkinter import Y, filedialog
from os import getcwd

class ShortCircuitWindow(tk.Toplevel):
    # Define the classes for the cursor and the segement that is used to approximate the tangent.
    class SimpleCursor():
        def __init__(self, x=10, y=10, host_canvas=None, color="blue"):
            self.x = x
            self.y = y
            self.host_canvas = host_canvas
            self.color = color
            self.horizontal_line = self.host_canvas.create_line(self.x, -10000, self.x, 10000, dash=(1, 5), fill=self.color, tags="horizontal")
            self.vertical_line = self.host_canvas.create_line(-10000, self.y, 10000, self.y, dash=(1, 5), fill=self.color, tags="vertical")

        def get_coordinate(self):
            return [self.x, self.y]

        def set_coordinate(self, coordinate):
            self. x = coordinate[0]
            self. y = coordinate[1]

        def move_cursor(self, x, y):
            self.x = x
            self.y = y
            self.host_canvas.coords(self.horizontal_line, self.x, -10000, self.x, 10000)
            self.host_canvas.coords(self.vertical_line, -10000, self.y, 10000, self.y)


    class SimpleSegment():
        def __init__(self, cursor_1, cursor_2, host_canvas=None, color="green"):
            self.cursor_1 = cursor_1 # Keep the references to the cursors.
            self.cursor_2 = cursor_2
            self.host_canvas = host_canvas
            self.color = color
            self.segment = self.host_canvas.create_line(self.cursor_1.get_coordinate()[0], self.cursor_1.get_coordinate()[1], 
            self.cursor_2.get_coordinate()[0], self.cursor_2.get_coordinate()[1],
            width=2, fill=self.color, tags="vertical")
        
        def update_segement(self):
            self.host_canvas.coords(self.segment,
            self.cursor_1.get_coordinate()[0], self.cursor_1.get_coordinate()[1], 
            self.cursor_2.get_coordinate()[0], self.cursor_2.get_coordinate()[1])

            
    # The constructor of the window.
    def __init__(self, main_window, **kwargs):
        super().__init__(**kwargs)
        self.main_window = main_window
        self.title("Approximating the tangent slope near the short circuit condition...")
        self.geometry("1010x710+200+50")
        # Previously the window was not resaizable.
        #self.resizable(False, False)
        image_icon = tk.PhotoImage(file = "resource files\\solar_panel_icon_png.png")
        self.iconphoto(False, image_icon)
        self.grab_set()


        self.i_v_image = None
        self.canvas_i_v_image = None

        self.ftypes = [   
            (".png", "*.png"), 
            (".jpg", "*.jpg"),
        ]

        # Create the label frame that contains a canvas.
        self.image_frame = ttk.LabelFrame(self, text="Load the I-V curve (for STC) near V=0:", 
        width=780, height=680)
        self.image_frame.grid(row=0, column=0, padx=5,pady=5)
        self.canvas_width = 770
        self.canvas_height = 670
        self.i_v_canvas = tk.Canvas(self.image_frame, width=self.canvas_width, height=self.canvas_height, bg="lightgrey")
        self.i_v_canvas.pack()
        # Create cursors.
        self.cursor_1 = self.SimpleCursor(x=10, y=10, host_canvas=self.i_v_canvas)
        self.cursor_2 = self.SimpleCursor(x=50, y=50, host_canvas=self.i_v_canvas, color="red")
        self.segment = self.SimpleSegment(self.cursor_1, self.cursor_2, host_canvas=self.i_v_canvas)
        # The int variable represents which cursor is currently selected.
        self.int_vars = {}
        self.int_vars["cursor"] = tk.IntVar()
        self.int_vars["cursor"].set(1)
        # Make the canvas respond to the event to move cursors.
        self.i_v_canvas.bind("<ButtonPress-1>", self.drag_cursor)
        self.i_v_canvas.bind("<B1-Motion>", self.drag_cursor)
        # Create the frame for buttons, labels and entries.
        self.right_frame = ttk.LabelFrame(self, text="To approximate the slope:", 
        width=200, height=680)
        self.right_frame.grid(row=0, column=1, padx=5,pady=5, sticky=tk.NE)
        self.right_frame.rowconfigure(0, weight=1)
        self.right_frame.columnconfigure(0, weight=1)

        
        self.labels = {}
        self.entries = {}
        self.buttons = {}
        self.radiobuttons = {}
        self.string_vars = {}


        self.create_widgets()

    def drag_cursor(self, event):
        # Update the cursor and the segment.
        x = event.x
        y = event.y
        if self.int_vars["cursor"].get() == 1:
            self.cursor_1.move_cursor(x, y)
        elif self.int_vars["cursor"].get() == 2:
            self.cursor_2.move_cursor(x, y)
            
        self.segment.update_segement()
        # Update the coordinate of the cursors.
        self.update_coordinates(self.cursor_1.get_coordinate()[0], self.cursor_1.get_coordinate()[1], 
        self.cursor_2.get_coordinate()[0], self.cursor_2.get_coordinate()[1])
        

    def create_widgets(self):
        # Create the widgets in the window.
        row_num = 0

        self.frame_load_clear = tk.Frame(self.right_frame)
        self.frame_load_clear.rowconfigure(0, weight=1)
        self.frame_load_clear.columnconfigure(0, weight=1)
        self.frame_load_clear.columnconfigure(1, weight=1)
        self.frame_load_clear.grid(row=row_num, column=0, columnspan=2, stick=tk.EW)
        self.buttons["load"] = ttk.Button(self.frame_load_clear, text="Load Image", command=self.load_image)
        self.buttons["load"].grid(row=0, column=0, padx=1, pady=1, stick=tk.EW)
        self.buttons["clear"] = ttk.Button(self.frame_load_clear, text="Clear Image", command=self.clear_image)
        self.buttons["clear"].grid(row=0, column=1, padx=1, pady=1, stick=tk.EW)
        row_num += 1

        self.separator_1 = ttk.Separator(self.right_frame)
        self.separator_1.grid(row=row_num, column=0, columnspan=3, padx=1, pady=2, sticky=tk.EW)
        row_num += 1

        self.radiobuttons["cursor 1"] =tk.Radiobutton(self.right_frame, variable=self.int_vars["cursor"], text="Cursor 1", value=1, fg="blue")
        self.radiobuttons["cursor 1"].grid(row=row_num, column=0, padx=1, pady=1)
        self.radiobuttons["cursor 2"] =tk.Radiobutton(self.right_frame, variable=self.int_vars["cursor"], text="Cursor 2", value=2, fg="red")
        self.radiobuttons["cursor 2"].grid(row=row_num, column=1, padx=1, pady=1)
        row_num +=1

        self.separator_2 = ttk.Separator(self.right_frame)
        self.separator_2.grid(row=row_num, column=0, columnspan=3, padx=1, pady=2, sticky=tk.EW)
        row_num += 1

        self.labels["delta i"] = tk.Label(self.right_frame, text="|ΔI| (A):", anchor=tk.E, justify=tk.LEFT)
        self.labels["delta i"].grid(row=row_num, column=0, padx=1, pady=1, sticky=tk.E)
        self.string_vars["delta i"] = tk.StringVar()
        self.string_vars["delta i"].set("")
        self.entries["delta i"] = ttk.Entry(self.right_frame, textvariable=self.string_vars["delta i"])
        self.entries["delta i"].grid(row=row_num, column=1, padx=1, pady=1, sticky=tk.W)
        row_num +=1

        self.labels["delta y"] = tk.Label(self.right_frame, text="|Δy| (pixels):", anchor=tk.E, justify=tk.LEFT)
        self.labels["delta y"].grid(row=row_num, column=0, padx=1, pady=1, sticky=tk.E)
        self.string_vars["delta y"] = tk.StringVar()
        self.string_vars["delta y"].set("")
        self.entries["delta y"] = ttk.Entry(self.right_frame, textvariable=self.string_vars["delta y"], state="readonly")
        self.entries["delta y"].grid(row=row_num, column=1, padx=1, pady=1, sticky=tk.W)
        row_num +=1

        self.labels["delta v"] = tk.Label(self.right_frame, text="|ΔV| (V):", anchor=tk.E, justify=tk.LEFT)
        self.labels["delta v"].grid(row=row_num, column=0, padx=1, pady=1, sticky=tk.E)
        self.string_vars["delta v"] = tk.StringVar()
        self.string_vars["delta v"].set("")
        self.entries["delta v"] = ttk.Entry(self.right_frame, textvariable=self.string_vars["delta v"])
        self.entries["delta v"].grid(row=row_num, column=1, padx=1, pady=1, sticky=tk.W)
        row_num +=1

        self.labels["delta x"] = tk.Label(self.right_frame, text="|Δx| (pixels):", anchor=tk.E, justify=tk.LEFT)
        self.labels["delta x"].grid(row=row_num, column=0, padx=1, pady=1, sticky=tk.E)
        self.string_vars["delta x"] = tk.StringVar()
        self.string_vars["delta x"].set("")
        self.entries["delta x"] = ttk.Entry(self.right_frame, textvariable=self.string_vars["delta x"], state="readonly")
        self.entries["delta x"].grid(row=row_num, column=1, padx=1, pady=1, sticky=tk.W)
        row_num +=1


        self.frame_set_delta_xy = tk.Frame(self.right_frame)
        self.frame_set_delta_xy.grid(row=row_num, column=0, columnspan=2, stick=tk.EW)
        self.frame_set_delta_xy.rowconfigure(0, weight=1)
        self.frame_set_delta_xy.columnconfigure(0, weight=1)
        self.frame_set_delta_xy.columnconfigure(1, weight=1)
        self.buttons["set delta y"] = ttk.Button(self.frame_set_delta_xy, text="Set |Δy|", command=self.set_delta_y)
        self.buttons["set delta y"].grid(row=row_num, column=0, padx=1, pady=1, sticky=tk.EW)
        self.buttons["set delta x"] = ttk.Button(self.frame_set_delta_xy, text="Set |Δx|", command=self.set_delta_x)
        self.buttons["set delta x"].grid(row=row_num, column=1, padx=1, pady=1, sticky=tk.EW)
        row_num +=1

        self.separator_3 = ttk.Separator(self.right_frame)
        self.separator_3.grid(row=row_num, column=0, columnspan=3, padx=1, pady=2, sticky=tk.EW)
        row_num += 1

        self.labels["coordinate 1"] = tk.Label(self.right_frame, text="(x1, y1):", anchor=tk.E, justify=tk.LEFT)
        self.labels["coordinate 1"].grid(row=row_num, column=0, padx=1, pady=1, sticky=tk.E)
        self.string_vars["coordinate 1"] = tk.StringVar()
        self.string_vars["coordinate 1"].set("("+str(self.cursor_1.get_coordinate()[0])+", "+str(self.cursor_1.get_coordinate()[0])+")")
        self.entries["coordinate 1"] = ttk.Entry(self.right_frame, textvariable=self.string_vars["coordinate 1"], state="readonly")
        self.entries["coordinate 1"].grid(row=row_num, column=1, padx=1, pady=1, sticky=tk.W)
        row_num += 1

        self.labels["coordinate 2"] = tk.Label(self.right_frame, text="(x2, y2):", anchor=tk.E, justify=tk.LEFT)
        self.labels["coordinate 2"].grid(row=row_num, column=0, padx=1, pady=1, sticky=tk.E)
        self.string_vars["coordinate 2"] = tk.StringVar()
        self.string_vars["coordinate 2"].set("("+str(self.cursor_2.get_coordinate()[0])+", "+str(self.cursor_2.get_coordinate()[0])+")")
        self.entries["coordinate 2"] = ttk.Entry(self.right_frame, textvariable=self.string_vars["coordinate 2"], state="readonly")
        self.entries["coordinate 2"].grid(row=row_num, column=1, padx=1, pady=1, sticky=tk.W)
        row_num += 1

        self.separator_4 = ttk.Separator(self.right_frame)
        self.separator_4.grid(row=row_num, column=0, columnspan=3, padx=1, pady=2, sticky=tk.EW)
        row_num += 1

        self.labels["tangent slope"] = tk.Label(self.right_frame, text="dI/dV (A/V):", anchor=tk.E, justify=tk.LEFT)
        self.labels["tangent slope"].grid(row=row_num, column=0, padx=1, pady=1, sticky=tk.E)
        self.string_vars["tangent slope"] = tk.StringVar()
        self.string_vars["tangent slope"].set("")
        self.entries["tangent slope"] = ttk.Entry(self.right_frame, textvariable=self.string_vars["tangent slope"], state="readonly")
        self.entries["tangent slope"].grid(row=row_num, column=1, padx=1, pady=1, sticky=tk.W)
        row_num += 1

        self.buttons["calculate slope"] = ttk.Button(self.right_frame, text="Calculate", command=self.calculate_slope)
        self.buttons["calculate slope"].grid(row=row_num, column=0, columnspan=2, padx=1, pady=1, sticky=tk.EW)
        row_num += 1

        self.separator_5 = ttk.Separator(self.right_frame)
        self.separator_5.grid(row=row_num, column=0, columnspan=3, padx=1, pady=2, sticky=tk.EW)
        row_num += 1

        self.frame_apply_cancel = tk.Frame(self.right_frame)
        self.frame_apply_cancel.grid(row=row_num, column=0, columnspan=2, stick=tk.EW)
        self.frame_apply_cancel.rowconfigure(0, weight=1)
        self.frame_apply_cancel.columnconfigure(0, weight=1)
        self.frame_apply_cancel.columnconfigure(1, weight=1)
        self.buttons["apply"] = ttk.Button(self.frame_apply_cancel, text="Apply", command=self.apply)
        self.buttons["apply"].grid(row=row_num, column=0, padx=1, pady=1, stick=tk.EW)
        self.buttons["cancel"] = ttk.Button(self.frame_apply_cancel, text="Cancel", command=self.cancel)
        self.buttons["cancel"].grid(row=row_num, column=1, padx=1, pady=1, stick=tk.EW)
        row_num += 1


    def is_a_number(self, x):
        try:
            float(x)
            return True
        except ValueError:
            return False
        
    def update_coordinates(self, x1, y1, x2, y2):
        # The method that updates the coordinates of the cursors, shown in the entries.
        self.string_vars["coordinate 1"].set("("+str(x1)+", "+str(y1)+")")
        self.string_vars["coordinate 2"].set("("+str(x2)+", "+str(y2)+")")


    def cancel(self):
        # Called when the cancel button is clicked.
        self.grab_release()
        self.destroy()

    def apply(self):
        # Called when the apply button is clicked.
        if self.is_a_number(self.string_vars["tangent slope"].get()):
            self.main_window.set_di_dv_sc(self.string_vars["tangent slope"].get())
            self.grab_release()
            self.destroy()

        else:
            tk.messagebox.showinfo(parent=self, title="dI/dV not obtained yet.", 
                message="Please get a valid dI/dV first.")

    def calculate_slope(self):
        # Calculate the slope of the segement approximating the tangent of the I-V curve.
        entries_to_check = ["delta i", "delta y", "delta v", "delta x"]
        all_good = True
        for item in entries_to_check:
            if self.is_a_number(self.string_vars[item].get()) is False:
                all_good = False
        if all_good:
            x1 = self.cursor_1.get_coordinate()[0]
            y1 = self.cursor_1.get_coordinate()[1]
            x2 = self.cursor_2.get_coordinate()[0]
            y2 = self.cursor_2.get_coordinate()[1]

            self.slop_i_v = - (y2 - y1) * float(self.string_vars["delta i"].get())/float(self.string_vars["delta y"].get()) / ((x2 - x1) * float(self.string_vars["delta v"].get())/float(self.string_vars["delta x"].get()))
            
            if self.slop_i_v > -1e-6:
                tk.messagebox.showinfo(parent=self, title="The I-V curve seems too flat or the slop appears positive", 
                message="The I-V curve seems too flat or the slop appears positive. To make the calculation numerically robust and the case valid, the slope is assumed to be -1e-6 (A/V). Please retry if necessary.")
                self.slop_i_v = -1e-6
            self.string_vars["tangent slope"].set("{:.5e}".format(self.slop_i_v))
        else:
            tk.messagebox.showinfo(parent=self, title="Invalid input", 
            message="Please provide valid numbers in the entries for |ΔI|, |Δy|, |ΔV|, and |Δx|.")

    def set_delta_y(self):
        # Set the delta y value in the entry.
        delta_y = abs(self.cursor_1.get_coordinate()[1] - self.cursor_2.get_coordinate()[1])
        self.string_vars["delta y"].set(str(delta_y))

    def set_delta_x(self):
        # Set the delta x value in the entry.
        delta_x = abs(self.cursor_1.get_coordinate()[0] - self.cursor_2.get_coordinate()[0])
        self.string_vars["delta x"].set(str(delta_x))
        

    def load_image(self):
        # Called when the load image button is clicked to load an user selected I-V curve image.
        image_to_open = filedialog.askopenfilename(parent=self, initialdir = getcwd(),title = "Open a case file",filetypes=self.ftypes)
        if image_to_open:
            i_v_image_original = Image.open(image_to_open)
            # Scale the image to fit the canvas.
            scale_x = self.canvas_width / i_v_image_original.width
            scale_y = self.canvas_height / i_v_image_original.height

            scale_image = min(scale_x, scale_y)

            i_v_image_scaled = i_v_image_original.resize((int(i_v_image_original.width*scale_image), int(i_v_image_original.height*scale_image)))

            self.i_v_image = ImageTk.PhotoImage(i_v_image_scaled)

            # Show the image in the canvas.
            self.canvas_i_v_image = self.i_v_canvas.create_image(
                (self.canvas_width//2, self.canvas_height//2),
                image=self.i_v_image
            )
            for i in range(3):
                self.i_v_canvas.tag_lower(self.canvas_i_v_image)


    def clear_image(self):
        # Clear the image from the canvas.
        self.i_v_canvas.delete(self.canvas_i_v_image)
        

    
