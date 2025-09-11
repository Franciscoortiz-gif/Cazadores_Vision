import minimalmodbus as mb
import serial
import time

comm = None

def init():
    global comm#port,
    comm = mb.Instrument('/dev/ttyUSB0',1)
    comm.serial.baudrate = 9600
    comm.serial.bytesize = 7
    comm.serial.parity = serial.PARITY_EVEN
    comm.serial.stopbits = 1
    comm.serial.timeout = 2 
    comm.mode = mb.MODE_ASCII  
    #port  = sr.Serial(port='/dev/ttyUSB0', baudrate=9600, bytesize=7,timeout=2, parity=sr.PARITY_EVEN, stopbits=sr.STOPBITS_ONE)
    
def processplc(data):
    init()
    global comm
    comm.write_bit(1280, 0, 5)
    comm.write_bit(1281, 0, 5)
    if data == 1:
        try:
            comm.write_bit(1280, 1, 5)
        except:
            pass
    
    if data == 2:
        try:
            comm.write_bit(1281, 1, 5)
        except:
            pass