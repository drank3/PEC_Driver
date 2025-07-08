from Arduino_Driver import Arduino_Driver
from Palmsens_Driver import Palmsens_Driver
import time
import numpy as np
import os

sample_name = "n_(n)3DFG-iSi_A2_8,46m-pSi_1,25"
save_path = r"C:\Users\Daniel\Box\Research\Data\PEC"
class Central_Driver:
    def __init__(self):
        self.arduino_instance = Arduino_Driver()

        self.palmsens_instance = Palmsens_Driver(r"C:\Users\Daniel\Box\Research\\Software\PEC_Driver\Methods_Directory")

        #Creating the save directory for all the data below
        if not os.path.exists(save_path+r"\\"+sample_name):
            os.makedirs(save_path+r"\\"+sample_name)
            print(f"Created folder: {sample_name}")
        else:
            pass
        self.data_directory = save_path+r"\\"+sample_name

        self.arduino_instance.initiateConnection("COM4")
        time.sleep(12)

    def Light_Pulse_Cycle(self):

        pulse_on_time = 1500
        pulse_off_time = 3000
        power_setpoint = 2600
        cycles = 16

        light_names = [404, 450, 500, 530, 600, 615, 660, 720, 850, 920]
        #light_names = [615, 660, 720, 850, 920]

        first_equil = True
        for ch_no in [1, 2, 3, 4]:
            for scan_rate in [25, 50, 75, 100, 125, 150, 175, 200]:
                if first_equil == True:
                    data = self.palmsens_instance.runCV(0, 0.3, -0.3, .005, 4, scan_rate/1000, 30, ch_no)
                    first_equil = False
                else:
                    data = self.palmsens_instance.runCV(0, 0.3, -0.3, .005, 4, scan_rate/1000, 5, ch_no)

                file_name = self.data_directory + "\\" + sample_name + f"-CVS_P{ch_no}_{scan_rate}mVs-1.csv"
                np.savetxt(file_name, data, delimiter=",", header="Voltage (V),Current (uA), Voltage (V),Current (uA)")

        for light in light_names:
            self.arduino_instance.write(f"{light}_Off")
            time.sleep(10)



            for ch_no in [1, 2, 3, 4]:

                self.arduino_instance.write(f"{light}_Pulse_On-{pulse_on_time}_Off-{pulse_off_time}_Power-{power_setpoint}_Cycles-{cycles}")
                data = self.palmsens_instance.runCA(0, 45, .05, 30, ch_no)
                file_name = self.data_directory + "\\" + sample_name + f"-CA_{light}nm_P{ch_no}_Power-{power_setpoint}_bias-0V.csv"
                np.savetxt(file_name, data, delimiter=",", header="Time (s),Current (uA)")

                time.sleep(5)
                print(f"Completed {light} pulsing at {ch_no} for CA")



                self.arduino_instance.write(f"{light}_On_Power-{power_setpoint}")
                data = self.palmsens_instance.runCV(0, 0.5, -0.5, .005, 3, .05, 15, ch_no)
                file_name = self.data_directory + "\\" + sample_name + f"-CV_{light}nm_P{ch_no}_Power-{power_setpoint}.csv"
                np.savetxt(file_name, data, delimiter=",", header="Voltage (V),Current (uA), Voltage (V),Current (uA), Voltage (V),Current (uA)")

                self.arduino_instance.write(f"{light}_Off")
                data = self.palmsens_instance.runCV(0, 0.5, -0.5, .005, 3, .05, 15, ch_no)
                file_name = self.data_directory + "\\" + sample_name + f"-CV_{light}nm_P{ch_no}_Power-0.csv"
                np.savetxt(file_name, data, delimiter=",", header="Voltage (V),Current (uA), Voltage (V),Current (uA), Voltage (V),Current (uA)")

                time.sleep(1.5)
                print(f"Completed {light} at {ch_no} for CV")


                self.arduino_instance.write(f"{light}_On_Power-{power_setpoint}")
                data = self.palmsens_instance.runEIS(0, 0.01, 5, 50000, 10, ch_no)
                file_name = self.data_directory + "\\" + sample_name + f"-EIS_{light}nm_P{ch_no}_Power-{power_setpoint}.csv"
                np.savetxt(file_name, data, delimiter=",", header="Z_im,Z_real,Frequency (Hz)")

                self.arduino_instance.write(f"{light}_Off")
                data = self.palmsens_instance.runEIS(0, 0.01, 5, 50000, 10, ch_no)
                file_name = self.data_directory + "\\" + sample_name + f"-EIS_{light}nm_P{ch_no}_Power-0.csv"
                np.savetxt(file_name, data, delimiter=",", header="Z_im,Z_real,Frequency (Hz)")

                time.sleep(1.5)
                print(f"Completed {light} at {ch_no} for EIS")

                self.arduino_instance.write(
                    f"{light}_Pulse_On-{pulse_on_time}_Off-{pulse_off_time}_Power-{power_setpoint}_Cycles-{cycles-7}")
                data = self.palmsens_instance.runOCP(45, ch_no)
                file_name = self.data_directory + "\\" + sample_name + f"-OCP_{light}nm_P{ch_no}_Power-{power_setpoint}.csv"
                np.savetxt(file_name, data, delimiter=",", header="Time (s),Potential (V)")

                time.sleep(15)
                print(f"Completed {light} pulsing at {ch_no} for OCP")
        self.arduino_instance.write("720_Off")









if __name__ == "__main__":

    Central_Driver_Instance = Central_Driver()
    Central_Driver_Instance.Light_Pulse_Cycle()
