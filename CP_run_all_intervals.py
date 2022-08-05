# -*- coding: utf-8 -*-
"""
Created on Thu Aug  4 15:17:05 2022

@author: iainh



Script which runs all intervals for a Dataset to optimise it
Will simply optimise each interval using its outputs to feed into the 
next interval





"""



import math
import pandas as pd
from ortools.sat.python import cp_model
from Solver.CPModel_SC import CPModel_SC_data 
from Solver.HintFunctions import CreateManHint, AddHint
from utils import readwrite

'''
ideintification of intervals and initial values
'''

full_horizon = 7200
interval_size = 1440
b = 0
c = interval_size
hint = 0
switchtime =0
dt = 60
num_interval = math.ceil(full_horizon/interval_size)

# used to define how long it takes to process each dataset
FLOP_to_proc = 1000
FLOPS_available = 100 # giga flops

obs_dataset_mem = int( 150e3/100 )# in 0.1 kB   
obs_rate = 100                    # used to allow the observations to be processed in parts while remaining integers

pro_rate = math.ceil(FLOP_to_proc/FLOPS_available)  # rate at which the system can process a dataset
pro_dataset_mem = int(300 /100)  # in 0.1 kB

down_rate_mem = 320  # in 0.1 kB per second
down_rate = int(down_rate_mem/pro_dataset_mem)  # the number of processed dataset units the satellite can downlink per second
down_dataset_mem = int(down_rate_mem/down_rate)
memory_storage = int( 64e7) # 64GB total memory in 0.1kB

all_action = range(4)
all_sats = range(66)
all_shifts = range(full_horizon)
all_interval = range(num_interval)
all_mod_shifts = range(interval_size)

memory= 0
num_obs = 0
num_pro= 0
num_down= 0


#making the dataframe to output the schedule
#schedtemp = [[] for a in range(9)]

schedule_out_titles = ['Observing', 'Processing', 'downlinking', 'idling', 'num observed', 'num processed', 'num downlinked', 'memory used (kB)', 'Satellite targeted']







for interval in all_interval:
    
    interval_size_CP_model = c-b
    interval_shifts=range(b,c)
    all_mod_shifts = range(c-b)
    
    '''
    File read in 
    '''
    
    #read in if a illuminator is in view 
    data = pd.read_csv("Data/60s, 5d, polar/Illuminator view data log.csv")
    temp = data.values.tolist()
    any_ilum_list = temp[b:c] 
    #read in the downlink data times
    data = pd.read_csv("Data/60s, 5d, polar/Communications Data log.csv")
    temp= data.values.tolist() 
    datals = temp[b:c]
    
    # chages downlink from list of lists to 1D list
    gnd_stat_list = [datals[i][0] for i in range(0, len(datals))]
    
    #  reads in which illuminators are visible
    data = pd.read_csv("Data/60s, 5d, polar/Avg objects Detection log.csv")
    temp = data.values.tolist()
    ilum_value_list = temp[b:c]
    
    for s in all_mod_shifts:
        for sat in all_sats:
            ilum_value_list[s][sat] = math.floor(ilum_value_list[s][sat]*10000)
    
    '''
    create model
    '''
    
    
    (model, shifts, target_ilum, num_obs, num_pro, num_down, memory, Log) = CPModel_SC_data(any_ilum_list,gnd_stat_list, interval_size_CP_model,b, obs_dataset_mem, obs_rate, pro_dataset_mem,
                    pro_rate, down_rate,down_dataset_mem, memory, memory_storage, num_obs, num_pro, num_down,dt, ilum_value_list,switchtime)
    print("CP Model made for interval %i to %i" % (b,c))

    '''
    run model
    '''
    
    solver = cp_model.CpSolver()  

    solver.parameters.max_time_in_seconds =600
    solver.parameters.log_search_progress = True
    solver.parameters.num_search_workers = 4
    
    status = solver.Solve(model)
    
    
    if status == cp_model.OPTIMAL :
        print('Solution: optimal found for interval %i to %i' % (b,c))
        print(f'Objective value achieved = {solver.ObjectiveValue()} ')
        print('\nStatistics')
        print('  - conflicts      : %i' % solver.NumConflicts())
        print('  - branches       : %i' % solver.NumBranches())
        print('  - wall time      : %f s' % solver.WallTime())
    
    
    elif status == cp_model.FEASIBLE:
        print('Solution: feasible found for interval %i to %i' % (b,c))
        print(f'Objective value achieved = {solver.ObjectiveValue()} ')
        print('\nStatistics')
        print('  - conflicts      : %i' % solver.NumConflicts())
        print('  - branches       : %i' % solver.NumBranches())
        print('  - wall time      : %f s' % solver.WallTime())
  
    
    else:
        print('Solution: no feasible solution found for %i to %i' % (b,c))
    
    
    
    memory= solver.Value(memory)
    num_obs = solver.Value(num_obs)
    num_pro= solver.Value(num_pro)
    num_down= solver.Value(num_down)
    
    
    '''
    write values out to files
    '''
    scheduleWrite = [[0  for a in range(9)] for s in all_mod_shifts]
    target_ilum_val_inv = [[0  for sat in all_sats] for s in all_mod_shifts] 
    for s in all_mod_shifts:
        for a in all_action:
            if solver.Value(shifts[(a,s)]) == 1:
              
                scheduleWrite[s][a] = 1
            for i in range(4):
                multi =1
                if i ==3:
                    multi = 0.1
                
                scheduleWrite[s][i+4] = multi*solver.Value(Log[i][s])
            
    for sat in all_sats:
        if solver.Value(target_ilum[(sat,s)]) == 1:
            scheduleWrite[s][8] = sat
            target_ilum_val_inv[s][sat] = 1
    ind = [i for i in range(b,c)]
    
    if b == 0:
        
        scheduleout= pd.DataFrame(scheduleWrite,index = ind, columns=schedule_out_titles)
        
    else:
        dftemp = pd.DataFrame(scheduleWrite,index = ind, columns=schedule_out_titles)
        scheduleout= scheduleout.append(dftemp)
        
    
    name = "scheduleraw_up_to_shift %i" % (c)    
    readwrite.df_to_xlsxOut(scheduleout,schedule_out_titles, name, "./results/many_interval_test/")
    b += interval_size
    c = b+interval_size
    print("\n")
        