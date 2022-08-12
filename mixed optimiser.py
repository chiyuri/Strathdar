# -*- coding: utf-8 -*-
"""
Created on Wed Aug 10 13:42:56 2022

@author: iainh


Wierd script to try and optimise over long time range then solwly optimise over smaller time scales


"""

import math
import pandas as pd
from ortools.sat.python import cp_model
from Solver.CPModel_SC import CPModel_SC_data 
from Solver.HintFunctions import CreateManHint, AddHint
from utils import plotFunctions as pf
from utils import postProcessing as post
from utils import readwrite
  


# initialisation stuff

hint = 1
switchtime =4
affix = "pol/1s_5d/G40/"
interval = 3600# interval in dt_min to be optimised
switching_constraint = 1
dt_min = 1
dt_long = 60

memory_init = 0
num_obs_init = 0
num_pro_init=0
num_down_init = 0
memory_storage = int( 64e7) # 64GB total memory in 0.1kB
num_obs_init = 0
all_shifts = range(interval)
all_action = range(4)
all_sats = range(66)


start_shift = 0
memory_init = 0
num_obs_init = 0
num_pro_init=0
num_down_init = 0
memory_storage = int( 64e7) # 64GB total memory in 0.1kB
num_obs_init = 0
all_T = range(interval)
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


'''
create lists with data instances on dt_max
'''
any_ilum_list_long = []
ilum_value_list_long= []
gnd_stat_list_long = []

interval_long = math.floor(86400/dt_long)
all_shifts_long = range(interval_long)


for s in all_shifts_long:
    any_ilum_list_long.append(any_ilum_list[s*dt_long])
    ilum_value_list_long.append(ilum_value_list[s*dt_long])
    gnd_stat_list_long.append(gnd_stat_list[s*dt_long])


'''
optimises it for the long time scale
'''
print("started making CP model")
(model, shifts, target_ilum, num_obs, num_pro, num_down, memory, Log) = CPModel_SC_data(any_ilum_list,gnd_stat_list, interval,start_shift, obs_dataset_mem, obs_rate, pro_dataset_mem,
                    pro_rate, down_rate,down_dataset_mem, memory_init, memory_storage, num_obs_init, num_pro_init, num_down_init,dt_long, ilum_value_list,switchtime,switching_constraint)

print("CP model made")

'''
assigns this optimised schedule to a schedule variable with dt = dtmin
'''


'''
define constraints for midpoint
'''

'''
optimise 1st half
'''

'''
optimise second half
'''


'''
plot and cry
'''