import cv2
import numpy as np
from skimage import exposure as ex
from process import clearimage
from process import clearobjects
from process import detection, maskoutside
from process import mask, findcenterbottle, findlettersoutside
from PLC import processplc
#Imagenes de la carpeta /im
filenames = ['img/1.png', 'img/3.png', 'img/4.png', 'img/5.png'
             , 'img/6.png']

a = 0
b = 0

def filtros(frame):
    global a
    
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
    imsk = np.array(gr).astype(np.uint8)
    im3 = ex.rescale_intensity(imsk, in_range=(44,209))
    kernel = np.array([[0,-1, 0], [-1,5,-1], [0,-1,0]])
    im4 = cv2.filter2D(im3, -1, kernel)
    return im4
   

def readimages():
    global b
    for x in filenames:
        img = cv2.imread(x)
        if img is not None:
            im = img.copy()
            contrast = contrastadjust(im)
            ima = clearimage(contrast)
            im4 = mask(ima)
            outmask =  maskoutside(ima)
            center = clearobjects(im4)
            outsi = clearobjects(outmask)
            bottlecenter =  findcenterbottle(center)
            bottleletters = findlettersoutside(outmask)
            dates= cv2.add(bottlecenter, bottleletters)
            im3, direction = detection(dates, im)
            processplc(direction)
            b += 1
            #cv2.imwrite('im/'+str(b)+'.png', ima)
            cv2.imshow('foto', im3)
            cv2.waitKey(0)
            cv2.destroyAllWindows()     