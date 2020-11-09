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
