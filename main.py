import cv2
import numpy as np
from skimage import exposure as ex
from process import clearimage

filenames = ['images/1.jpg', 'images/2.jpg', 'images/3.jpg', 'images/4.jpg']

def main():
    cap = cv2.VideoCapture('/dev/video0')
    
    while True:
        if cap is not None:
            ret, frame = cap.read()
            if frame is not None:
                #cv2.imwrite('images/11.png', frame)
                im = contrastadjust(frame)
                cl = clearimage(im)
                cv2.imshow('camera',cl)
                if cv2.waitKey(1) == ord('q'):
                    cv2.destroyAllWindows()
                    cap.release()
                    break
            else:
                print('camera not readable')
                cap.release()
                

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
    for x in filenames:
        img = cv2.imread(x)
        if img is not None:
            im = img.copy()
            contrast = contrastadjust(im)
            ima = cv2.resize(contrast, (700,500))
            cv2.imshow('foto', ima)
            cv2.waitKey(0)
            cv2.destroyAllWindows()     
            
            """labimg =  cv2.cvtColor(im, cv2.COLOR_BGR2LAB)
            l,a,b = cv2.split(labimg)
            clahe = cv2.createCLAHE(clipLimit=12.0, tileGridSize=(38,38))
            cl = clahe.apply(l)
            im2 = cv2.merge((cl,a,b))
            col = cv2.cvtColor(im2, cv2.COLOR_LAB2BGR)"""  
            
if __name__ == '__main__':
    main()