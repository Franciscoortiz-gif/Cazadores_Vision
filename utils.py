import cv2
import numpy as np

isver = {}
ishor = {}
Angle = {"Angle": 0}
size = {"width": 540, "height": 540, "Tolerance": 15}

def processdetection(mask, ori):
    global isver, ishor, size, Angle
    im =  mask.copy()
    out1 =  ori.copy()
    isver = {}
    ishor = {}
    Angle = {"Angle": 0}
    tmpHor =  cv2.imread('Template/TMP1.png',0)
    tmpVer = cv2.imread('Template/TMP2.png', 0)
    tmpVer2 =  cv2.imread('Template/TMP3.png', 0)
    if tmpHor is not None and tmpVer is not None and tmpVer2 is not None:
        wver, hver =  tmpVer.shape[::-1]
        wver2, hver2 =  tmpVer2.shape[::-1]
        whor, vhor = tmpHor.shape[::-1]
        
        resh = cv2.matchTemplate(im, tmpHor, cv2.TM_CCOEFF_NORMED)
        resv = cv2.matchTemplate(im, tmpVer, cv2.TM_CCOEFF_NORMED)
        resv2 =  cv2.matchTemplate(im, tmpVer2, cv2.TM_CCOEFF_NORMED)
        thresold = 0.6
        thresold2 = 0.8
        loch =  np.where(resh >= thresold)
        locv = np.where(resv >= thresold)
        locv2 = np.where(resv2 >= thresold2)
        for pt in zip(*loch[::-1]):
            cv2.rectangle(out1, pt,(pt[0] + whor, pt[1] + vhor), (255,255,0), 2)
            ishor = {"x": pt[0], "y": pt[1], "Orientation": "Horizontal"}  
        
        for pt1 in zip(*locv[::-1]):
            cv2.rectangle(out1, pt1, (pt1[0] + wver, pt1[1] + hver), (255,0,255), 2)
            isver = {"x": pt1[0], "y": pt1[1], "Orientation": "Vertical"}
        
        for pt2 in zip(*locv2[::-1]):
            cv2.rectangle(out1, pt2, (pt2[0]+ wver2, pt2[1] + hver2), (0,255,255),2)
            isver = {"x": pt2[0], "y": pt2[1], "Orientation": "Vertical"}

        if ishor == {}:
            cv2.putText(out1, "Orientation: " + str(isver["Orientation"]),
                        (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2,cv2.LINE_4)
            cv2.putText(out1, "Position X: " + str(isver["x"]),
                        (10,60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2,cv2.LINE_4)
            cv2.putText(out1, "Position Y: " + str(isver["y"]),
                        (10,90), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2,cv2.LINE_4)
            cntr = size["height"] / 2
            if isver["x"] < cntr:
                Angle["Angle"] = 90
            elif isver["x"] > cntr:
                Angle["Angle"] = 270
            else:
                Angle["Angle"] = 0
            cv2.putText(out1, "Rotation Angle: " + str(Angle["Angle"]),
                        (10,120), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2,cv2.LINE_4)
        elif isver == {}:
            cv2.putText(out1, "Orientation: " + str(ishor["Orientation"]),
                        (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2,cv2.LINE_4)
            cv2.putText(out1, "Position X: " + str(ishor["x"]),
                        (10,60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2,cv2.LINE_4)
            cv2.putText(out1, "Position Y: " + str(ishor["y"]),
                        (10,90), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2,cv2.LINE_4)
            cntr = size["width"] / 2
            if ishor["y"] < cntr:
                Angle["Angle"] = 180
            elif ishor["y"] > cntr:
                Angle["Angle"] = 0
            else:
                Angle["Angle"] = 0
            cv2.putText(out1, "Rotation Angle: " + str(Angle["Angle"]),
                        (10,120), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2,cv2.LINE_4)
        
        result = out1.copy()
        
        return result, Angle
    else:
        return out1
        
        
    
        
    
    

    