#this files convert the data format and resample to 72fps
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import math
from pykalman import KalmanFilter

old_data = pd.read_csv("video1/tracking_data.csv")

d = {'id':[],'gid':[],'x':[],'y':[],'dir_x':[],'dir_y':[],'radius':[],'time':[]}

new_data = pd.DataFrame(data=d)

timestamps = [ item for item in old_data["timestamp"] ]

deltaTimestamp = [ timestamps[i] - timestamps[i-1] for i in range(0, len(timestamps), 1) if i > 0 ]

deltatimeMilliSeconds = np.mean(np.array(deltaTimestamp)) 

def kalman(x,y):

    measurements = np.column_stack((x, y))

    initial_state_mean = [measurements[0, 0],0,measurements[0, 1],0]

    transition_matrix = [[1, 1, 0, 0],
                        [0, 1, 0, 0],
                        [0, 0, 1, 1],
                        [0, 0, 0, 1]]

    observation_matrix = [[1, 0, 0, 0],[0, 0, 1, 0]]

    kf1 = KalmanFilter(transition_matrices = transition_matrix,
                    observation_matrices = observation_matrix,
                    initial_state_mean = initial_state_mean)

    kf1 = kf1.em(measurements, n_iter=5)
    (smoothed_state_means, smoothed_state_covariances) = kf1.smooth(measurements)

    kf2 = KalmanFilter(transition_matrices = transition_matrix,
                  observation_matrices = observation_matrix,
                  initial_state_mean = initial_state_mean,
                  observation_covariance = 10000000*kf1.observation_covariance,
                  em_vars=['transition_covariance', 'initial_state_covariance'])

    kf2 = kf2.em(measurements, n_iter=5)
    (smoothed_state_means, smoothed_state_covariances)  = kf2.smooth(measurements)

    # plt.figure(1)
    # times = range(measurements.shape[0])
    # plt.plot(measurements[:, 0], measurements[:, 1], 'bo',
    #         smoothed_state_means[:, 0], smoothed_state_means[:, 2], 'b--',)
    # plt.show()

    return (smoothed_state_means[:, 0].tolist(),smoothed_state_means[:, 2].tolist())

def resample(series_x,series_y, currenttime, targettime):
    
    resampledseries_x = [] 
    resampledseries_y = [] 

    resampledseries_x.append(series_x[0])
    resampledseries_y.append(series_y[0])

    for time in targettime[1:]:
        
        # find closeset and second closest sample in time

        values = [ abs(item-time) for item in currenttime]

        closestindex = values.index(min(values))
        
        if(closestindex>0): secondclosestindex = values.index(min([values[closestindex+1], values[closestindex-1]]))
        else: secondclosestindex = values.index(values[closestindex+1])


        minindex = min([closestindex,secondclosestindex])

        maxindex = max([closestindex,secondclosestindex])

        
        mintimevalue = currenttime[minindex]

        maxtimevalue = currenttime[maxindex]

        # remapping between time doamin and space domain 

        resampledseries_x.append(remap (time,mintimevalue,maxtimevalue,series_x[maxindex],series_x[minindex]))
        resampledseries_y.append(remap (time,mintimevalue,maxtimevalue,series_y[maxindex],series_y[minindex]))

    # measurements =  np.column_stack((resampledseries_x, resampledseries_y))
    # origmeasurements =  np.column_stack((series_x, [i+10 for i in series_y]))
    # plt.figure(1)
    # for i in range(0,len(resampledseries_x)):
    #     plt.text(resampledseries_x[i], resampledseries_y[i], str(i), bbox=dict(facecolor='red', alpha=0.5))
    # plt.plot(measurements[:, 0], measurements[:, 1], 'bo', measurements[:, 0], measurements[:, 1], 'b--',)
    # plt.plot(origmeasurements[:, 0], origmeasurements[:, 1], 'ro', origmeasurements[:, 0], origmeasurements[:, 1], 'r--',)
    # plt.show()

    return resampledseries_x,resampledseries_y


def remap (old_value,old_min,old_max,new_max,new_min):

    new_value = ( (old_value - old_min) / (old_max - old_min) ) * (new_max - new_min) + new_min

    return new_value
        

for cname in old_data.columns:
        if not 'Unnamed' in cname and  not 'timestamp' in cname and not 'index' in cname:
           
            startIndex=0
            for item in old_data[cname]:                 
                if type(item) is str:
                    break
                startIndex+=1

            print("processing ---> " + cname)

            series = [ [ int(i) for i in item.replace('(','').replace(')','').split(',')] for item in old_data[cname] if type(item) is str]           

            deltatimeNanoSeconds = int(deltatimeMilliSeconds * 1000000)
            targetdeltatimeNanoSeconds = 13900000

            
            #generate timestamps
            endindex = len(series) + startIndex
            indexArray = range( startIndex , endindex )  
            currenttimeArray = [ i*deltatimeNanoSeconds for i in indexArray]

            deltaindex = int(int(currenttimeArray[-1]-currenttimeArray[0])/targetdeltatimeNanoSeconds)
            targetindexArray = range( 0 , deltaindex )  
            targettimeArray = [ i*targetdeltatimeNanoSeconds+currenttimeArray[0] for i in targetindexArray]
            
            

            #extract the x and y series 
            x = [ item[0] for item in series ]
            y = [ item[1] for item in series ]

            #kalman filtered values 
            kalman_x,kalman_y = kalman(x,y)

            #resampled
            resampled_x,resampled_y = resample(kalman_x,kalman_y,currenttimeArray,targettimeArray)
            
            #sizing all columns accordingly
            dir_x = [0] * len(resampled_x)
            dir_y = [0] * len(resampled_x)
            id = [int(cname)]*len(resampled_x)
            gid = id 
            
            print(len(resampled_x))
            
            targettimeArrayinsec = [ i/1000000000 for i in targettimeArray]

            new_d= {'id':id,'gid':gid,'x':resampled_x,'y':resampled_y,'dir_x':dir_x,'dir_y':dir_y,'radius':dir_y,'time':targettimeArrayinsec}
            new_user = pd.DataFrame(data=new_d)
            
            new_data = new_data.append(new_user) 

            print(len(new_data))

new_data.to_csv("video1/tracking_data_per_user_resampled.csv")