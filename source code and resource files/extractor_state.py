# Define the class of the object that represents the extractor's state
# and uses a thread to extract the equivalent circuit parameters.
# Using the thread, one can avoid freezing the main window when 
# the extraction is running as the extractor is possibly time consuming.

from pvmmpe import PV_Module_Model_Parameter_Extractor
import threading

class ExtractorState():
    # Define the thread for the parameters extraction work.
    class SolverThread(threading.Thread):
        def __init__(self, extractor_state):
            # The constructor for the solver thread class.
            # Keep a reference to the extractor state.
            self.extractor_state = extractor_state

        def run(self):
            # Put the possible time consuming solving work here.
            # First, disable all input entries in the GUI.
            self.extractor_state.main_window.disable_input_entries()
            # Disable the button before the extraction completes.
            self.extractor_state.main_window.disable_extraction()
            # Update the state bar at the GUI's bottom part.
            self.extractor_state.main_window.set_execution_state("Extracting parameters...")

            parameter_extracter = PV_Module_Model_Parameter_Extractor(
                v_oc_stc=self.extractor_state.v_oc_stc, 
                i_sc_stc=self.extractor_state.i_sc_stc, 
                v_mp=self.extractor_state.v_mp, 
                i_mp=self.extractor_state.i_mp, 
                temp_coeff_i_perc=self.extractor_state.temp_coeff_i_perc, 
                temp_coeff_v_perc=self.extractor_state.temp_coeff_v_perc, 
                n_cell=self.extractor_state.n_cell, 
                di_dv_sc=self.extractor_state.di_dv_sc, 
                di_dv_oc=self.extractor_state.di_dv_oc,
                temperature_c=self.extractor_state.temperature_c, 
                solar_irr=self.extractor_state.solar_irr
            )

            parameter_extracter.extract(self.extractor_state.a_init, self.extractor_state.r_s_init)
            solution = parameter_extracter.get_solution()
            mismatch = parameter_extracter.get_mismatch()

            # Set format for the the mismatch.
            string_format = "{:.4e}"
            # Update the solution entries in the GUI
            self.extractor_state.main_window.set_solution_entries(solution)

            # Enable the previously disabled entries.
            self.extractor_state.main_window.enable_input_entries()
            # Enable the extract button.
            self.extractor_state.main_window.enable_extraction()

            formatted_mismatch = [
            string_format.format(mismatch[0]),
            string_format.format(mismatch[1]),
            string_format.format(mismatch[2])
            ]
            # Update the state bar's text.
            self.extractor_state.main_window.set_execution_state("Extraction finished. Mismatch vector: ["+ formatted_mismatch[0] + ", " + formatted_mismatch[1] + ", " + formatted_mismatch[2] + "]" +". Ready for extracting again...")

            return



    def __init__(self, main_window):
        # The constructor for the extractor state class.
        # Keep a reference to the main GUI window.
        self.main_window = main_window
        # Input:
        self.v_oc_stc = None
        self.i_sc_stc = None
        self.v_mp = None
        self.i_mp = None
        self.temp_coeff_i_perc = None
        self.temp_coeff_v_perc = None
        self.n_cell = None
        self.di_dv_sc = None
        self.di_dv_oc = None
        self.temperature_c = None
        self.solar_irr = None
        # Solution:
        self.a = None
        self.i_o = None
        self.r_s = None
        self.r_sh = None
        self.i_ph = None
        #self.v_oc = None

        # Mismatch:
        self.mismatch = None



    def update_input_from_gui(self):
        # Get the input for the extractor from the GUI window.
        input_dict = self.main_window.get_input_for_extractor()

        self.v_oc_stc = input_dict["v_oc_stc"]
        self.i_sc_stc = input_dict["i_sc_stc"]
        self.v_mp = input_dict["v_mp"]
        self.i_mp = input_dict["i_mp"]
        self.temp_coeff_i_perc = input_dict["temp_coeff_i_perc"]
        self.temp_coeff_v_perc = input_dict["temp_coeff_v_perc"]
        self.n_cell = input_dict["n_cell"]
        self.di_dv_sc = input_dict["di_dv_sc"]
        self.di_dv_oc = input_dict["di_dv_oc"]
        self.temperature_c = input_dict["temperature_c"]
        self.solar_irr = input_dict["solar_irr"]

        self.a_init = input_dict["a_init"]
        self.r_s_init = input_dict["r_s_init"]

    def extract(self):
        self.update_input_from_gui()

        solver_thread = self.SolverThread(self)
        solver_thread.run()

    



