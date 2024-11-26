import serial
import serial.tools.list_ports
from time import sleep

class SIMTRUMlaserClass:
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
            self.laser_port = serial.Serial(comport)
            self.laser_port.baudrate = 9600
            self.laser_port.stopbits= 1
            self.laser_port.parity = 'N'
            self.laser_port.bytesize = 8
            print(self.laser_port)
            print("\nConnection with Laser successful")
        except: 
            print("\nLaser not found in ",comport,"\nPlease enter the correct comport\n")
            for port in ports:
                print(f"Port: {port.device}")
                print(f"Description: {port.description}")
                print(f"Hardware ID: {port.hwid}\n")
            while True:
                #Try loop for manual connection
                try:
                    print("Laser port is usually labeled as SER=FTDI on the Hardware ID line")
                    comport = "COM"+input("Enter laser COM port number: ")
                    print(comport)
                    self.laser_port = serial.Serial(comport)
                    self.laser_port.baudrate = 9600
                    self.laser_port.stopbits= 1
                    self.laser_port.parity = 'N'
                    self.laser_port.bytesize = 8
                    print(self.laser_port)
                    print("\nConnection with Laser successful")
                    break
                except:
                    print("\nInvalid COM number\nTry Again\n")
                    continue
    
    #This function takes in a channel number and sends the corresponding byte array to the laser
    def set_wl(self,ch_number):
        datah = ch_number//256
        datal = ch_number%256
        send_array = bytearray([0x00,0x01,0x01,datah,datal,datah+datal+2])
        self.laser_port.write(send_array)
        print("Wait 5s for laser to stabilize")
        sleep(5)

    #This section runs the routine for setting the sweep parameters
    def param_set(self):
                print("\n \nSET SWEEP PARAMETERS")
                inp_loop = True
                while inp_loop:
                    print("Refer to the spreadsheet in the C-Band Laser Gdrive folder for the equivalent wavelength \nChannel Start must be higher than channel end")
                    arg_ch_start = int(input("Channel Start (1-100): "))
                    arg_ch_end = int(input("Channel End (1-100): "))
                    arg_n_samples = int(input("Samples per Wavelength: "))
                    if arg_ch_start>arg_ch_end and (arg_ch_end<=100) and arg_ch_start<=100 :
                        break
                    print("\nINVALID VALUE/S \n")   

                return [arg_ch_start,arg_ch_end,arg_n_samples]


    #This function runs the initialization of a sweep; includes resetting the wavelength and other variables
    def sweep_init(self):
        
        if(self.first_run_ind == 1):
            print("\nDEFAULT PARAMETERS")
            print("Channel Start: ",str(self.ch_start))
            print("Channel End: ",str(self.ch_end))
            print("Samples per wavelength: ",str(self.n_samples))
            if(input("Would you like to enter different parameters?(y/n)").lower() == 'y'):
                [self.ch_start,self.ch_end,self.n_samples] = self.param_set()
        else:
            print("\nLAST RUN PARMETERS")
            print("Channel Start: ",str(self.ch_start))
            print("Channel End: ",str(self.ch_end))
            print("Samples per wavelength: ",str(self.n_samples))
            if(input("Would you like to enter new parameters?(y/n)").lower() == 'y'):
                [self.ch_start,self.ch_end,self.n_samples] = self.param_set()
        
        

        #set laser wavelength to channel start after initialization
        self.set_wl(self.ch_start)
        self.curr_ch = self.ch_start
        self.ch_in_range = True
        self.first_run_ind = 0



    #This function iterates through the channel numbers. Flags ch_in_range to indicate when the wavelengths are done
    def next_wl(self):
        self.curr_ch = self.curr_ch - 1
        self.set_wl(self.curr_ch)
        if self.curr_ch < self.ch_end:
            self.ch_in_range = False
