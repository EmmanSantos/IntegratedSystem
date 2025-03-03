import serial
import serial.tools.list_ports
from time import sleep
from pmod_sweep_util import settings_list_gen
from tqdm import tqdm

class pmodClass:
    #This function initializes RS232 connection with the laser
    def __init__(self):
        #initialize default variables as well as default com port
        self.n_samples = 10
        self.wl_start = 1527.371398
        self.wl_end = 1565.49586423
        self.stepsize = 100
        self.first_run_ind = 1
        comport = 'COM4'
        ports = serial.tools.list_ports.comports()
        self.source_device = 'pmod'

        self.prev_ch = 0

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

    #This function takes in a channel number and sends the corresponding byte array to the laser
    def set_wl(self,settings):
        self.curr_wl = 299792458/(settings[1]+settings[2])*1e3 # update equivalent wavelength nm

        command = 'LAS:CHAN: '+str(settings[0]) + '\r'
        self.pmod_port.write(command.encode())
        # print(command)

        sleep(1)

        command = 'LAS:FINE: '+str(settings[1]) + '\r'
        self.pmod_port.write(command.encode())
        
        
        # if settings[0] != self.prev_ch:
        #     print("Wait 120s due to channel change")
        #     for i in tqdm(range(120),desc="Waiting", bar_format="{desc}: {n}/{total}"):
        #         sleep(1)
        #     self.prev_ch = settings[0]
        # else:
        #     print("Wait 30s for laser to stabilize")
        #     for i in tqdm(range(30),desc="Waiting", bar_format="{desc}: {n}/{total}"):
        #         sleep(1)
        #     self.prev_ch = settings[0]

         #This section runs the routine for setting the sweep parameters
    def param_set(self):
                print("\n \nSET SWEEP PARAMETERS")
                inp_loop = True
                while inp_loop:
                    print("Wavelength Start must be lower than Wavelength end\n",
                          "Minimum Wavelength (nm): 1527.371398\n",
                          "Maximum Wavelength (nm): 1565.49586423\n",
                          "Minimum step size (pm): 1 (2pm step size is smallest recommended)")
                    arg_wl_start = float(input("Wavelength Start (nm): "))
                    arg_wl_end = float(input("Wavelength End(nm): "))
                    arg_stepsize = float(input("Stepsize (pm): "))
                    arg_n_samples = int(input("Samples per Wavelength: "))
                    if arg_wl_start<arg_wl_end and (arg_wl_end<=1565.49586423) and arg_wl_start>=1527.371398 and arg_stepsize>=1:
                        break
                    print("\nINVALID VALUE/S \n")   

                return [arg_wl_start,arg_wl_end,arg_stepsize,arg_n_samples]


    #This function runs the initialization of a sweep; includes resetting the wavelength and other variables
    def sweep_init(self):
        
        if(self.first_run_ind == 1):
            print("\nDEFAULT PARAMETERS")
            print("Wavelength Start  (nm): ",str(self.wl_start))
            print("Wavelength End  (nm): ",str(self.wl_end))
            print("Step size (pm):",str(self.stepsize))
            print("Samples per wavelength: ",str(self.n_samples))
            if(input("Would you like to enter different parameters?(y/n)").lower() == 'y'):
                [self.wl_start,self.wl_end,self.stepsize,self.n_samples] = self.param_set()
        else:
            print("\nLAST RUN PARMETERS")
            print("Wavelength Start: ",str(self.wl_start))
            print("Wavelength End: ",str(self.wl_end))
            print("Samples per wavelength: ",str(self.n_samples))
            print("Step size (pm):",str(self.stepsize))
            if(input("Would you like to enter new parameters?(y/n)").lower() == 'y'):
                [self.wl_start,self.wl_end,self.stepsize,self.n_samples] = self.param_set()
        
        self.settings_list = settings_list_gen(self.wl_start,self.wl_end,self.stepsize)
        
        self.first_run_ind = 0
        self.prev_ch = 0

    def start_wl(self):
        #set laser wavelength to channel start after initialization
        self.curr_ch = 1 # 1 is first setting for ui purposes
        self.set_wl(self.settings_list[self.curr_ch-1])
        self.ch_in_range = True 

    #This function iterates through the channel numbers. Flags ch_in_range to indicate when the wavelengths are done
    def next_wl(self):
        self.curr_ch = self.curr_ch + 1
        if self.curr_ch > len(self.settings_list): #stop conditon
            self.ch_in_range = False
            return
        self.set_wl(self.settings_list[self.curr_ch-1])