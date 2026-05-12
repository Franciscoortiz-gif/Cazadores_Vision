import minimalmodbus as mb
import serial
import time

comm = None
error = False

def init():
    global comm, error
    error = False
    try:
        comm = mb.Instrument('/dev/ttyUSB0',1)
        comm.serial.baudrate = 9600
        comm.serial.bytesize = 7
        comm.serial.parity = serial.PARITY_EVEN
        comm.serial.stopbits = 1
        comm.serial.timeout = 2 
        comm.mode = mb.MODE_ASCII  
        #port  = sr.Serial(port='/dev/ttyUSB0', baudrate=9600, bytesize=7,timeout=2, parity=sr.PARITY_EVEN, stopbits=sr.STOPBITS_ONE)
    except:
        #print("Communication Failed")
        error = True
def processplc(data):
    init()
    global comm, error
    
    AS = {"D0": 40001}
    DVP = {"D0": 4096}
    if error is False:
        if data is not None:
            comm.write_register(AS["D0"], data, 0, 6,signed=True)
    else:
        pass