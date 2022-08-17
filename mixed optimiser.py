# -*- coding: utf-8 -*-
"""
Created on Wed Aug 10 13:42:56 2022

@author: iainh


Wierd script to try and optimise over long time range then solwly optimise over smaller time scales


"""

import math
import pandas as pd
import datetime
import os
from ortools.sat.python import cp_model
from Solver.CPModel_SC import CPModel_SC_data , CPModel_SC_data_endpoint_constraints
from Solver.HintFunctions import CreateManHint, AddHint
from utils import plotFunctions as pf
from utils import postProcessing as post
from utils import readwrite
  



affix = "pol/10s_15d/G40/"
current_time = datetime.datetime.now()
month =  str(current_time.month)
day = str(current_time.day)
hour = str(current_time.hour)
minute = str(current_time.minute)
time_now = "_M" + month + "_D" +day +"_H" + hour + "_min" + minute
path = "./results/" + affix + "iainLaptop"
path = path +time_now
os.mkdir(path)
path = path+ "/"


# initialisation stuff

hint = 1
switchtime =4
affix = "pol/1s_5d/G40/"
interval_time_length = 86400# interval in seconds to be optimised
switching_constraint = 60 # switching constraint in seconds

dt = [60, 30, 15]
interval_true_length = [math.ceil(interval_time_length/dt[i]) for i in range(int(len(dt)))]

memory= 0
num_obs = 0
num_pro=0
num_down= 0
memory_storage = int( 64e7) # 64GB total memory in 0.1kB
num_obs_init = 0

all_action = range(4)
all_sats = range(66)


start_shift = 0
b = start_shift

memory_storage = int( 64e7) # 64GB total memory in 0.1kB
num_obs_init = 0
all_action = range(4)
all_sats = range(66)

FLOP_to_proc = 1000
FLOPS_available = 100 # giga flops

obs_dataset_mem = int( 150e3/100 )# in 0.1 kB   
obs_rate = 100                    # used to allow the observations to be processed in parts while remaining integers

pro_rate = math.ceil(FLOP_to_proc/FLOPS_available)  # rate at which the system can process a dataset
pro_dataset_mem = int(300 /100)  # in 0.1 kB


down_rate_mem = 320  # in 0.1 kB per second
down_rate = int(down_rate_mem/pro_dataset_mem)  # the number of processed dataset units the satellite can downlink per second
down_dataset_mem = int(down_rate_mem/down_rate)



'''
bring in all data
'''

  
#read in if a illuminator is in view 
data = pd.read_csv("Data/pol/1s_5d/G40/Illuminator view data log.csv")
any_ilum_list = data.values.tolist()

#read in the downlink data times
data = pd.read_csv("Data/pol/1s_5d/G40//Communications Data log.csv")
datals= data.values.tolist() 

#  reads in which illuminators are visible
data = pd.read_csv("Data/pol/1s_5d/G40//Avg objects Detection log.csv")
ilum_value_list = data.values.tolist()

# chages downlink from list of lists to 1D list
gnd_stat_list = [datals[i][0] for i in range(0, len(datals))]


schedule_out_titles = ['Observing', 'Processing', 'downlinking', 'idling', 'num observed', 'num processed', 'num downlinked', 'memory used (kB)', 'Satellite targeted']

all_shifts=[range(interval_true_length[i]) for i in range(len(dt))]
mod_interval_length = [math.ceil(interval_true_length[i]/(2**i)) for i in range(len(dt))]
all_mod_shifts = [range(mod_interval_length[i]) for i in range(len(dt))]


