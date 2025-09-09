import cv2
import numpy as np
import diplib as dip

def clearimage(img):
    im = img.copy()
    ker = np.ones((9,9), np.uint8)
    clea = cv2.morphologyEx(im, cv2.MORPH_TOPHAT, ker)
    return clea

def detectionorange(imag):
    im = imag.copy()
    