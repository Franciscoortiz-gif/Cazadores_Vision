import cv2
import numpy as np
import diplib as dip
import skimage.exposure as exposure

a = 0

def increase_brightness(img, value=30):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    lim = 255 - value
    v[v > lim] = 255
    v[v <= lim] += value

    final_hsv = cv2.merge((h, s, v))
    img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    return img

def clearimage(img):
    im = img.copy()
    dp = np.array(im).astype(np.uint8)
    gr = dip.ColorSpaceManager.Convert(dp, 'grey')
    th = gr > 128
    mea = dip.EdgeObjectsRemove(th)
    mea = dip.Label(th, minSize=30)
    m = dip.MeasurementTool.Measure(mea,gr,['Size'])
    #print(m)
    sel = ((m['Size'] < 2500)& (m['Size']>600))
    measure = sel.Apply(mea)
    ##Opencv
    meas = np.array(measure).astype(np.uint8) * 255
    return meas

def clearobjects(imag):
    im = imag.copy()
    ker = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    ker2 = np.array((5,5)).astype(np.uint8)
    ero = cv2.erode(im, ker2, iterations=1)
    dila = cv2.dilate(ero, ker,iterations=3)
    return dila

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

def maskoutbottle(img):
    im = img.copy()
    gray =  cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    filtro = exposure.rescale_intensity(gray,(70,123))
    filtro = cv2.blur(filtro, (13,13))
    filterimg = cv2.subtract(gray, filtro)
    
    color = cv2.cvtColor(filterimg, cv2.COLOR_GRAY2BGR) 
    return color

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
    

