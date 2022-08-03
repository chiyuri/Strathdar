# -*- coding: utf-8 -*-
"""
Created on Thu Jul 28 14:18:06 2022

@author: iainh
"""

# CP model tester, not for long term use

import math
import pandas as pd
from ortools.sat.python import cp_model
from CPModel_SC import CPModel_SC_data
from Strathdar.utils.plotFunctions import ganttChart
data = pd.read_csv("../Data/30s, 1d, polar/Illuminator view data log.csv")
any_ilum_list = data.values.tolist()

#read in the downlink data times
data = pd.read_csv("../Data/30s, 1d, polar/Communications Data log.csv")
datals= data.values.tolist() 
# chages downlink from list of lists to 1D list
gnd_stat_list = [datals[i][0] for i in range(0, len(datals))]



FLOP_to_proc = 920
FLOPS_available = 92 # giga flops

interval = 1000
start_shift=0
obs_mem_size = 1500
obs_rate = 1 
pro_mem_size = 30
pro_rate = math.ceil(FLOP_to_proc/FLOPS_available)
down_rate = 32
memory_init = 0
memory_storage = 64000
num_obs_init = 0


(model, shifts, num_obs, num_pro, num_down, memory) = CPModel_SC_data(any_ilum_list,gnd_stat_list, interval,start_shift, obs_mem_size, obs_rate, pro_mem_size,
                    pro_rate, down_rate, memory_init, memory_storage, num_obs_init)

solver = cp_model.CpSolver()

solver.parameters.max_time_in_seconds = 600
solver.parameters.log_search_progress = True
solver.parameters.num_search_workers = 4

status = solver.Solve(model)
if status == cp_model.OPTIMAL :
    print('Solution: optimal found')

elif status == cp_model.FEASIBLE:
    print('Solution: feasible found')
else:
    print('not feasible solution found')
    

