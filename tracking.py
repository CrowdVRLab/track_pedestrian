# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import pandas as pd
import numpy as np
import argparse
import imutils
import time
import cv2

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--path", type=str, default="video4",
	help="Path to input video file")
ap.add_argument("-t", "--tracker", type=str, default="csrt",
	help="OpenCV object tracker type csrt,kcf,boosting,mil,tld,medianflow,mosse check opencv documentation ")
ap.add_argument("-s", "--showID", type=bool, default=False,
	help="Show the ID of the tracked objects loaded from tracking_data.csv")
ap.add_argument("-sP", "--showPreviousData", type=bool, default=True,
	help="Only play old data")
ap.add_argument("-pM", "--playMode", type=bool, default=False,
	help="Only play old data")
args = vars(ap.parse_args())

#standard names 
trackingDataNameAndLocation = args["path"]+"/"+"tracking_data.csv" 
sourceVideoNameAndLocation = args["path"]+"/"+"video.mp4" 
outputVideoNameAndLocation = args["path"]+"/"+'output.avi'

#loading source video
vs = cv2.VideoCapture(sourceVideoNameAndLocation)
fps = None
fps = vs.get(cv2.CAP_PROP_FPS)
data = None 
frame = vs.read()
frame = frame[1]
frame = imutils.resize(frame, width=1200)
(H, W) = frame.shape[:2]

# Define the codec and create VideoWriter object for output video
out = cv2.VideoWriter(outputVideoNameAndLocation,cv2.VideoWriter_fourcc('M','J','P','G'), fps, (W,H))
old_data_bool=False

#variables
tracker = []
initBB = []
initBBOld =[]
timestamps=[]
#tracker types "csrt","kcf","boosting","mil","tld","medianflow","mosse" check opencv documentation 
trackerType = args["tracker"]
showNumber = args["showID"]

#attempting to load prexisting tracking data 
try: 
    old_data = pd.read_csv(trackingDataNameAndLocation)
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

    tracker.append(OPENCV_OBJECT_TRACKERS[trackerType]())
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

def deleteTracker():

    if len(tracker) == 1 or not args["playMode"]:
        initBB.pop(0)
        tracker.pop(0)     
        addTracker(frame)

def updateTrackers(frame):

    if len(tracker) >0 or args["playMode"]:
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
                if centerX<5 or centerY<5 or centerX>W-5 or centerY>H-5:
                    print("remove -> "+str(i))
                    tracker[i] = None
                    initBB[i] = None                 
            else:
                #remove unsucesfull
                print(str(i) + " was unsucesfull")
                print("remove -> "+str(i))
                initBB.pop(i)
                tracker.pop(i)
                #add new tracker
                addTracker(frame)
        i+=1

    else:
        addTracker(frame)

def updateCircles(frame):

    #this highlight the currently tracked data 

    if len(initBB) >0:
        i=0
        for box in initBB:
            if box == None: 
                pass
            else:
                (x, y, w, h) = [int(v) for v in box]
                centerX = int(x+w/2)
                centerY = int(y+h/2)               
                cv2.circle(frame, (centerX,centerY), 10,(0, 0, 250), 2)
            i+=1
    
    return frame

def updateOldCircles(frame,framenumber):

    #this highlight the data that has already been tracked  

    if(args['showPreviousData']):
        for cname in old_data.columns:
            if not 'Unnamed' in cname and  not 'timestamp' in cname and not 'index' in cname:
                if old_data.shape[0]>framenumber:
                    if isinstance(old_data.at[int(framenumber),cname], str):
                        tupledata = tuple(map(int, old_data.at[framenumber,cname].replace('(', '').replace(')', '').split(', ') ))
                        centerX= tupledata[0]
                        centerY= tupledata[1]
                        cv2.circle(frame, (centerX,centerY), 1,(0, 255, 0), 2)
                        if(showNumber): cv2.putText(frame, cname, (centerX,centerY),cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)
         
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
    
    elif key == ord("d"): deleteTracker()

    elif key == ord("e"): break

#save csv
if old_data_bool: 
    mergedata()   
    old_data.to_csv(trackingDataNameAndLocation)
else:
    data.to_csv(trackingDataNameAndLocation)

#release the videos
vs.release()
out.release()

#destroy all windows
cv2.destroyAllWindows()