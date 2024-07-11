
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
import matplotlib.pyplot as plt

def run_example():
    wl_plot = []
    pow_plot = []
    try:
        
        scpi = pyBristolSCPI()
        laser = laserClass()
        scpi.sendSimpleMsg(b'CALC2:SCAL PEAK\r\n')
    except Exception as e:
        print('cannot connect to device: {}'.format(e))
        return 1
    
    cont_flag = 'y'
    while(cont_flag.lower() == 'y' ):
        laser.sweep_init()
        
        n = laser.n_samples

        input("Press Enter to Start Sweep")

        plt.close()
        fig = plt.figure(num=1,figsize=(15,7))
        ax = fig.add_subplot(1,1,1)
        wl_plot = []
        pow_plot = [] 
        while laser.sweep_hasnext:
            print("Wait 4s for laser to stabilize")
            time.sleep(4)
            print("Current Channel: ",laser.curr_ch)

            for i in range(0,n):
                wl = scpi.readWL()
                pow = scpi.readPOW()
                wl_plot.append(wl)
                pow_plot.append(pow)
                print('wavelength = {}, power {}'.format(wl,pow))
            
            
            ax.clear()
            ax.set_title("_linegraph")
            ax.set_xlabel("Wavelength (nm)")
            ax.set_ylabel("Output Power (dBm)")
            ax.grid(alpha=0.7)
            ax.plot(wl_plot,pow_plot)
            # plt.savefig(graph_dir+"/"+name+"_linegraph.png")
            plt.draw()
            plt.pause(0.1)


            

            laser.next_wl()

        plt.close()
        plt.figure(figsize=(15,7))
        plt.plot(wl_plot,pow_plot)
        plt.title("_linegraph")
        plt.xlabel("Wavelength (nm)")
        plt.ylabel("Output Power (dBm)")
        plt.grid(alpha=0.7)
        # plt.savefig(graph_dir+"/"+name+"_linegraph.png")
        plt.show()
        plt.close()
        cont_flag = input("Start another run?(y/n)")


   
    return 0

print('running example')
run_example()