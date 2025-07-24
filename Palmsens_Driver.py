# Standard library imports
import datetime
import logging
import os
import os.path
import sys
import numpy as np

import pspython.pspyfiles
import pspython.pspydata
import datetime

# Third-party imports

# import matplotlib.pyplot as plt

# Local imports
import pspython.pspyinstruments as pspyinstr


class Palmsens_Driver:
    def __init__(self, method_d):
        self.initiateConnection()
        self.method_d = method_d

    def initiateConnection(self):
        self.instr = pspyinstr.InstrumentManager()
        self.device = self.instr.discover_instruments(ftdi=True)[0]
        if self.device:
            self.instr.connect(self.device)

        else:
            print("Connection to Palmsens device failed")

    #This function will run a chronoamperometric measurements and return the collected data
    #All input variables follow their titles (all time units in seconds, and bias in volts)
    #Take note that this function can only perform a single channel at a timeon the MUX, inputted as 1-8 (don't enter this variable if not applicable)
    def runCA(self, bias, process_time, meas_interval, equil_time, mux_ch=1):


        file_path = f"{self.method_d}"+ r"\Chronoamperometry_Default.psmethod"
        temp_path = f"{self.method_d}"+ r"\Temp\Chronoamperometry_Temp.psmethod"

        # Open and read the file
        try:
            with open(file_path, "r", encoding="utf-16le") as file:
                method_text = file.readlines()
                file.close()


            with open(temp_path, "wb") as file:

                for line in method_text:
                    if "T_EQUIL" in line:
                        new_line = f"T_EQUIL={self.numberConvSci(equil_time)}\n".encode('utf-16le')
                        file.write(new_line)
                    elif "T_RUN" in line:
                        new_line = f"T_RUN={self.numberConvSci(process_time)}\n".encode('utf-16le')
                        file.write(new_line)
                    elif "T_INTERVAL" in line:
                        new_line = f"T_INTERVAL={self.numberConvSci(meas_interval)}\n".encode('utf-16le')
                        file.write(new_line)
                    elif "E=" == line[0:2]:
                        new_line = f"E={self.numberConvSci(bias)}\n".encode('utf-16le')
                        file.write(new_line)
                    elif "MUX_METHOD" in line:
                        if mux_ch is None:
                            new_line = f"MUX_METHOD=-1\n".encode('utf-16le')
                            file.write(new_line)
                        else:
                            new_line = f"MUX_METHOD=0\n".encode('utf-16le')
                            file.write(new_line)
                    elif "USE_MUX_CH" in line:
                        if mux_ch is not None:
                            print(mux_ch)
                            ch_num = f"{2**(mux_ch-1)}"
                            print(ch_num)
                            new_line = f"USE_MUX_CH={ch_num}\n".encode('utf-16le')
                            file.write(new_line)
                        else:
                            new_line = "USE_MUX_CH=1\n".encode('utf-16le')
                            file.write(new_line)
                    else:
                        file.write(line.encode("utf-16le"))

                file.close()

            method = pspython.pspyfiles.load_method_file(temp_path)
            results = self.instr.measure(method)

            data = np.array([results.time_arrays, results.current_arrays])

            return data[:, 0, :].T

        except FileNotFoundError:
            print("Chronoamperometry method file not found, please change directory")
            return None

    def runCV(self, start_pot, vertex_1_pot, vertex_2_pot, pot_step, scan_no, scan_rate, equil_time, mux_ch=None):

        file_path = f"{self.method_d}" + r"\Chronovoltammetry_Default.psmethod"
        temp_path = f"{self.method_d}" + r"\Temp\Chronovoltammetry_Temp.psmethod"

        try:
            with open(file_path, "r", encoding="utf-16le") as file:
                method_text = file.readlines()
                file.close()

            with open(temp_path, "wb") as file:

                for line in method_text:
                    if "T_EQUIL" in line:
                        new_line = f"T_EQUIL={self.numberConvSci(equil_time)}\n".encode('utf-16le')
                        file.write(new_line)
                    elif "E_BEGIN" in line:
                        new_line = f"E_BEGIN={self.numberConvSci(start_pot)}\n".encode('utf-16le')
                        file.write(new_line)
                    elif "E_STEP" in line:
                        new_line = f"E_STEP={self.numberConvSci(pot_step)}\n".encode('utf-16le')
                        file.write(new_line)
                    elif "E_VTX1" in line:
                        new_line = f"E_VTX1={self.numberConvSci(vertex_1_pot)}\n".encode('utf-16le')
                        file.write(new_line)
                    elif "E_VTX2" in line:
                        new_line = f"E_VTX2={self.numberConvSci(vertex_2_pot)}\n".encode('utf-16le')
                        file.write(new_line)
                    elif "SCAN_RATE" in line:
                        new_line = f"SCAN_RATE={self.numberConvSci(scan_rate)}\n".encode('utf-16le')
                        file.write(new_line)
                    elif "N_SCANS=" in line:
                        new_line = f"N_SCANS={scan_no}\n".encode('utf-16le')
                        file.write(new_line)
                    elif "MUX_METHOD" in line:
                        if mux_ch is None:
                            new_line = f"MUX_METHOD=-1\n".encode('utf-16le')
                            file.write(new_line)
                        else:
                            new_line = f"MUX_METHOD=0\n".encode('utf-16le')
                            file.write(new_line)
                    elif "USE_MUX_CH" in line:
                        if mux_ch is None:
                            new_line = "USE_MUX_CH=1\n".encode('utf-16le')
                            file.write(new_line)
                        else:
                            ch_num = f"{2 ** (mux_ch - 1)}"
                            new_line = f"USE_MUX_CH={ch_num}\n".encode('utf-16le')
                            file.write(new_line)
                    else:
                        file.write(line.encode("utf-16le"))

                file.close()

            method = pspython.pspyfiles.load_method_file(temp_path)
            results = self.instr.measure(method)
            print(np.shape(results.potential_arrays))
            data_array = np.array([])
            for i in range(0, scan_no, 1):
                if i == 0:
                    data_array = np.concatenate(([results.potential_arrays[i]], [results.current_arrays[i]]), axis=0)
                else:
                    data_array = np.concatenate((data_array, [results.potential_arrays[i], results.current_arrays[i]]), axis=0)

            return data_array.T

        except FileNotFoundError:
            print("Chronovoltammetry method file not found, please change directory")
            return None


    def runEIS(self, e_DC, e_AC, min_freq, max_freq, equil_time, mux_ch=None):

        file_path = f"{self.method_d}" + r"\Impedance_Spectroscopy_Default.psmethod"
        temp_path = f"{self.method_d}" + r"\Temp\Impedance_Spectroscopy_Temp.psmethod"

        try:
            with open(file_path, "r", encoding="utf-16le") as file:
                method_text = file.readlines()
                file.close()

            with open(temp_path, "wb") as file:

                for line in method_text:
                    if "T_EQUIL" in line:
                        new_line = f"T_EQUIL={self.numberConvSci(equil_time)}\n".encode('utf-16le')
                        file.write(new_line)
                    elif "E_BEGIN" in line:
                        new_line = f"E_BEGIN={self.numberConvSci(e_DC)}\n".encode('utf-16le')
                        file.write(new_line)
                    elif "E=" == line[0:2]:
                        new_line = f"E={self.numberConvSci(e_DC)}\n".encode('utf-16le')
                        file.write(new_line)
                    elif "AMPLITUDE" in line:
                        new_line = f"AMPLITUDE={self.numberConvSci(e_AC)}\n".encode('utf-16le')
                        file.write(new_line)
                    elif "MAX_FREQ" in line:
                        new_line = f"MAX_FREQ={self.numberConvSci(max_freq)}\n".encode('utf-16le')
                    elif "MIN_FREQ" in line:
                        new_line = f"MIN_FREQ={self.numberConvSci(min_freq)}\n".encode('utf-16le')
                    elif "MUX_METHOD" in line:
                        if mux_ch is None:
                            new_line = f"MUX_METHOD=-1\n".encode('utf-16le')
                            file.write(new_line)
                        else:
                            new_line = f"MUX_METHOD=0\n".encode('utf-16le')
                            file.write(new_line)
                    elif "USE_MUX_CH" in line:
                        if mux_ch is None:
                            new_line = "USE_MUX_CH=1\n".encode('utf-16le')
                            file.write(new_line)
                        else:
                            ch_num = f"{2 ** (mux_ch - 1)}"
                            new_line = f"USE_MUX_CH={ch_num}\n".encode('utf-16le')
                            file.write(new_line)
                    else:
                        file.write(line.encode("utf-16le"))

                file.close()


            method = pspython.pspyfiles.load_method_file(temp_path)
            results = self.instr.measure(method)

            data = np.array([results.zim_arrays, results.zre_arrays, results.freq_arrays])
            return data[:, 0, :].T



        except Exception as e:
            print(e)
            print("EIS method file not found, please change directory")
            return None



    def runOCP(self, equil_time, mux_ch=None):

        #TODO: Properly fill this function out

        file_path = f"{self.method_d}" + r"\Open_Circuit_Potentiometry_Default.psmethod"
        temp_path = f"{self.method_d}" + r"\Temp\Open_Circuit_Potentiometry_Temp.psmethod"


        with open(file_path, "r", encoding="utf-16le") as file:
            method_text = file.readlines()
            file.close()

        with open(temp_path, "wb") as file:

            for line in method_text:
                if "T_EQUIL" in line:
                    new_line = f"T_EQUIL={self.numberConvSci(equil_time)}\n".encode('utf-16le')
                    file.write(new_line)
                elif "MUX_METHOD" in line:
                    if mux_ch is None:
                        new_line = f"MUX_METHOD=-1\n".encode('utf-16le')
                        file.write(new_line)
                    else:
                        new_line = f"MUX_METHOD=0\n".encode('utf-16le')
                        file.write(new_line)
                elif "USE_MUX_CH" in line:
                    if mux_ch is None:
                        new_line = "USE_MUX_CH=1\n".encode('utf-16le')
                        file.write(new_line)
                    else:
                        ch_num = f"{2 ** (mux_ch - 1)}"
                        new_line = f"USE_MUX_CH={ch_num}\n".encode('utf-16le')
                        file.write(new_line)
                else:
                    file.write(line.encode("utf-16le"))

            file.close()

        method = pspython.pspyfiles.load_method_file(temp_path)
        results = self.instr.measure(method)
        data = np.array([results.time_arrays, results.potential_arrays])

        return data[:, 0, :].T

    #This function converts an input number into the format accepted by the Palmsens
    def numberConvSci(self, num):
        formatted = f"{num:.3E}"
        # Split the result into the base and exponent
        base, exponent = formatted.split('E')
        # Ensure the exponent part always has 3 digits
        exponent = f"{int(exponent):+04d}"
        return f"{base}E{exponent}"


if __name__ == '__main__':
    ps_instance = Palmsens_Driver(r"C:\Users\Daniel\Box\Research\Software\PEC_Driver\Methods_Directory")
    #data = ps_instance.runCV(0, 0.1, -0.1, .005, 2, .05, 1, 1)

    print(ps_instance.runOCP(equil_time=15, mux_ch=2))
