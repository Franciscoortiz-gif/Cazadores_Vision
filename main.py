import cv2
import numpy as np
from skimage import exposure as ex
from process import clearimage
from process import clearobjects
from process import detection
from process import mask, findcenterbottle, findlettersoutside
#Imagenes de la carpeta /im
filenames = ['img/1.png', 'img/2.png', 'img/3.png', 'img/4.png', 'img/5.png'
             , 'img/6.png']

a = 0
b = 0

def main():
    global a
    cap = cv2.VideoCapture('/dev/video2')
    
    while True:
        if cap is not None:
            ret, frame = cap.read()
            if ret == True:
                im = contrastadjust(frame)
                cl = clearimage(im)
                maks = mask(cl)
                outsid, cente =  clearobjects(maks)
                centerr =  findcenterbottle(cente)
                bottlelet = findlettersoutside(outsid)
                #det = detection(cente)
                if cv2.waitKey(1) == ord('c'):
                    a += 1
                    cv2.imwrite('im/'+str(a)+'.png', frame)
                    
                cv2.imshow('camera',cente)
                
                if cv2.waitKey(1) == ord('q'):
                    cv2.destroyAllWindows()
                    cap.release()
                    break
            else:
                print('camera not readable')
                readimages()
                cap.release()
                break
                

        else:
            print('camera not found')
            break
            
            
            
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
            outside,center = clearobjects(im4)
            bottlecenter =  findcenterbottle(center)
            bottleletters = findlettersoutside(outside)
            im3 = detection(im4)
            irez = cv2.resize(bottleletters, (840,540))
            b += 1
            #cv2.imwrite('im/'+str(b)+'.png', ima)
            cv2.imshow('foto', irez)
            cv2.waitKey(0)
            cv2.destroyAllWindows()     
            
            
            
if __name__ == '__main__':
    main()