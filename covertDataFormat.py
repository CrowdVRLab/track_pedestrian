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

    # plt.figure(1)
    # times = range(measurements.shape[0])
    # plt.plot(measurements[:, 0], measurements[:, 1], 'bo',
    #         smoothed_state_means[:, 0], smoothed_state_means[:, 2], 'b--',)
    # plt.show()

    return (smoothed_state_means[:, 0].tolist(),smoothed_state_means[:, 2].tolist())

def resample(series, currenttime, targettime):
    
    resampledseries = [] 

    for time in targettime:
        
        # find closeset and second closest sample in time

        values = [ abs(item-time) for item in currenttime]

        closestindex = values.index(min(values))
        
        if(closestindex>0): secondclosestindex = values.index(min([values[closestindex+1], values[closestindex-1]]))
        else: secondclosestindex = values.index(values[closestindex+1])


        closesttimevalue = currenttime[closestindex]

        secondclosesttimevalue = currenttime[secondclosestindex]

        closestspacevalue = series[closestindex]

        secondclosestspacevalue = series[secondclosestindex]


        # remapping between time doamin and space domain 

        old_min = min([closesttimevalue,secondclosesttimevalue])

        old_max = max([closesttimevalue,secondclosesttimevalue])

        old_value = time

        new_max = max([closestspacevalue,secondclosestspacevalue])

        new_min = min([closestspacevalue,secondclosestspacevalue])

        new_value = ( (old_value - old_min) / (old_max - old_min) ) * (new_max - new_min) + new_min
        
        resampledseries.append(new_value);
    

    return resampledseries

for cname in old_data.columns:
        if not 'Unnamed' in cname and  not 'timestamp' in cname and not 'index' in cname:
           
            startIndex=0
            for item in old_data[cname]:                 
                if type(item) is str:
                    break
                startIndex+=1

            series = [ [ int(i) for i in item.replace('(','').replace(')','').split(',')] for item in old_data[cname] if type(item) is str]           

            deltatimeNanoSeconds = int(deltatimeMilliSeconds * 1000000)
            targetdeltatimeNanoSeconds = int(1000000000/72) #(1s/72) in nanoseconds = 13,888,888 N

            #generate timestamps
            endindex = len(series) + startIndex
            indexArray = range( startIndex , endindex )  
            currenttimeArray = [ i*deltatimeNanoSeconds for i in indexArray]

            endindex = int(int(currenttimeArray[-1]-currenttimeArray[0])/targetdeltatimeNanoSeconds)
            targetindexArray = range( startIndex , endindex )  
            targettimeArray = [ i*targetdeltatimeNanoSeconds for i in targetindexArray]
            targettimeArrayinsec = [ i/1000000000 for i in targettimeArray]

            #extract the x and y series 
            x = [ item[0] for item in series ]
            y = [ item[1] for item in series ]

            #kalman filtered values 
            kalman_x,kalman_y = kalman(x,y)

            #resampled
            resampled_x = resample(kalman_x,currenttimeArray,targettimeArray)
            resampled_y = resample(kalman_y,currenttimeArray,targettimeArray)

            #sizing all columns accordingly
            dir_x = [0] * len(resampled_x)
            dir_y = [0] * len(resampled_x)
            id = [int(cname)]*len(resampled_x)
            gid = id 
            
           
            new_d= {'id':id,'gid':gid,'x':resampled_x,'y':resampled_y,'dir_x':dir_x,'dir_y':dir_y,'radius':dir_y,'time':targettimeArrayinsec}
            new_user = pd.DataFrame(data=new_d)
            
            new_data = new_data.append(new_user) 

new_data.to_csv("video1/tracking_data_per_user_resampled.csv")