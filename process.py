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

def maskoutbottle(img):
    im = img.copy()
    gray =  cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    filtro = exposure.rescale_intensity(gray,(70,123))
    filtro = cv2.blur(filtro, (13,13))
    filterimg = cv2.subtract(gray, filtro)
    
    color = cv2.cvtColor(filterimg, cv2.COLOR_GRAY2BGR) 
    return color

def mask2(img):
    im =img.copy()
    fil = exposure.rescale_intensity(im, (61,104))
    gr = cv2.cvtColor(fil, cv2.COLOR_BGR2GRAY)
    th =  cv2.inRange(gr, 10, 255)
    #DIPLIB
    grd = dip.ColorSpaceManager.Convert(th, 'grey')
    thd = grd > 128
    mea = dip.EdgeObjectsRemove(thd)
    mea = dip.Label(thd, minSize=30)
    if dip.Maximum(mea)[0] == 0:
        return im
    m = dip.MeasurementTool.Measure(mea,gr,['Size'])
    if m.NumberOfObjects() == 0:
        return im
    sel = m['Size'] > 2500
    reac = sel.Apply(mea)
    #OPENCV
    op1 = np.array(reac).astype(np.uint8) * 255
    inter = cv2.subtract(gr, op1)
    th2 = cv2.inRange(inter,10,255)
    ker1 = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    ker2 = np.array((5,5)).astype(np.uint8)
    ero = cv2.erode(th2, ker2, iterations=1)
    dil = cv2.dilate(ero, ker1, iterations=5)
    #DIPLIB
    dpi =  dip.ColorSpaceManager.Convert(dil, 'grey')
    thd2 = dpi > 128
    mea2 = dip.EdgeObjectsRemove(thd2)
    mea2 = dip.Label(thd2, minSize=30)
    m2 = dip.MeasurementTool.Measure(mea2,dpi,['Size'])
    if m2.NumberOfObjects() == 0:
        return im
    sel2 = ((m2['Size'])< 5000)
    re =  sel2.Apply(mea2)
    ret = np.array(re).astype(np.uint8) * 255
    casimsk = cv2.subtract(inter, ret)
    ker3 = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    shar = cv2.filter2D(casimsk, -1, ker3)
    th3 = cv2.inRange(shar, 200, 255)
    ker4 = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    dil1 =  cv2.dilate(th3, ker4, iterations=5)
    #DipLib
    dp3 =  dip.ColorSpaceManager.Convert(dil1, 'grey')
    thd3 = dp3 > 128
    mea3 = dip.EdgeObjectsRemove(thd3)
    mea3 = dip.Label(thd3, minSize=30)
    m3 = dip.MeasurementTool.Measure(mea3,dp3,['Size'])
    if m3.NumberOfObjects() == 0:
        return im
    sel3 = ((m3['Size']< 2500))
    re =  sel3.Apply(mea3)
    res3 =  np.array(re).astype(np.uint8) * 255
    msk3 =  cv2.subtract(casimsk, res3)
    th4 = cv2.inRange(msk3, 200,240)
    dil4 =  cv2.dilate(th4, ker4, iterations=15)
    inf =  cv2.countNonZero(dil4)
    #DIPLIB
    if inf > 0:
        dp5 = dip.ColorSpaceManager.Convert(dil4, 'grey')
        thd5 = dp5 > 128
        mea5 = dip.EdgeObjectsRemove(thd5)
        mea5 = dip.Label(thd5, minSize=30)
        m5 = dip.MeasurementTool.Measure(mea5,dp5,['Size'])
        sel5 = ((m5['Size']> 5000))
        re5 = sel5.Apply(mea5)
        res5 = np.array(re5).astype(np.uint8) * 255
    else:
        res5 = dil4
    
    mskfin =  cv2.subtract(msk3, res5)
    return mskfin

def position(img, ori):
    try:
        im = img.copy()
        ker = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        ker2 = np.array((5,5)).astype(np.uint8)
        ker3 =  cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
        shar = cv2.filter2D(im, -1, ker)
        th = cv2.inRange(shar, 150, 255)
        ero1 = cv2.erode(th, ker2, iterations=1)
        dil1 = cv2.dilate(ero1, ker3, iterations=3)
        #DipLib
        dpi = dip.ColorSpaceManager.Convert(dil1, 'grey')
        dth = dpi > 128
        mea = dip.EdgeObjectsRemove(dth)
        mea = dip.Label(dth, minSize=30)
        m = dip.MeasurementTool.Measure(mea,dpi,['Size'])
        if m.NumberOfObjects() == 0:
            return im
        sel = ((m['Size'] > 800))
        reac = sel.Apply(mea)
        opp = np.array(reac).astype(np.uint8) * 255
        ker4 = np.ones((3,3), np.uint8)
        trns = cv2.morphologyEx(opp, cv2.MORPH_CLOSE, ker4, iterations=1)
        #DIPLIB
        dpi2 = dip.ColorSpaceManager.Convert(trns, 'grey')
        dth2 = dpi2 > 128
        mea2 = dip.EdgeObjectsRemove(dth2)
        mea2 = dip.Label(dth2, minSize=30)
        m2 = dip.MeasurementTool.Measure(mea2,dpi2,['Perimeter','Roundness','P2A','EllipseVariance'])
        sel2 = ((m2['SolidArea'] >1208) & (m2['SolidArea'] < 1550))
        reac2 = sel2.Apply(mea2)
        opp2 = np.array(reac2).astype(np.uint8) * 255
        res1 = cv2.subtract(opp, opp2)
        #DIPLIB
        dpi3 = dip.ColorSpaceManager.Convert(res1, 'grey')
        dth3 = dpi3 > 128
        mea3 = dip.EdgeObjectsRemove(dth3)
        mea3 = dip.Label(dth3, minSize=30)
        m3 = dip.MeasurementTool.Measure(mea3,dpi3,['Perimeter','Roundness','P2A','EllipseVariance'])
        sel3 = ((m3['SolidArea'] >1150)&(m3['SolidArea'] <1300)&(m3['Roundness']>0.3)
                &(m3['EllipseVariance']> 0.2))
        reac3 = sel3.Apply(mea3)
        res3 = np.array(reac3).astype(np.uint8) * 255
        ress = cv2.subtract(res1, res3) 
        return ress
    except:
        return img