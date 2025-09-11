import cv2
import numpy as np
import diplib as dip
import skimage.exposure as exposure

def clearimage(img):
    im = img.copy()
    ker = np.ones((9,9), np.uint8)
    clea = cv2.morphologyEx(im, cv2.MORPH_TOPHAT, ker)
    return clea

def clearobjects(imag):
    im = imag.copy()
    im2 = exposure.rescale_intensity(im, (21,231))
    #im2 = cv2.blur(im2, (3,3))
    co = cv2.cvtColor(im2, cv2.COLOR_GRAY2BGR)
    llab = cv2.cvtColor(co, cv2.COLOR_BGR2LAB)
    l,a,b = cv2.split(llab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(10,10))
    lcha = clahe.apply(l)
    con = cv2.merge((lcha,a,b))
    im3 = cv2.cvtColor(con, cv2.COLOR_LAB2BGR)
    gr = cv2.cvtColor(im3, cv2.COLOR_BGR2GRAY)
    kern = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
    clean = cv2.erode(gr,kern, iterations=1)
    blur = cv2.blur(clean, (3,3))
    lis = cv2.inRange(blur, 30,255)
    dil = cv2.dilate(lis, kern, iterations=5)
    dil2 = cv2.dilate(lis, kern, iterations=10)
    return dil2, dil

def mask(img):
    #OPENCV
    im = img.copy()
    res = exposure.rescale_intensity(im, (127,128))
    ker = cv2.getStructuringElement(cv2.MORPH_RECT, (4,4))
    ker2 = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
    ero = cv2.erode(res, ker2, iterations=1)
    dil = cv2.dilate(ero, ker,iterations=9)
    #DIPLIB
    dpim =  np.asarray(dil).astype(np.uint8)
    dim = dip.ColorSpaceManager.Convert(dpim, 'grey')
    bni = dim > 128
    mea = dip.EdgeObjectsRemove(bni)
    mea = dip.Label(bni, minSize=30)
    m = dip.MeasurementTool.Measure(mea, dim, ['Size','SolidArea', 'Perimeter','Radius','Circularity']) 
    sel1 = ((m['Size'] > 4500) & (m['Size'] < 6800))
    sel1.Relabel()
    resul1 = sel1.Apply(mea)
    #OPENCV
    ope1 = np.array(resul1).astype(np.uint8) * 255
    mas = cv2.bitwise_xor(dil, ope1)
    #DIPLIB
    dp = np.asarray(mas).astype(np.uint8)
    imd = dip.ColorSpaceManager.Convert(dp,'grey')
    biim =  imd > 128
    man = dip.EdgeObjectsRemove(biim)
    man = dip.Label(biim,minSize=30)
    m2 = dip.MeasurementTool.Measure(man, imd, ['Size'])
    se2 = (m2['Size'] > 900)
    se2.Relabel()
    final = se2.Apply(man)
    #OPENCV
    imop = np.array(final).astype(np.uint8) * 255
    cleanmask = cv2.bitwise_and(im,im,mask=imop)
    cleanimg =  cv2.bitwise_xor(im, cleanmask)
    return cleanimg

def detection(imag):
    im = imag.copy()
    #DIPLIB ZONE
    dipim = np.asarray(im).astype(np.uint8)
    gr =  dip.ColorSpaceManager.Convert(dipim, 'grey')
    dth = gr > 128
    mea = dip.EdgeObjectsRemove(dth)
    mea = dip.Label(dth, minSize=30)
    m = dip.MeasurementTool.Measure(mea, gr, ['Size','SolidArea', 'Perimeter','Radius']) 
    #print(m)
    sel = ((m['Size'] > 1000) & (m['Size'] < 5500) & (m['Perimeter'] > 110) & (m['Perimeter']<405))
    sel.Relabel()
    resul = sel.Apply(mea)
    ope = np.array(resul).astype(np.uint8) * 255
    return ope

def findcenterbottle(img):
    im = img.copy()
    #DIPLIB
    dpim = dip.ColorSpaceManager.Convert(im, 'grey')
    binim =  dpim > 128
    mea = dip.EdgeObjectsRemove(binim)
    mea = dip.Label(binim, minSize=30)
    m = dip.MeasurementTool.Measure(mea, dpim, ['Size','SolidArea', 'Perimeter','Radius'])
    selec = ((m['Size'] > 1100)& (m['Size'] < 4500))
    selec.Relabel()
    cen =  selec.Apply(mea)
    #OPENCV
    center =  np.array(cen).astype(np.uint8) * 255
    krn = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    dil1 = cv2.dilate(center, krn, iterations=10)
    #DIPLIB
    dpim2 = dip.ColorSpaceManager.Convert(dil1, 'grey')
    bim2 =  dpim2 > 128
    me1 = dip.EdgeObjectsRemove(bim2)
    me1 = dip.Label(bim2, minSize=30)
    m1 = dip.MeasurementTool.Measure(me1, dpim2, ['Size','SolidArea', 'Perimeter','Radius'])
    selec2 = ((m1['Perimeter'] > 400.0)& (m1['Perimeter'] < 700.0))
    selec2.Relabel()
    cen2 =  selec2.Apply(me1)
    cntr =  np.array(cen2).astype(np.uint8) * 255
    krn2 =  cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    cnero =  cv2.erode(cntr,krn2, iterations=10)
    return cnero

def findlettersoutside(img):
    im = img.copy()
    #DIPLIB Quitar objetos grandes y muy pequenos
    imdp = dip.ColorSpaceManager.Convert(im, 'grey')
    dth = imdp > 128
    mea = dip.EdgeObjectsRemove(dth)
    mea = dip.Label(dth, minSize=30)
    m = dip.MeasurementTool.Measure(mea, imdp, ['Size','SolidArea', 'Perimeter','Radius','Circularity']) 
    sel1 = ((m['Size'] > 1000) & (m['Size'] < 3000))
    sel1.Relabel()
    ltclear = sel1.Apply(mea)
    print(m)
    #Opencv Resultado
    littleobj = np.array(ltclear).astype(np.uint8) * 255
    return littleobj    
    
