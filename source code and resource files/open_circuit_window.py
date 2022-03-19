# Define the window class for approximating the slope di/dv near the open circuit condition
# using a graphical approximation method.

from short_circuit_window import ShortCircuitWindow
import tkinter as tk

class OpenCircuitWindow(ShortCircuitWindow):
    # Just inherit from the short circuit window class and make appropriate modifications.
    def __init__(self, main_window, **kwargs):
        super().__init__(main_window, **kwargs)

        self.title('Approximating the tangent slope near the open circuit condition...')
        self.image_frame.configure(text='Load the I-V curve (for STC) near I=0:')

    def calculate_slope(self):
        entries_to_check = ['delta i', 'delta y', 'delta v', 'delta x']
        all_good = True
        for item in entries_to_check:
            if self.is_a_number(self.string_vars[item].get()) is False:
                all_good = False
        if all_good:
            x1 = self.cursor_1.get_coordinate()[0]
            y1 = self.cursor_1.get_coordinate()[1]
            x2 = self.cursor_2.get_coordinate()[0]
            y2 = self.cursor_2.get_coordinate()[1]

            self.slop_i_v = - (y2 - y1) * float(self.string_vars['delta i'].get())/float(self.string_vars['delta y'].get()) / ((x2 - x1) * float(self.string_vars['delta v'].get())/float(self.string_vars['delta x'].get()))
            
            if self.slop_i_v > 0 or self.slop_i_v < -1e6:
                tk.messagebox.showinfo(parent=self, title='The I-V curve seems too steep or the slop appears positive', 
                message='The I-V curve seems too steep or the slop appears positive. To make the calculation numerically robust and the case valid, the slope is assumed to be -1e6 (A/V). Please retry if necessary.')
                self.slop_i_v = -1e6
            self.string_vars['tangent slope'].set('{0:.5f}'.format(self.slop_i_v))
        else:
            tk.messagebox.showinfo(parent=self, title='Invalid input', 
            message='Please provide valid numbers in the entries for |ΔI|, |Δy|, |ΔV|, and |Δx|.')



    def apply(self):
        if self.is_a_number(self.string_vars['tangent slope'].get()):
            self.main_window.set_di_dv_oc(self.string_vars['tangent slope'].get())
            self.grab_release()
            self.destroy()

        else:
            tk.messagebox.showinfo(parent=self, title='dI/dV not obtained yet.', 
                message='Please get a valid dI/dV first.')