for timeset in range(len(dt)):
    
    
    '''
    optimises it for the long time scale
    '''
    if timeset == 0:
          
        (model, shifts, target_ilum, num_obs, num_pro, num_down, memory, Log) = CPModel_SC_data(any_ilum_list,gnd_stat_list, interval_true_length[timeset],b, obs_dataset_mem, obs_rate, pro_dataset_mem,
                        pro_rate, down_rate,down_dataset_mem, memory, memory_storage, num_obs, num_pro, num_down,dt[timeset], ilum_value_list,switchtime, switching_constraint)
        
        c = interval_true_length[timeset]
        print("CP Model made for interval %i to %i" % (b,c))
        solver = cp_model.CpSolver()  


        solver.parameters.max_time_in_seconds =1000
    
        solver.parameters.log_search_progress = True
        solver.parameters.num_search_workers = 8
        
        status = solver.Solve(model)
        
        
        if status == cp_model.OPTIMAL :
            print('Solution: optimal found for interval %i to %i' % (b,c*dt[timeset]))
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
            print('\nStatistics')
            print('  - conflicts      : %i' % solver.NumConflicts())
            print('  - branches       : %i' % solver.NumBranches())
            print('  - wall time      : %f s' % solver.WallTime())
        
        
        memory= solver.Value(memory)
        num_obs = solver.Value(num_obs)
        num_pro= solver.Value(num_pro)
        num_down= solver.Value(num_down)
        
        
        '''
        write values out to files
        '''
        scheduleWrite = [[0  for a in range(9)] for s in all_mod_shifts[timeset]]
        target_ilum_val_inv = [["-"  for sat in all_sats] for s in all_mod_shifts[timeset]] 
        for s in all_mod_shifts[timeset]:
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
            
        
        name = "Alt_scheduleraw_up_to_shift %i" % (c*dt[timeset])    
        readwrite.df_to_xlsxOut(scheduleout,schedule_out_titles, name, path)
        
        
        
        
        
    if timeset > 0 :
        endpoint_constraints = []
        for i in range(4):
            multi =1
            if i == 3:
                multi = 10
            endpoint_constraints.append(multi*scheduleWrite[int(interval_true_length[0]/2)][i+4])
            
        (model, shifts, target_ilum, num_obs, num_pro, num_down, memory, Log) = CPModel_SC_data_endpoint_constraints(any_ilum_list,gnd_stat_list, interval_true_length[timeset],b, obs_dataset_mem, obs_rate, pro_dataset_mem,
                        pro_rate, down_rate,down_dataset_mem, memory, memory_storage, num_obs, num_pro, num_down,dt[timeset], ilum_value_list,switchtime, switching_constraint,endpoint_constraints)
        
        
        solver = cp_model.CpSolver()  


        solver.parameters.max_time_in_seconds =1000
    
        solver.parameters.log_search_progress = True
        solver.parameters.num_search_workers = 8
        
        status = solver.Solve(model)
        
        
        if status == cp_model.OPTIMAL :
            print('Solution: optimal found for interval %i to %i' % (b,c*dt[timeset]))
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
            print('\nStatistics')
            print('  - conflicts      : %i' % solver.NumConflicts())
            print('  - branches       : %i' % solver.NumBranches())
            print('  - wall time      : %f s' % solver.WallTime())
        
        
        memory= solver.Value(memory)
        num_obs = solver.Value(num_obs)
        num_pro= solver.Value(num_pro)
        num_down= solver.Value(num_down)
        
        
        '''
        write values out to files
        '''
        scheduleWrite = [[0  for a in range(9)] for s in all_mod_shifts[timeset]]
        target_ilum_val_inv = [["-"  for sat in all_sats] for s in all_mod_shifts[timeset]] 
        for s in all_mod_shifts[timeset]:
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
            
        
        name = "Alt_scheduleraw_up_to_shift %i" % (c*dt[timeset])    
        readwrite.df_to_xlsxOut(scheduleout,schedule_out_titles, name, path)
  
'''

    print("started making CP model")
    (model, shifts, target_ilum, num_obs, num_pro, num_down, memory, Log) = CPModel_SC_data(any_ilum_list,gnd_stat_list, interval,start_shift, obs_dataset_mem, obs_rate, pro_dataset_mem,
                    pro_rate, down_rate,down_dataset_mem, memory_init, memory_storage, num_obs_init, num_pro_init, num_down_init,dt_long, ilum_value_list,switchtime,switching_constraint)

    print("CP model made")
   
'''
