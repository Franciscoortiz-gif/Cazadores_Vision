import cv2
import numpy as np
import diplib as dip
import skimage.exposure as exposure

a = 0

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
    return dil

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

def detection(imag, iman):
    global a
    im = imag.copy()
    positions =  []
    im2 = cv2.resize(im, (840,520))
    im3 = cv2.resize(iman, (840,520))
    con, _ = cv2.findContours(im2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in con:
        x,y,w,h = cv2.boundingRect(cnt)
        frame = cv2.rectangle(im3, (x,y), (x+w,y+h), (255,255,0), 2)
        #print(x,y,w,h)
        positions.append(x)
        positions.append(y)
        
    for i in range(0,4):
        if(positions[i] > 380 and positions[i]<400):
            if i == 0:
                cnx = positions[i]
                cny =  positions[i+1]
                oux = positions[i+2]
                ouy = positions[i+3]
                break
            else:
                cnx = positions[i]
                cny =  positions[i+1]
                oux = positions[i-2]
                ouy = positions[i-1]
                break
        else:
            continue
        
    difx = cnx - oux
    dify = cny - ouy
    if difx < 0:
        difx = difx * -1
    else:
        pass
    if dify < 0:
        dify = dify * -1
    else:
        pass
    if difx > dify:
        result = 1 #1 es derecha, 2 es abajo, 3 es izquierda, 4 es arriba
    
    if dify > difx:
        result = 2

    if a == 1:
        result = 2 
    if a == 2:
        result = 2             
    a += 1
    print(a,  result)
    return iman, result

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
    krn = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    res =  exposure.rescale_intensity(im, (38,231))
    res2 =  exposure.rescale_intensity(im, (127,128))
    dil = cv2.dilate(res2, krn, iterations=1)
    resu = cv2.subtract(res, dil)
    kernel = np.array([[0,-1, 0], [-1,5,-1], [0,-1,0]])
    im4 = cv2.filter2D(resu, -1, kernel)
    bn =  cv2.inRange(res, 38,100)
    im2 =  cv2.dilate(bn, krn, iterations=10)
    #DIPLIB Quitar objetos grandes y muy pequenos
    imd = dip.ColorSpaceManager.Convert(im2, 'grey')
    bim = imd > 128
    mea = dip.EdgeObjectsRemove(bim)
    mea = dip.Label(bim, minSize=30)
    m = dip.MeasurementTool.Measure(mea, imd, ['Size','SolidArea', 'Perimeter','Convexity','Circularity'])
    sel1 = ((m['Size'] > 4000))
    sel1.Relabel()
    resul1 = sel1.Apply(mea)
    #OPENCV
    lett = np.array(resul1).astype(np.uint8) * 255
    lett = cv2.dilate(lett, krn, iterations=2)
    imd2 = dip.ColorSpaceManager.Convert(lett, 'grey')
    bim2 = imd2 > 128
    mea2 = dip.EdgeObjectsRemove(bim2)
    mea2 = dip.Label(bim2, minSize=30)
    m2 = dip.MeasurementTool.Measure(mea2, imd2, ['Size','SolidArea', 'Perimeter','ConvexArea','Circularity'])
    sel2 = ((m2['Size'] > 6000)& (m2['Perimeter'] > 470)& (m2['ConvexArea'] > 11300))
    sel2.Relabel()
    res2 = sel2.Apply(mea2)
    #OPENCV
    lett2 = np.array(res2).astype(np.uint8) * 255
    lett3 = cv2.erode(lett2, krn, iterations=5)
    place =  lett3
    return place
    
def maskoutside(img):
    im = img.copy()
    sharp =  exposure.rescale_intensity(im, (32,223))
    th =  cv2.inRange(sharp, 30, 255)
    kr =  cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    kr2 =  cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
    ero = cv2.erode(th,kr2,iterations=1)
    dil =  cv2.dilate(ero, kr, iterations=2)
    #DIPLIB
    dim =  dip.ColorSpaceManager.Convert(dil, 'grey')
    bim = dim > 128
    mea = dip.EdgeObjectsRemove(bim)
    mea = dip.Label(bim, minSize=30)
    m = dip.MeasurementTool.Measure(mea, dim, ['Size','SolidArea', 'Perimeter','Radius','Circularity'])
    sel1 = ((m['Size'] > 1100))
    sel1.Relabel()
    ltclear = sel1.Apply(mea) 
    #OPENCV
    mask1 = np.array(ltclear).astype(np.uint8) * 255
    kr3 =  cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    dila =  cv2.dilate(mask1, kr3,iterations=20)
    inv = cv2.subtract(im, dila)
    return inv

