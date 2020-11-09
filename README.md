# Pedestrain tracking OpenCV

These scripts allows multiple objects tracking on a aerial video across multiple sessions using opencv trackers\

The first script "tracking.py" allows a user to define a tracking object, once the video is completed the tracked object path (x,y) is saved on a tracking_data.csv file; in the following session the tracking_data is loaded and visualized\

![alt text](https://github.com/sbanca/track_pedestrian/blob/main/images/pedestrian_tracking.gif?raw=true)

A second script "postProcess.py" allow for noise removal and resampling of the pedestrian trajectories
Noise removal is performed via Kalman Filter (pykalman) and is sucesfull in removing head oscillating noise from the trajectory
Ultimately the script also allows for resampling (up/down) to your desired framerate

Kalman Filter\
![alt text](https://github.com/sbanca/track_pedestrian/blob/main/images/kalman_filter.PNG?raw=true)

Resampling\
![alt text](https://github.com/sbanca/track_pedestrian/blob/main/images/resampling.PNG?raw=true)

## Tracking.py

This script has 4 arguments\ 
__--path__: str the path folder where the video.mp4 is saved\
__--tracker__: str object tracker type csrt,kcf,boosting,mil,tld,medianflow,mosse check opencv documentation\
__--showID__: bool Show the ID of the tracked objects loaded from tracking_data.csv\
__--playMode__: bool in this mode the script plays without the need of defining an ID\

for example:\

```
python tracking.py --path video3 --tracker csrt
```
Once the script is launched you will be prompt to define a tracking area with the mouse, once the area has been defined you can press enter, subsequently you can define another area/tracker. Once you defined a number of racker you are happy with you can press [Q] for the video to start and the tracker to start tracking.
If a pedestrian enters the video area you can press [S] to define a new tracker.
If you experienced a wronlgy tracked pedestrian during a session you can open tracking_data.csv and remove the column with the pedestrian id.

