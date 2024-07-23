


from pyBristolSCPI import *
import time
from laserRS232 import laserClass
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import os
import csv
import datetime
import sys
from pathvalidate import ValidationError, validate_filename
import multiprocessing as mp
import statistics as stat
from math import log10

def mw_ave_to_dB(input_array):
    mw_array = []
    for a in input_array:
        mw_array.append(10**(a/10))
    
    # total = sum(mw_array)
    # length = len(mw_array)
    # ave_mw = total/length

    ave_mw = stat.mean(mw_array)
    
    ave = 10*log10(ave_mw)
    
    return ave



#Create necessary directories, returns dictionary for use in main()
def dir_create():
   
    dir_dict = {
        "csv_dir" : "./OUTPUT_FILES/csv_outputs",
        "ave_csv_dir" : "./OUTPUT_FILES/csv_averaged",
        "graph_dir" :"./OUTPUT_FILES/graphs"
    }

    for value in dir_dict.values():
        if not os.path.exists(value):
            os.makedirs(value)
    return dir_dict

#Child process for displaying real time plot, passes queues and fileame as arguments

def plot_subproc(x_q: mp.Queue,y_q: mp.Queue,name):
    plt.close()

    x_data,y_data=[],[]

  

    #Update routine that is called by FuncAnimation instance to update plot data, returns 2D tuple that is used to graph
    def update(frame,x_q: mp.Queue,y_q: mp.Queue):

        #check if queue is not empty before getting from queue
        if x_q.empty() == False:
            y_data.append(y_q.get())
            x_data.append(x_q.get())

        line.set_data(x_data, y_data)
        figure.gca().relim()
        figure.gca().autoscale_view()
        return line,

    
    while True:
          #Initialize plot
        figure = plt.figure(num=1,figsize=(15,7))
        ax = figure.add_subplot(1,1,1)
        ax.clear()
        ax.set_title(name)
        ax.set_xlabel("Wavelength (nm)")
        ax.set_ylabel("Output Power (dBm)")
        ax.grid(alpha=0.7)
        line, = plt.plot(x_data, y_data, '-')
        animation = FuncAnimation(figure, update,fargs=[x_q,y_q], interval=200,cache_frame_data=False)
        plt.show()
        time.sleep(1)

    # while True:
    #     
    #     plt.pause(0.1)

def store_to_csv(name,dir,col1,col2):

    with open(dir+"/"+name+".csv", mode='w', newline='') as file:
        csv_writer = csv.writer(file)
        header = ['Wavelength', 'Power']
        csv_writer.writerow([name])
        csv_writer.writerow(header)

        for i in range(0,len(col1)):
            csv_writer.writerow([col1[i],col2[i]])


def main():
    dir_dict = dir_create()
    wl_plot = []
    pow_plot = []
    
    try:
        # Instantiate OSA and laser objects which also initiates connection to both
        scpi = pyBristolSCPI()
        laser = laserClass()
        scpi.sendSimpleMsg(b'CALC2:SCAL PEAK\r\n')
        scpi.sendSimpleMsg(b'UNIT:POW DBM\r\n')
        scpi.sendSimpleMsg(b'UNIT:WAV NM\r\n')
    except Exception as e:
        print('Cannot connect to device: {}'.format(e))
        return 1
    

    cont_flag = 'y' #Used to indicate if user wants another run
    while(cont_flag.lower() == 'y' ):
        

        #Initialize sweep parameters
        laser.sweep_init()
        
        n = laser.n_samples

        #While loop for validating filename
        while(True):

            #Following code is for validating filename; try and except is for checking non character inputs
            try:
                name = input("Enter file name for this test: ")
                ts = datetime.datetime.now().strftime("%Y%m%d-%H_%M_%S")
            except Exception as e:
                print('Input error: {}'.format(e))
                continue
            try:
                filename = name+"-"+ts
                filename_ave = filename + "_ave"
                validate_filename(filename,platform="Windows")
            except ValidationError as e:
                print(f"{e}\n", file=sys.stderr)
                continue
           
            print(filename)
            
            break

        #Reset plot arrays 
        wl_plot = []
        pow_plot = []

        ave_wl_plot = []
        ave_pow_plot = []
            
        input("Press Enter to Start Sweep")

        # Instantation  for Queues; queues can be passed between subprocesses and thus used for passing data
        y_q = mp.Queue()
        x_q = mp.Queue()

        # Instantation for plot subprocess
        plot = mp.Process(target=plot_subproc,args=[x_q,y_q,filename])
        plot.start()


        #  Main sweep loop
        while laser.ch_in_range:
            print("Wait 5s for laser to stabilize")
            time.sleep(5)
            print("Current Channel: ",laser.curr_ch)

            #incremenets number of items to be averaged if wavelength is in range
            ave_counter = 0 
            # Get n measurements and store to respective locations
            for i in range(0,n):
                wl = scpi.readWL()
                pow = scpi.readPOW()

                if(1527<wl and wl<1568):
                    wl_plot.append(wl)
                    pow_plot.append(pow)
                    x_q.put(wl)
                    y_q.put(pow)
                    ave_counter = ave_counter+1
                    print('wavelength = {}, power {}'.format(wl,pow))
                else:
                    print("Wavelength Out of Range; Power reading invalid")


            laser.next_wl()
            #Get average wl and pow of last n measurements 
            if ave_counter>0:
                # ave_wl_plot.append(stat.mean(wl_plot[-n:]))
                # ave_pow_plot.append(stat.mean(pow_plot[-n:]))
                ave_wl_plot.append(mw_ave_to_dB(wl_plot[-n:]))
                ave_pow_plot.append(mw_ave_to_dB(pow_plot[-n:]))
                
                store_to_csv(filename,dir_dict['csv_dir'],wl_plot,pow_plot)
                store_to_csv(filename_ave,dir_dict['ave_csv_dir'],ave_wl_plot,ave_pow_plot)

            else:
                print("Average not executed, n = 0")
            
        plot.terminate()

        store_to_csv(filename,dir_dict['csv_dir'],wl_plot,pow_plot)
        store_to_csv(filename_ave,dir_dict['ave_csv_dir'],ave_wl_plot,ave_pow_plot)
            
        plt.close()
        plt.figure(figsize=(15,7))
        plt.plot(ave_wl_plot,ave_pow_plot)
        plt.title(filename_ave)
        plt.xlabel("Wavelength (nm)")
        plt.ylabel("Output Power (dBm)")
        plt.grid(alpha=0.7)
        plt.savefig(dir_dict['graph_dir']+"/"+filename_ave+".png")
        plt.close()

        print("\nSweep Finished\nClose graph to continue")
        plt.figure(figsize=(15,7))
        plt.plot(wl_plot,pow_plot)
        plt.title(filename)
        plt.xlabel("Wavelength (nm)")
        plt.ylabel("Output Power (dBm)")
        plt.grid(alpha=0.7)
        plt.savefig(dir_dict['graph_dir']+"/"+filename+"_linegraph.png")
        plt.show()
        plt.close()



        cont_flag = input("Start another run?(y/n)")


   
    return 0

# Safeguards for subprocesses
if __name__ == '__main__':
    try:
        print('Running Integrated System')
        mp.freeze_support()
        main()
        input("Enter to Close")
    except:
        print("Error")
        input("Enter to Close")

