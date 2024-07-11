
## @example scpi_example.py
# This is an example using the bristolSCPI python class. 
# @details There are some general functions that are 
# common to our instruments, and some special functions that are instrument specific.
# The instrument specific examples have been commented out. Simply uncomment them to run.
#
# Example:

from pyBristolSCPI import *
import time
from laserRS232 import laserClass

def run_example():
    try:
        
        scpi = pyBristolSCPI()
        laser = laserClass()
    except Exception as e:
        print('cannot connect to device: {}'.format(e))
        return 1
    
    laser.sweep_init()
    laser.sweep_init()
    scpi.sendSimpleMsg(b'CALC2:SCAL REF\r\n')

    id = scpi.getSimpleMsg(b':STAT:QUES:COND?\r\n')
    print("Test ",format(id))
    #general instructions
    for i in range (0,10):
        wl = scpi.readWL()
        pow = scpi.getSimpleMsg(b'FETC:SCAL:POW?\r\n')
        print('wavelength = {}, power {}'.format(wl,pow.decode('ascii')))

   

    #specific instructions for 428, 438, 771 Laser Spectrum Analyzers
    # scpi.getWLSpectrum('calc3_output.txt')
    # scpi.getSpectrum()

    #specific instructions for 871, 828 Laser Wavelength Meters
    # scpi.startBuffer()
    # print('Acquiring 2 seconds of data...')
    # time.sleep(10)
    # scpi.readBuffer('buffer_output.txt', 10)
   
    return 0

print('running example')
run_example()