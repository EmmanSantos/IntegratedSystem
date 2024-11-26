import serial
import serial.tools.list_ports

class pmodClass:
    #This function initializes RS232 connection with the laser
    def __init__(self):
        #initialize default variables as well as default com port
        self.n_samples = 10
        self.ch_start = 100
        self.ch_end = 1
        self.first_run_ind = 1
        comport = 'COM4'
        ports = serial.tools.list_ports.comports()

        #Try connecting to default COM value
        try:
            self.pmod_port = serial.Serial(comport)
            self.pmod_port.baudrate = 115200
            self.pmod_port.bytesize = serial.EIGHTBITS
            self.pmod_port.parity = serial.PARITY_NONE
            self.pmod_port.stopbits = serial.STOPBITS_ONE
            self.pmod_port.timeout = 1 # Non-blocking read
            self.pmod_port.xonxoff = False
            self.pmod_port.rtscts = False
            self.pmod_port.dsrdtr = False
            self.pmod_port.writeTimeout = 2

            print(self.pmod_port)
            print("\nConnection with PModLaser successful")

        except: 
            print("\nPMod not found in ",comport,"\nPlease enter the correct comport\n")
            for port in ports:
                print(f"Port: {port.device}")
                print(f"Description: {port.description}")
                print(f"Hardware ID: {port.hwid}\n")
            while True:
                #Try loop for manual connection
                try:
                    print("PMod port is usually labeled as Prolific on the Desc line")
                    comport = "COM"+input("Enter PMod COM port number: ")
                    print(comport)
                    
                    self.pmod_port = serial.Serial(comport)
                    self.pmod_port.baudrate = 115200
                    self.pmod_port.bytesize = serial.EIGHTBITS
                    self.pmod_port.parity = serial.PARITY_NONE
                    self.pmod_port.stopbits = serial.STOPBITS_ONE
                    self.pmod_port.timeout = 1 # Non-blocking read
                    self.pmod_port.xonxoff = False
                    self.pmod_port.rtscts = False
                    self.pmod_port.dsrdtr = False
                    self.pmod_port.writeTimeout = 2

                    print(self.pmod_port)
                    print("\nConnection with Laser successful")
                    break
                except:
                    print("\nInvalid COM number\nTry Again\n")
                    continue