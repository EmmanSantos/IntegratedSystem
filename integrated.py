


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
from multiprocessing import Process
import multiprocessing as mp

def dir_create():
   
    dir_dict = {
        "csv_dir" : "./OUTPUT_FILES/csv_outputs",
        "avg_csv_dir" : "./OUTPUT_FILES/csv_averaged",
        "graph_dir" :"./OUTPUT_FILES/graphs"
    }

    for value in dir_dict.values():
        if not os.path.exists(value):
            os.makedirs(value)
    return dir_dict

def plot_subproc(x_q: mp.Queue,y_q: mp.Queue,name):
    plt.close()

    x_data,y_data=[],[]

    figure = plt.figure(num=1,figsize=(15,7))
    ax = figure.add_subplot(1,1,1)
    ax.clear()
    ax.set_title(name)
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Output Power (dBm)")
    ax.grid(alpha=0.7)
    # ax.plot(wl_plot,pow_plot)
    line, = plt.plot(x_data, y_data, '-')


    def update(frame,x_q: mp.Queue,y_q: mp.Queue):
        if x_q.empty() == False:
            y_data.append(y_q.get())
            x_data.append(x_q.get())

        line.set_data(x_data, y_data)
        figure.gca().relim()
        figure.gca().autoscale_view()
        return line,

    animation = FuncAnimation(figure, update,fargs=[x_q,y_q], interval=200)
    plt.show()

def store_to_csv(name,dir,col1,col2):

    with open(dir+"/"+name+".csv", mode='w', newline='') as file:
        csv_writer = csv.writer(file)
        header = ['Wavelength', 'Power']
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
    except Exception as e:
        print('Cannot connect to device: {}'.format(e))
        return 1
    

    cont_flag = 'y' #Used to indicate if user wants another run
    while(cont_flag.lower() == 'y' ):
        


        laser.sweep_init()
        
        n = laser.n_samples

        while(True):

            #Following code is for validating filename
            try:
                name = input("Enter file name for this test: ")
                ts = datetime.datetime.now().strftime("%Y%m%d-%H_%M_%S")
            except Exception as e:
                print('Input error: {}'.format(e))
                continue
            try:
                filename = name+"-"+ts
                validate_filename(filename,platform="Windows")
            except ValidationError as e:
                print(f"{e}\n", file=sys.stderr)
                continue
           
            print(filename)
            
            break
        
        l_plot = []
        pow_plot = []
            
        input("Press Enter to Start Sweep")

        # Instantation for plot subprocess
        y_q = mp.Queue()
        x_q = mp.Queue()
        plot = mp.Process(target=plot_subproc,args=[x_q,y_q,filename])
        plot.start()



        while laser.ch_in_range:
            print("Wait 5s for laser to stabilize")
            time.sleep(5)
            print("Current Channel: ",laser.curr_ch)

            for i in range(0,n):
                wl = scpi.readWL()
                pow = scpi.readPOW()
                wl_plot.append(wl)
                pow_plot.append(pow)

                x_q.put(wl)
                y_q.put(pow)

                print('wavelength = {}, power {}'.format(wl,pow))
            

            laser.next_wl()
            
        plot.terminate()
            

        print("\nSweep Finished\nClose graph to continue")
        plt.close()
        plt.figure(figsize=(15,7))
        plt.plot(wl_plot,pow_plot)
        plt.title(filename)
        plt.xlabel("Wavelength (nm)")
        plt.ylabel("Output Power (dBm)")
        plt.grid(alpha=0.7)
        plt.savefig(dir_dict['graph_dir']+"/"+filename+"_linegraph.png")
        plt.show()
        plt.close()

        store_to_csv(filename,dir_dict['csv_dir'],wl_plot,pow_plot)

        cont_flag = input("Start another run?(y/n)")


   
    return 0
if __name__ == '__main__':
    print('Running Integrated System')
    mp.freeze_support()
    main()
    input("Enter to Close")

