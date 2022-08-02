# -*- coding: utf-8 -*-
"""
Created on Thu Jul 28 14:18:06 2022

@author: iainh
"""

# CP model tester, not for long term use

import math
import pandas as pd
from ortools.sat.python import cp_model
from Solver.CPModel_SC import CPModel_SC_data
from utils import plotFunctions as pf
from utils import postProcessing as post

data = pd.read_csv("Data/30s, 1d, polar/Illuminator view data log.csv")
any_ilum_list = data.values.tolist()

#read in the downlink data times
data = pd.read_csv("Data/30s, 1d, polar/Communications Data log.csv")
datals= data.values.tolist() 

data = pd.read_csv("Data/30s, 1d, polar/Avg objects Detection log.csv")
ilum_value_list = data.values.tolist()

# chages downlink from list of lists to 1D list
gnd_stat_list = [datals[i][0] for i in range(0, len(datals))]



FLOP_to_proc = 920
FLOPS_available = 92 # giga flops

interval = 80
start_shift=0

obs_dataset_mem = int( 15e9/100 )# in 0.1 kB
obs_rate = 100


pro_rate = math.ceil(FLOP_to_proc/FLOPS_available)
pro_dataset_mem = int(300 /100)  # in 0.1 kB

 
down_rate_mem = 320  # in 0.1 kB per second
down_rate = int(down_rate_mem/pro_dataset_mem)


memory_init = 0
memory_storage = int( 64e9) # 64GB total memory in 0.1kB
num_obs_init = 0
all_T = range(interval)
all_action = range(4)
all_sats = range(66)
dt = 30
time = [dt*t for t in all_T]

for t in all_T:
    for s in all_sats:
        ilum_value_list[t][s] = int(ilum_value_list[t][s]*10000)



(model, shifts, target_ilum, num_obs, num_pro, num_down, memory) = CPModel_SC_data(any_ilum_list,gnd_stat_list, interval,start_shift, obs_dataset_mem, obs_rate, pro_dataset_mem,
                    pro_rate, down_rate, memory_init, memory_storage, num_obs_init,dt, ilum_value_list)

print("CP Model made")
solver = cp_model.CpSolver()  

solver.parameters.max_time_in_seconds =300
solver.parameters.log_search_progress = True
solver.parameters.num_search_workers = 8

status = solver.Solve(model)
if status == cp_model.OPTIMAL :
    print('Solution: optimal found')

elif status == cp_model.FEASIBLE:
    print('Solution: feasible found')
else:
    print('Solution: no feasible solution found')


'''
post processing
'''
    
# Creates pd dataframe to then be used to make gantt chart
titles = ['Observing', 'Processing', 'downlinking', 'idling']
data = []
actionABS = []
schedule = [[0 for s in all_T] for a in all_action]
target_ilum_val = [[0 for s in all_T] for sat in all_sats]
for s in all_T:
    for a in all_action:
        if solver.Value(shifts[(a,s)]) == 1:
            actionABS.append(titles[a])
            schedule[a][s] = 1
    for sat in all_sats:
        if solver.Value(target_ilum[(sat,s)]) == 1:
            target_ilum_val[sat][s] = 1
    
    tempDict = dict(start = s*dt, duration = dt, end = (s+1)*dt, action = actionABS[s])
    data.append(tempDict)
df = pd.DataFrame(data)

pf.ganttChart(df,titles)


(memoryLogs, num_logs) = post.memoryLogAssem(schedule, obs_dataset_mem, pro_dataset_mem, obs_rate, pro_rate, down_rate)

pf.memoryGraph(memoryLogs,time)


pf.ObsValueGraph(ilum_value_list,target_ilum_val, schedule, time, all_T, all_sats)






