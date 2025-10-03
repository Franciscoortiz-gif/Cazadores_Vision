import cv2
import numpy as np
from skimage import exposure as ex
from process import increase_brightness
from process import maskoutbottle,mask2, position
from PLC import processplc
from utils import processdetection
#Imagenes de la carpeta /im

a = 0
b = 0
c = 1

def filtros(frame):
    global a,b
    
    if frame is not None:
        im = contrastadjust(frame)

        if cv2.waitKey(1) == ord('c'):
            a += 1
            cv2.imwrite('im/'+str(a)+'.png', frame)
            
        return im
    else:
        pass
            
            
def contrastadjust(imag):
    im = imag.copy()
    
    gr = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    _, th =  cv2.threshold(gr, 67,255, cv2.THRESH_BINARY)
    return th
   

def readimages():
    global b, c

    while True:
        try:
            img = cv2.imread('im/'+str(c)+'.png')
        except:
            pass
        
        if img is not None:
            im = img.copy()
            imori1 =  img.copy()
            mask =  maskoutbottle(im)
            brig = increase_brightness(mask, value=30)
            msk2 = mask2(brig)
            objects = position(msk2, im)
            drawc, Angle = processdetection(objects, imori1)
            processplc(Angle)
            b += 1
            #cv2.imwrite('images/'+str(b)+'.png', brig)
            cv2.imshow('foto', drawc)
            cv2.waitKey(0)
            c += 1
        else:
            break
        