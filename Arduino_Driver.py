import time
import warnings
import serial
import serial.tools.list_ports


class Arduino_Driver:
    def __init__(self):
        pass

    def initiateConnection(self, ser=None):
        print(serial.tools.list_ports.comports())
        if ser is None:
            arduino_ports = [
                p.device

                for p in serial.tools.list_ports.comports()
                if 'Arduino' in p.description  # may need tweaking to match new arduinos
            ]
            if not arduino_ports:
                raise IOError("No Arduino found")
            if len(arduino_ports) > 1:
                warnings.warn('Multiple Arduinos found - using the first')

            ser = serial.Serial(arduino_ports[0])

        print(ser)

        self.arduino = serial.Serial(port=ser, baudrate=9600, timeout=.1)





    def write(self, input_str):
        self.arduino.write(bytes(input_str, 'utf-8'))
        time.sleep(0.05)






if __name__ == "__main__":
    print("loser")
    arduino = Arduino_Driver()
    arduino.write("L8P4")
    time.sleep(5)
    arduino.write("L8P1")