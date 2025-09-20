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

def clearletters(img):
    im = img.copy()
    dp = np.array(im).astype(np.uint8)
    gr = dip.ColorSpaceManager.Convert(dp, 'grey')
    th = gr > 128
    lbl = dip.EdgeObjectsRemove(th)
    lbl = dip.Label(th, minSize=30)
    m = dip.MeasurementTool.Measure(lbl,gr,['Size', 'Perimeter'])
    sel = ((m['Size'] > 600) & (m['Size'] < 1700) & (m['Perimeter']> 15)& (m['Perimeter']< 220) )
    selc = sel.Apply(lbl)
    a =  np.array(selc).astype(np.uint8) * 255
    th2 =  a > 128
    lbl1 = dip.EdgeObjectsRemove(th2)
    lbl1 = dip.Label(th2, minSize= 30)
    m2 = dip.MeasurementTool.Measure(lbl1, selc, ['Size','Perimeter'])
    print(m2)
    step1 = np.array(selc).astype(np.uint8) * 255
    
    return step1
    

