import pandas as pd
import numpy as np
import math

old_data = pd.read_csv("video2/tracking_data.csv")

d = {'id':[],'gid':[],'x':[],'y':[],'dir_x':[],'dir_y':[],'radius':[],'time':[]}

new_data = pd.DataFrame(data=d)

for cname in old_data.columns:
        if not 'Unnamed' in cname and  not 'timestamp' in cname and not 'index' in cname:
           
            i=0
            for item in old_data[cname]:                 
                if type(item) is str:
                    break
                i+=1

            series = [ [ int(i) for i in item.replace('(','').replace(')','').split(',')] for item in old_data[cname] if type(item) is str]

            index = range(i,len(series)+i)           
            id = [int(cname)]*len(series)
            gid = id 
           
            x = [ item[0] for item in series ]
            y = [ item[1] for item in series ]
            
            dir_x = [0] * len(series)
            dir_y = [0] * len(series)
            time = [ i*40 for i in index]

            new_d= {'id':id,'gid':gid,'x':x,'y':y,'dir_x':dir_x,'dir_y':dir_y,'radius':dir_y,'time':time}
            new_user = pd.DataFrame(data=new_d)
            
            new_data = new_data.append(new_user) 

new_data.to_csv("video2/tracking_data_per_user.csv")