# The PV module model parameter extractor class.
#
# The instance of this class can be used to automatically calculate the
# PV module model parameters, given the PV module's data from the data sheet
# provided by the manufacturer.
#
# It is used to remove the need for any manual calculation of the PV module model
# parameters for further uses in circuit simulations using other
# software such as, Simulink, PLECS, XCOS, PSpice, LTspice, etc.
#
# In one step of the calculation process, a nonlinear equation system solver
# is needed. Since Scipy is a free open source package, to avoid reinventing
# the wheel, it is decided that Scipy's fsolve function is used as the 
# required nonlinear equation system solver.


from scipy.optimize import fsolve
from math import exp

class PV_Module_Model_Parameter_Extractor:

    def __init__(self, v_oc_stc=44.9, i_sc_stc=8.53, v_mp=36.1, i_mp=8.04, 
    temp_coeff_i_perc=0.046, temp_coeff_v_perc=-0.33, n_cell=72, 
     di_dv_sc=-2.488e-3, di_dv_oc=-2.05,
     temperature_c=25, solar_irr =1000):
        self._solved = False # Initially, the parameters are not extracted yet.

        # Some physical constants:
        self._q = 1.6e-19 # the charge of an electron in SI unit
        self._k = 1.38e-23 # Boltzmann constant in SI unit
        self._stc_temp_k = 25.0 + 273.15 # STC condition temperature with unit K
        self._stc_solar_irr = 1000 # STC condition solar irradiation with unit W/(m^2)

        # The parameters that need to be extracted:
        self._i_ph = 0.0 # photon current
        self._v_oc = 0.0 # the open circuit voltage in a different temperature
        self._r_sh = 0.0 # shunt resistance
        self._r_s = 0.0 # series resistance
        self._a = 0.0 # diode ideality factor
        self._i_o = 0.0 # diode reverse saturation current.
        self._i_o_stc = 0.0 # i_o at STC.

        # Initialize:
        self._v_oc_stc = v_oc_stc
        self._i_sc_stc = i_sc_stc
        self._v_mp = v_mp
        self._i_mp = i_mp
        self._temp_coeff_i = temp_coeff_i_perc / 100 
        # The temperature coefficient's unit is %/C, need to be converted.
        self._temp_coeff_v = temp_coeff_v_perc / 100
        self._n_cell = n_cell
        self._di_dv_sc = di_dv_sc
        self._di_dv_oc = di_dv_oc
        self._temperature_c = temperature_c
        self._temperature_k = self._temperature_c + 273.15 # convert temperature unit C to K
        self._solar_irr = solar_irr
        

    def _nonlinear_equations(self, x):

        # Unpack to get the unknown variables.
        a, i_o, r_s = x
        # Define the three nonlinear equations
        f_1 = i_o * (exp(self._q * self._v_oc_stc/(self._n_cell * a * self._k * self._stc_temp_k)) - 1)\
             - (self._i_sc_stc - self._v_oc_stc / self._r_sh)
        f_2 = self._i_mp - self._i_sc_stc + i_o * (exp((self._v_mp + r_s*self._i_mp)\
             / ((self._n_cell* a* self._k* self._stc_temp_k)/self._q)) - 1)\
                  + (self._v_mp + self._r_s * self._i_mp) / self._r_sh
        f_3 = r_s + 1 / self._di_dv_oc + (self._n_cell* a* self._k* self._stc_temp_k/ self._q) / self._i_sc_stc

        return [f_1, f_2, f_3]

    def extract(self, a_init = 1.3, r_s_init = 0.3):
        # note that the temperature coefficient's unit is %/C
        self._i_ph = self._i_sc_stc * (1 + self._temp_coeff_i * (self._temperature_k - self._stc_temp_k))
        self._i_ph *= self._solar_irr / self._stc_solar_irr

        self._v_oc = self._v_oc_stc *(1 + self._temp_coeff_v * (self._temperature_k - self._stc_temp_k))

        self._r_sh = -1.0 / self._di_dv_sc

        # The inital value of the reverse saturation current, i_o, is calculated by:
        i_o_init = (self._i_sc_stc - self._v_oc_stc / self._r_sh)\
             / exp(self._q*self._v_oc_stc/(self._n_cell * a_init * self._k * self._stc_temp_k))
        
        # Solve nonlinear equations to get the model parameters.
        self._a, self._i_o_stc, self._r_s = fsolve(self._nonlinear_equations, [a_init, i_o_init, r_s_init], xtol=1e-12)



        # Update self._i_o based on the new open circuit voltage (1000 W/m^2 irradiance).
        i_sc_working = self._i_sc_stc * (1 + self._temp_coeff_i * (self._temperature_k - self._stc_temp_k))
        self._i_o = (i_sc_working - self._v_oc/self._r_sh)\
             / exp(self._q*self._v_oc/(self._n_cell*self._a*self._k*self._temperature_k))

        self._solved = True
        return self._a, self._i_o, self._i_ph, self._r_s, self._r_sh

    def get_mismatch(self):
        print("showing nonlinear equation errors with the numerical solution:")
        mismatch = self._nonlinear_equations([self._a, self._i_o_stc, self._r_s])
        print(mismatch)

        return mismatch

    def get_solution(self):
        # Pass the solution to the GUI.
        if not self._solved:
            return None

        solution = {
            "a": self._a,
            "i_o": self._i_o,
            "i_ph": self._i_ph,
            "r_s": self._r_s,
            "r_sh": self._r_sh,
        }
        return solution


# Unit test.
if __name__ == "__main__":
    parameter_extracter = PV_Module_Model_Parameter_Extractor()
    a, i_o, i_ph, r_s, r_sh = parameter_extracter.extract()
    print("")
    print("The extracted PV module parameters are:")
    #print((a, i_o, i_ph, r_s, r_sh))
    print("a = " + str(a))
    #print(a)
    print("I_o = " + str(i_o))
    #print(i_o)
    print("I_ph = " + str(i_ph))
    #print(i_ph)
    print("R_s = " + str(r_s))
    #print(r_s)
    print("R_sh = " + str(r_sh))
    #print(r_sh)
    #print("V_oc = " + str(v_oc))

