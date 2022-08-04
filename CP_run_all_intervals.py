# -*- coding: utf-8 -*-
"""
Created on Thu Aug  4 15:17:05 2022

@author: iainh
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

full_horizon = 5000
interval_size = 1000
dt= 60
a = 0
b = interval_size
hint = 0
switchtime =0

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
num_obs= 0

for interval in all_interval:
    
    
    interval_shifts=range(a,b)
    all_mod_shifts = range(b-a)
    '''
    File read in 
    '''
    #read in if a illuminator is in view 
    data = pd.read_csv("Data/60s, 5d, polar/Illuminator view data log.csv")
    temp = data.values.tolist()
    any_ilum_list = temp[a:b] 
    #read in the downlink data times
    data = pd.read_csv("Data/60s, 5d, polar/Communications Data log.csv")
    temp= data.values.tolist() 
    datals = temp[a:b]
    
    # chages downlink from list of lists to 1D list
    gnd_stat_list = [datals[i][0] for i in range(0, len(datals))]
    #  reads in which illuminators are visible
    data = pd.read_csv("Data/60s, 5d, polar/Avg objects Detection log.csv")
    temp = data.values.tolist()
    ilum_value_list = temp[a:b]
    
    for s in all_mod_shifts:
        for sat in all_sats:
            ilum_value_list[s][sat] = math.floor(ilum_value_list[s][sat]*10000)
    
    '''
    create model
    '''
    
    
    (model, shifts, target_ilum, num_obs, num_pro, num_down, memory, Log) = CPModel_SC_data(any_ilum_list,gnd_stat_list, interval,a, obs_dataset_mem, obs_rate, pro_dataset_mem,
                    pro_rate, down_rate,down_dataset_mem, memory, memory_storage, num_obs, num_pro, num_down,dt, ilum_value_list,switchtime)
    print("CP Model made for interval %i to %i" % (a,b))

    '''
    run model
    '''
    
    
    
    
    
    '''
    write values out to files
    '''
    
    
 
    a += interval_size
    b = a+interval_size-1
  
        