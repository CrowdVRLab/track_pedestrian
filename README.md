# Pedestrain tracking OpenCV

This script allows multiple objects tracking on a aerial video across multiple sessions\

The software allows a user to define a tracking object, once the video is completed the tracked object path (x,y) is saved on a tracking_data.csv file; in the following session the tracking_data is loaded and visualized\

![alt text](https://github.com/sbanca/track_pedestrian/blob/main/pedestrian_tracking.gif?raw=true)

A second scripts allow for noise removal and resampling of the trajectories
Noise removal is performed via Kalman Filter (pykalman) and is sucesfull in removing head oscillating noise from the trajectory
Ultimately the script also allows for resampling (up/down) to your desired framerate


