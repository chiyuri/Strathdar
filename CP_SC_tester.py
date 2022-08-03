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
from Solver.HintFunctions import CreateManHint, AddHint
from utils import plotFunctions as pf
from utils import postProcessing as post
from utils import readwrite
  
#read in if a illuminator is in view 
data = pd.read_csv("Data/60s, 5d, polar/Illuminator view data log.csv")
any_ilum_list = data.values.tolist()

#read in the downlink data times
data = pd.read_csv("Data/60s, 5d, polar/Communications Data log.csv")
datals= data.values.tolist() 

#  reads in which illuminators are visible
data = pd.read_csv("Data/60s, 5d, polar/Avg objects Detection log.csv")
ilum_value_list = data.values.tolist()

# chages downlink from list of lists to 1D list
gnd_stat_list = [datals[i][0] for i in range(0, len(datals))]


# used to define how long it takes to process each dataset
FLOP_to_proc = 1000
FLOPS_available = 100 # giga flops


hint = 0
interval = 300 # length of interval to be optimised
start_shift=0

obs_dataset_mem = int( 150e3/100 )# in 0.1 kB   
obs_rate = 100                    # used to allow the observations to be processed in parts while remaining integers



pro_rate = math.ceil(FLOP_to_proc/FLOPS_available)  # rate at which the system can process a dataset
pro_dataset_mem = int(300 /100)  # in 0.1 kB

 
down_rate_mem = 320  # in 0.1 kB per second
down_rate = int(down_rate_mem/pro_dataset_mem)  # the number of processed dataset units the satellite can downlink per second
down_dataset_mem = int(down_rate_mem/down_rate)

memory_init = 0
num_obs_init = 0
num_pro_init=0
num_down_init = 0
memory_storage = int( 64e7) # 64GB total memory in 0.1kB
num_obs_init = 0
all_T = range(interval)
all_action = range(4)
all_sats = range(66)
dt = 60
time = [dt*t for t in all_T]

for t in all_T:
    for s in all_sats:
        ilum_value_list[t][s] = int(ilum_value_list[t][s]*10000)

'''
Creating Hint
'''
if hint == 1:
    #add code to make hint
    (hint_shifts, hint_target_ilum) = CreateManHint(any_ilum_list,ilum_value_list, gnd_stat_list, all_action,all_T, all_sats, obs_dataset_mem, obs_rate, pro_dataset_mem,
                                                        pro_rate, down_rate, memory_init, memory_storage, num_obs_init,num_pro_init, dt)
'''
creating cp model
'''

(model, shifts, target_ilum, num_obs, num_pro, num_down, memory, Log) = CPModel_SC_data(any_ilum_list,gnd_stat_list, interval,start_shift, obs_dataset_mem, obs_rate, pro_dataset_mem,
                    pro_rate, down_rate,down_dataset_mem, memory_init, memory_storage, num_obs_init, num_pro_init, num_down_init,dt, ilum_value_list)

print("CP Model made")

if hint ==1:
    (model, shifts, target_ilum) = AddHint(model, shifts, target_ilum, hint_shifts, hint_target_ilum, all_T, all_action, all_sats)


'''
solving the CP model
'''

solver = cp_model.CpSolver()  

solver.parameters.max_time_in_seconds =2400
solver.parameters.log_search_progress = True
solver.parameters.num_search_workers = 8

status = solver.Solve(model)
if status == cp_model.OPTIMAL :
    print('Solution: optimal found')
    print('\nStatistics')
    print('  - conflicts      : %i' % solver.NumConflicts())
    print('  - branches       : %i' % solver.NumBranches())
    print('  - wall time      : %f s' % solver.WallTime())
    
    
elif status == cp_model.FEASIBLE:
    print('Solution: feasible found')
    print('\nStatistics')
    print('  - conflicts      : %i' % solver.NumConflicts())
    print('  - branches       : %i' % solver.NumBranches())
    print('  - wall time      : %f s' % solver.WallTime())
  
    
else:
    print('Solution: no feasible solution found')



'''
post processing
'''
    
# Creates pd dataframe to then be used to make gantt chart
titles = ['Observing', 'Processing', 'downlinking', 'idling', 'num observed', 'num processed', 'num downlinked', 'memory used (kB)']
data = []
actionABS = []
scheduleWrite = [[0  for a in range(8)] for s in all_T]
schedule = [[0  for s in all_T] for a in all_action]
target_ilum_val = [[0 for s in all_T] for sat in all_sats]
for s in all_T:
    for a in all_action:
        if solver.Value(shifts[(a,s)]) == 1:
            actionABS.append(titles[a])
            scheduleWrite[s][a] = 1
            schedule[a][s] = 1
        for i in range(4):
            multi =1
            if i ==3:
                multi = 0.1
                
            scheduleWrite[s][i+4] = multi*solver.Value(Log[i][s])
            
    for sat in all_sats:
        if solver.Value(target_ilum[(sat,s)]) == 1:
            target_ilum_val[sat][s] = 1
    
    tempDict = dict(start = s*dt, duration = dt, end = (s+1)*dt, action = actionABS[s])
    data.append(tempDict)
    
df = pd.DataFrame(data)


readwrite.xlsxOut(scheduleWrite,titles, "scheduleraw.xlsx", "./results/")


pf.ganttChart(df,titles)


(memoryLogs, num_logs) = post.memoryLogAssem(schedule, obs_dataset_mem, pro_dataset_mem, obs_rate, pro_rate, down_rate,dt)
pf.memoryGraph(memoryLogs,time)


pf.ObsValueGraph(ilum_value_list,target_ilum_val, schedule, time, all_T, all_sats)






