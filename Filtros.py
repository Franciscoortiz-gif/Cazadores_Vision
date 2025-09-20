import cv2
import numpy as np
from skimage import exposure as ex
from process import clearimage
from process import clearobjects
from process import detection, increase_brightness
from process import maskoutbottle, clearletters
from PLC import processplc
#Imagenes de la carpeta /im

a = 0
b = 0
c = 1

def filtros(frame):
    global a,b
    
    if frame is not None:
        im = contrastadjust(frame)
        #cl = clearimage(im)
        #maks = mask(cl)
        #outsid, cente =  clearobjects(maks)
        #outmask = maskoutside(cl)
        #centerr =  findcenterbottle(cente)
        #bottlelet = findlettersoutside(outsid)
        #dates =  cv2.add(centerr, bottlelet)
        #det, data = detection(dates)
        #processplc(data)
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
            mask =  maskoutbottle(im)
            brig = increase_brightness(mask, value=30)
            contrast = contrastadjust(brig)
            defition = clearobjects(contrast)
            ima = clearimage(defition)
            letters = clearletters(ima)
            #bottlecenter =  findcenterbottle(center)
            #bottleletters = findlettersoutside(outmask)
            #dates= cv2.add(bottlecenter, bottleletters)
            #im3, direction = detection(dates, im)
            #processplc(direction)
            b += 1
            #cv2.imwrite('images/'+str(b)+'.png', brig)
            cv2.imshow('foto', letters)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            c += 1
        else:
            break
        