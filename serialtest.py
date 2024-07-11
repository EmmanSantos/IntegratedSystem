import serial
import serial.tools.list_ports
import pyvisa

ports = serial.tools.list_ports.comports()
for port in ports:
    print(f"Port: {port.device}")
    print(f"Description: {port.description}")
    print(f"Hardware ID: {port.hwid}\n")

print("Laser port is usually labeled as SER=FTDI on the Hardware ID line")
comport = "COM"+input("Enter laser COM port number: ")
print(comport)
osa_serial = serial.Serial(comport)
osa_serial.baudrate = 9600
osa_serial.stopbits= 1
osa_serial.parity = 'N'
osa_serial.bytesize = 8
print(osa_serial)


rm = pyvisa.ResourceManager()
print(rm.list_resources())

osa = rm.open_resource('ASRL4')