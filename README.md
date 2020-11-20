# Pedestrain tracking OpenCV

These scripts allows multiple objects tracking on a aerial video across multiple sessions using opencv trackers\

The first script "tracking.py" allows a user to define a tracking object, once the video is completed the tracked object path (x,y) is saved on a tracking_data.csv file; in the following session the tracking_data is loaded and visualized\

![](https://github.com/sbanca/track_pedestrian/blob/main/images/pedestrian_tracking.gif?raw=true) 

A second script "postProcess.py" allow for noise removal and resampling of the pedestrian trajectories
Noise removal is performed via Kalman Filter (pykalman) and is sucesfull in removing head oscillating noise from the trajectory
Ultimately the script also allows for resampling (up/down) to your desired framerate

Kalman Filter\
![](https://github.com/sbanca/track_pedestrian/blob/main/images/kalman_filter.PNG?raw=true)

Resampling\
![](https://github.com/sbanca/track_pedestrian/blob/main/images/resampling.PNG?raw=true)

## tracking.py

This script has 4 arguments

__--path__: str the path folder where the video.mp4 is saved\
__--tracker__: str object tracker type csrt,kcf,boosting,mil,tld,medianflow,mosse check opencv documentation\
__--showID__: bool Show the ID of the tracked objects loaded from tracking_data.csv\
__--playMode__: bool in this mode the script plays without the need of defining an ID\

for example:

```
python tracking.py --path video3 --tracker csrt
```
Once the script is launched a user will be prompt to define a tracking area with the mouse, once the area has been defined you can press enter, subsequently you can define another area/tracker. Once the user defined a number of tracker he is happy with , he can press [Q] for the video to start and the tracker to start tracking.
If a pedestrian enters the video area at a later frame than the first the user can press [S] to stop the video and define a new tracker.
If the user experience tracking error during a session he can open __tracking_data.csv__ and remove the column with the pedestrian id. Further different types of trackers  (csrt,kcf,boosting,mil,tld,medianflow,mosse) or different trakers areas can be tested in order to improve results.  
The folder defined in the __path__ argument (in the previous example video3) should contain a video.mp4 (the video with the pedestrians you wish to record),
if tracking is launched for a video that does not have a tracking_data.csv a tracking_data.csv will be saved within the __path__ once the video has completed a full play/track loop. 


### tracking_data.csv

index |  timestamp | pedestrian 1 | pedestrian n
------------ | ------------- |------------- |-------------
(int) | (float) | (float,float)| (float,float)

## postProcess.py

This script has 6 arguments

__--path__: str the path folder where the video.mp4 is saved\
__--kalman__: bool Apply Kalman filter\
__--resampling__: bool Resample the tracked data to a specific framerate\
__--mirrorX__: bool mirror X data\
__--mirrorY"__: bool mirror Y data\
__--plotResults__: bool plot the results of kalman filtering and resampling for each of the tracks 

for example:

```
python postProcess.py --path video3 
```
Once the script is launched it will load the dataset from tracking_data.csv and transform it into the following format 

### tracking_data_per_user.csv

id |  guid | x | y | dir_x | dir_y | radius | time | 
-- | ----- | - | - | ----- | ----- | ------ | ---- |
(int) | (int) | (float) | (float)  | (float)  | (float)  | (float)| (float)| 


### Dependencies

imutils               0.5.3
matplotlib            3.3.2
numpy                 1.19.2
opencv-contrib-python 4.4.0.44
opencv-python         4.4.0.44
pandas                1.1.3
pykalman              0.9.5
scipy                 1.5.4
