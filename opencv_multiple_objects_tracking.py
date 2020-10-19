# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import pandas as pd
import numpy as np
import argparse
import imutils
import time
import cv2

vs = cv2.VideoCapture("video4.mp4")
fps = None
tracker = []
initBB = []

fps = vs.get(cv2.CAP_PROP_FPS)

data = None 

timestamps=[]

frame = vs.read()
frame = frame[1]
frame = imutils.resize(frame, width=1200)
(H, W) = frame.shape[:2]

# Define the codec and create VideoWriter object.The output is stored in 'outpy.avi' file.
out = cv2.VideoWriter('C.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 55, (W,H))

old_data_bool=False

try: 
    old_data = pd.read_csv("tracking_data.csv")
    old_data_bool=True
except:
    pass

def addTracker(frame):
    global data

    OPENCV_OBJECT_TRACKERS = {
		"csrt": cv2.TrackerCSRT_create,
		"kcf": cv2.TrackerKCF_create,
		"boosting": cv2.TrackerBoosting_create,
		"mil": cv2.TrackerMIL_create,
		"tld": cv2.TrackerTLD_create,
		"medianflow": cv2.TrackerMedianFlow_create,
		"mosse": cv2.TrackerMOSSE_create
	}

    tracker.append(OPENCV_OBJECT_TRACKERS["csrt"]())
    initBB.append(None)

    #add bounding box
    initBB[-1] = cv2.selectROI("Frame", frame, fromCenter=True, showCrosshair=True)

    if [int(v) for v in initBB[-1]][0]==0:
        initBB.pop(-1)
        tracker.pop(-1)
        return

    #add tracker
    tracker[-1].init(frame, initBB[-1])

    frame = updateCircles(frame)
    
    while True:

        cv2.imshow("Frame", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("s"): 
            addTracker(frame)
            break
            
        elif key == ord("q"): break

def updateTrackers(frame):

    if len(tracker) >0:
        i=0
        for t in tracker:
            if t == None: 
                i+=1
                continue
            (success, box) = t.update(frame)
            if success:
                (x, y, w, h) = [int(v) for v in box]
                centerX = int(x+w/2)
                centerY = int(y+h/2)
                initBB[i] = box
                if centerX<10 or centerY<10 or centerX>W-10 or centerY>H-10:
                    print("remove -> "+str(i))
                    tracker[i] = None
                    initBB[i] = None
            i+=1

    else:
        addTracker(frame)

def updateCircles(frame):

    if len(initBB) >0:
        i=0
        for box in initBB:
            if box == None: 
                pass
            else:
                (x, y, w, h) = [int(v) for v in box]
                centerX = int(x+w/2)
                centerY = int(y+h/2)               
                cv2.circle(frame, (centerX,centerY), 10,(0, 255, 0), 2)
            i+=1
    
    return frame

def updateOldCircles(frame,framenumber):

    for cname in old_data.columns:
        if not 'Unnamed' in cname and  not 'timestamp' in cname and not 'index' in cname:
            if old_data.shape[0]>framenumber:
                if isinstance(old_data.at[int(framenumber),cname], str):
                    tupledata = tuple(map(int, old_data.at[framenumber,cname].replace('(', '').replace(')', '').split(', ') ))
                    centerX= tupledata[0]
                    centerY= tupledata[1]
                    cv2.circle(frame, (centerX,centerY), 1,(0, 255, 0), 2)
                    cv2.putText(frame, cname, (centerX,centerY),cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)
           
    return frame

def updateData():
    global data

    newdata = [timestamps[-1]]
    columns = ['timestamp']

    if len(initBB) >0:
        i=0
        for box in initBB:
            if box == None: 
                newdata.append(None)
            else:
                (x, y, w, h) = [int(v) for v in box]
                centerX = int(x+w/2)
                centerY = int(y+h/2)               
                newdata.append((centerX,centerY))

            i+=1

            columns.append(str(i))

            try:
                if len(data.columns)>i+1:
                    data[str(i)] = pd.Series(np.full(len(data['Timestamp']),None,dtype=tuple), index=data.index)
            except:
                pass

    if len(timestamps)==1:
        data = pd.DataFrame(np.array([newdata]), index=[0], columns=columns)
    else:
        newdata = pd.DataFrame(np.array([newdata]),index=[data.shape[0]], columns=columns)
        data = data.append(newdata)

def mergedata():
    global old_data
    global data
    for oldname in data.columns:
        if not 'Unnamed' in oldname and  not 'timestamp' in oldname and not 'index' in oldname:
            newname = str(len(old_data.columns)-2+int(oldname))
            data = data.rename(columns={oldname: newname })
            print(oldname+ '->'+newname)
            print(str(data[newname].shape))
            print(str(data[data.index.duplicated()]))
            old_data[newname] = data[newname]

while True:

    frame = vs.read()
    frame = frame[1]
    if frame is None: break
    frame = imutils.resize(frame, width=1200)
    (H, W) = frame.shape[:2]
    timestamps.append(vs.get(cv2.CAP_PROP_POS_MSEC))

    if old_data_bool: frame = updateOldCircles(frame,vs.get(cv2.CAP_PROP_POS_FRAMES))

    updateTrackers(frame)
    frame = updateCircles(frame)
    
    
    updateData()

    out.write(frame)

    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("s"): addTracker(frame)
        
    elif key == ord("e"): break

#save csv
if old_data_bool: 
    mergedata()   
    old_data.to_csv("tracking_data.csv")
else:
    data.to_csv("tracking_data.csv")

vs.release()
out.release()

cv2.destroyAllWindows()