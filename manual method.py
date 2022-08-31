# -*- coding: utf-8 -*-
"""
Created on Mon Aug 15 12:25:28 2022

@author: iainh




"""


import os
import datetime
import math
import pandas as pd
from ortools.sat.python import cp_model
from Solver.CPModel_SC import CPModel_SC_data 
from Solver.HintFunctions import CreateManHint, AddHint#, CreateManHint_SwitchingConstraint
from utils import readwrite

'''
ideintification of intervals and initial values
'''


full_horizon = 21000
interval_size = 21000
b = 0
c = b + interval_size
hint = 1
switchtime =1
affix = "iss/60s_30d/G40/"
switching_constraint = 1
dt = 60
hot_start =0# defines whether it should start from data already partially optimised




num_interval = math.ceil(full_horizon/interval_size)


file_affix = "60s_30d_pol_"



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
current_time = datetime.datetime.now()
month =  str(current_time.month)
day = str(current_time.day)
hour = str(current_time.hour)
minute = str(current_time.minute)
time_now = "_M" + month + "_D" +day +"_H" + hour + "_min" + minute
path = "./results/" + affix + "iainLaptopManual"
path = path +time_now
os.mkdir(path)
path = path+ "/"

#read in if a illuminator is in view 
data = pd.read_csv("Data/" + affix +"/Illuminator view data log.csv")
temp = data.values.tolist()
any_ilum_list = temp[b:c] 
#read in the downlink data times
data = pd.read_csv("Data/" + affix +"/Communications Data log.csv")
temp= data.values.tolist() 
datals = temp[b:c]

# chages downlink from list of lists to 1D list
gnd_stat_list = [datals[i][0] for i in range(0, len(datals))]

#  reads in which illuminators are visible
data = pd.read_csv("Data/" + affix +"/Avg objects Detection log.csv")
temp = data.values.tolist()
ilum_value_list = temp[b:c]

for s in all_mod_shifts:
    for sat in all_sats:
        ilum_value_list[s][sat] = math.floor(ilum_value_list[s][sat]*10000)
    
(hint_shifts, hint_target_ilum,Log ) = CreateManHint(any_ilum_list,ilum_value_list, gnd_stat_list, all_action,all_mod_shifts, all_sats, obs_dataset_mem, obs_rate, pro_dataset_mem,
                    pro_rate, down_rate, memory, memory_storage, num_obs,num_pro, dt, switching_constraint)





   
'''
write values out to files
'''
scheduleWrite = [[0  for a in range(9)] for s in all_mod_shifts]
target_ilum_val_inv = [[0  for sat in all_sats] for s in all_mod_shifts] 
for s in all_mod_shifts:
    for a in all_action:
        if hint_shifts[a][s] == 1:
          
            scheduleWrite[s][a] = 1
    for i in range(4):
        multi =1
        if i ==3:
            multi = 0.1
        scheduleWrite[s][i+4] = Log[i][s]
        
            
    for sat in all_sats:
        if hint_target_ilum[sat][s] == 1:
            scheduleWrite[s][8] = sat
            target_ilum_val_inv[s][sat] = 1
ind = [i for i in range(b,c)]

if b == 0:
    
    scheduleout= pd.DataFrame(scheduleWrite,index = ind, columns=schedule_out_titles)
    
else:
    dftemp = pd.DataFrame(scheduleWrite,index = ind, columns=schedule_out_titles)
    scheduleout= scheduleout.append(dftemp)
    

name = "Alt_scheduleraw_up_to_shift %i" % (c)    
readwrite.df_to_xlsxOut(scheduleout,schedule_out_titles, name, path)
  















