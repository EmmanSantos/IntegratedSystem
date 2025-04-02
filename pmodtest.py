from pmodRS232 import pmodClass

laser = pmodClass()

settings = [1,0,1]
while True:
    settings[0]= int((input("Enter Chan: ")))
    settings[1]= int((input("Enter Off: ")))
    laser.set_wl(settings)
