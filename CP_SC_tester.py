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
# chages downlink from list of lists to 1D list
gnd_stat_list = [datals[i][0] for i in range(0, len(datals))]



FLOP_to_proc = 920
FLOPS_available = 92 # giga flops

interval = 300
start_shift=0

obs_dataset_mem = 1500
obs_size = 100 
obs_mem_size = math.ceil(obs_dataset_mem/obs_size)  ## need to add code to check error from rounding

pro_size = math.ceil(FLOP_to_proc/FLOPS_available)
pro_dataset_mem = 30
pro_mem_size = math.ceil(pro_dataset_mem/pro_size)

down_rate = 32  # in KB per second

memory_init = 0
memory_storage = int( 64e6) # 64GB total memory
num_obs_init = 0
all_T = range(interval)
all_action = range(4)
dt = 30
time = [dt*t for t in all_T]

(model, shifts, num_obs, num_pro, num_down, memory) = CPModel_SC_data(any_ilum_list,gnd_stat_list, interval,start_shift, obs_mem_size, obs_size, pro_mem_size,
                    pro_size, down_rate, memory_init, memory_storage, num_obs_init)

print("CP Model made")
solver = cp_model.CpSolver()  

solver.parameters.max_time_in_seconds =1000
solver.parameters.log_search_progress = True
solver.parameters.num_search_workers = 4

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
for s in all_T:
    for a in all_action:
        if solver.Value(shifts[(a,s)]) == 1:
            actionABS.append(titles[a])
            schedule[a][s] = 1
    
    
    tempDict = dict(start = s*dt, duration = dt, end = (s+1)*dt, action = actionABS[s])
    data.append(tempDict)
df = pd.DataFrame(data)

pf.ganttChart(df,titles)


(memoryLogs, num_logs) = post.memoryLogAssem(schedule, obs_mem_size, pro_mem_size, obs_size, pro_size, down_rate)

pf.memoryGraph(memoryLogs,time)






