import serial
import serial.tools.list_ports
from time import sleep

class laserClass:
    def __init__(self):
        self.n_samples = 0
        self.ch_start = 0
        self.ch_end = 0
        self.first_run_ind = 1
        ports = serial.tools.list_ports.comports()
        for port in ports:
            print(f"Port: {port.device}")
            print(f"Description: {port.description}")
            print(f"Hardware ID: {port.hwid}\n")

        print("Laser port is usually labeled as SER=FTDI on the Hardware ID line")
        comport = "COM"+input("Enter laser COM port number: ")
        print(comport)
        self.laser_port = serial.Serial(comport)
        self.laser_port.baudrate = 9600
        self.laser_port.stopbits= 1
        self.laser_port.parity = 'N'
        self.laser_port.bytesize = 8
        print(self.laser_port)
    
    def set_wl(self,ch_number):
        datah = ch_number//256
        datal = ch_number%256
        send_array = bytearray([0x00,0x01,0x01,datah,datal,datah+datal+2])
        self.laser_port.write(send_array)

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



    def sweep_init(self):
        
        if(self.first_run_ind == 1):
            [self.ch_start,self.ch_end,self.n_samples] = self.param_set()
        else:
            print("\nLAST RUN PARMETERS")
            print("Channel Start: ",str(self.ch_start))
            print("Channel End: ",str(self.ch_end))
            print("Samples per wavelength: ",str(self.n_samples))
            if(input("Would you like to enter new parameters?(y/n)").lower() == 'y'):
                [self.ch_start,self.ch_end,self.n_samples] = self.param_set()
        
        self.increment = -1 if self.ch_start>self.ch_end else 1

        #set laser wavelength to channel start after initialization
        self.set_wl(self.ch_start)
        self.curr_ch = self.ch_start
        self.sweep_hasnext = True
        self.first_run_ind = 0

        # input("Press Enter to start sweep")  
        # for i in range(self.ch_start,self.ch_end+self.increment,self.increment):
        #     ch_num = i
        #     datah = ch_num//256
        #     datal = ch_num%256
        #     send_array = bytearray([0x00,0x01,0x01,datah,datal,datah+datal+2])
        #     print("Channel Number: ",ch_num)
        #     print(send_array)
        #     self.laser_port.write(send_array)
        #     sleep(self.n_samples)

        # self.first_run_ind = 0
        # print("\n \nSWEEP FINISHED")

    def next_wl(self):
        self.curr_ch = self.curr_ch + self.increment
        self.set_wl(self.curr_ch)
        if self.curr_ch < self.ch_end:
            self.sweep_hasnext = False
        

# cont_flag = 'y'
# while(cont_flag.lower() == 'y' ):
#     sweep()
#     cont_flag = input("Start another run?(y/n)")
