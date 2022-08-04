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

full_horizon = 3000
interval_size = 1000
dt= 60


hint = 0

switchtime =0

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





'''
File read in 
'''


'''
create model
'''
memory_init = 0
num_obs_init = 0
num_pro_init=0
num_down_init = 0

num_obs_init = 0
all_mod_shifts = range(interval_size)
'''
run model
'''




'''
write values out to files
'''
