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

        #initialize wl_list
        self.wl_list = [1567.1326, 1566.7231, 1566.3138, 1565.9047, 1565.4959, 1565.0872, 1564.6788, 1564.2706, 1563.8626, 1563.4548, 1563.0472, 1562.6399, 1562.2327, 1561.8258, 1561.4191, 1561.0125, 1560.6062, 1560.2001, 1559.7943, 1559.3886, 1558.9831, 1558.5779, 1558.1729, 1557.768, 1557.3634, 1556.959, 1556.5548, 1556.1508, 1555.7471, 1555.3435, 1554.9401, 1554.537, 1554.134, 1553.7313, 1553.3288, 1552.9265, 1552.5244, 1552.1225, 1551.7208, 1551.3193, 1550.918, 1550.517, 1550.1161, 1549.7155, 1549.315, 1548.9148, 1548.5148, 1548.1149, 1547.7153, 1547.3159, 1546.9167, 1546.5177, 1546.1189, 1545.7203, 1545.3219, 1544.9238, 1544.5258, 1544.128, 1543.7305, 1543.3331, 1542.936, 1542.539, 1542.1423, 1541.7457, 1541.3494, 1540.9533, 1540.5573, 1540.1616, 1539.7661, 1539.3708, 1538.9757, 1538.5807, 1538.186, 1537.7915, 1537.3972, 1537.0031, 1536.6092, 1536.2155, 1535.822, 1535.4287, 1535.0356, 1534.6427, 1534.25, 1533.8575, 1533.4653, 1533.0732, 1532.6813, 1532.2896, 1531.8981, 1531.5068, 1531.1157, 1530.7248, 1530.3341, 1529.9436, 1529.5534, 1529.1633, 1528.7734, 1528.3837, 1527.9942, 1527.6049]

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
        self.curr_wl = self.wl_list[ch_number-1] # update equivalent wavelength
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
        
        
        self.first_run_ind = 0 

    def start_wl(self):
        #set laser wavelength to channel start after initialization
        self.set_wl(self.ch_start)
        self.curr_ch = self.ch_start
        self.ch_in_range = True
        


    #This function iterates through the channel numbers. Flags ch_in_range to indicate when the wavelengths are done
    def next_wl(self):
        self.curr_ch = self.curr_ch - 1
        self.set_wl(self.curr_ch)
        if self.curr_ch < self.ch_end:
            self.ch_in_range = False
