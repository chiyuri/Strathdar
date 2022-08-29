# -*- coding: utf-8 -*-
"""
Created on Mon Aug  8 14:26:47 2022

@author: iainh
"""



'''
Creates plots and post processing data from xlsx sheets with the results from
the optimisation
'''

import os
import math
import pandas as pd
from ortools.sat.python import cp_model
from Solver.CPModel_SC import CPModel_SC_data 
from utils import plotFunctions as pf
from utils import postProcessing as post
from utils import readwrite



filename = ["iainLaptop_M8_D17_H13_min24","iainLaptopManual_M8_D18_H11_min48",]
affix = "pol/60s_30d/G40/"

dt = 60

path = "results/figures/"+ affix +filename[0]
#os.mkdir(path)
scheduleout = []
ganttout = []
num_detect_Log_out = []

for j in  range(2):
    
    optimised_data = "results/" +affix + filename[j] + "/Alt_scheduleraw_up_to_shift 21000.xlsx"
    df = pd.read_excel(optimised_data)
    data = df.values.tolist()
    
    #  reads in which illuminators are visible
    df = pd.read_csv("Data/pol/60s_30d/G40 new area/Avg objects Detection log.csv")
    ilum_value_list = df.values.tolist()
    
    data_length = len(data)
    all_shifts = range(data_length)
    all_action = range(4)
    all_sat = range(66)
    time = [dt*t/3600 for t in all_shifts]
    
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
    
    
    '''
    taking data from excel sheet into consituent parts for post processing
    
    
    profitability calculation, check if it matches the profit calculated by the model
    cost function shown below
    sum(4*shifts[(2,s)]  + target_ilum[(sat,s)] * ilum_value_list[s][sat] for sat in all_sats for s in all_mod_shifts)
    '''
    schedule = [[],[],[],[]]
    schedule_abs = [[],[]]
    schedule_titles = [["Opt_Observe", "Opt_Process", "Opt_Downlink", "Opt_Idle"],["Man_Observe", "Man_Process", "Man_Downlink", "Man_Idle"]]
    schedule_inv = [[0  for s in all_shifts] for a in all_action]
    profitability_Log = [0 for s in all_shifts]
    profitability = 0
    profit_action = [0,0,66,0]
    num_detect= 0
    num_detect_Log = [0 for s in all_shifts]
    
    for s in all_shifts:
        for a in all_action:
            if data[s][a+1] == 1:
                schedule[a].append(1)
                schedule_abs[j].append(schedule_titles[j][a])
                schedule_inv[a][s] = 1
                profitability += profit_action[a]
       
        for sat in all_sat:
            if data[s][9] == sat and data[s][1] == 1:
                profitability += math.floor(ilum_value_list[s][sat]*10000)
                num_detect += dt*ilum_value_list[s][sat]
        profitability_Log[s]= profitability
        num_detect_Log[s] = num_detect
        
     # loop to assign gantt data to dictionary so it can be plotted   
    Gantt_data = []
              
    for s in all_shifts:
        tempDict = dict(start = s*dt/3600, duration = dt/3600, end = (s+1)*dt/3600, action = schedule_abs[j][s])
        Gantt_data.append(tempDict)

    scheduleout.append(schedule_inv)
    ganttout.append(Gantt_data)
    num_detect_Log_out.append(num_detect_Log)


    Gantt_df = pd.DataFrame(ganttout[j])
pf.ganttChart(Gantt_df,schedule_titles,path)
 


(memoryLogs1, num_logs1) = post.memoryLogAssem(scheduleout[0], obs_dataset_mem, pro_dataset_mem, obs_rate, pro_rate, down_rate,dt)
(memoryLogs2, num_logs2) = post.memoryLogAssem(scheduleout[1], obs_dataset_mem, pro_dataset_mem, obs_rate, pro_rate, down_rate,dt)

pf.memoryGraph_compare(memoryLogs1,memoryLogs2,time,path)
pf.memoryGraph_compare(memoryLogs1,memoryLogs2,time,path)

pf.ProfitGraph(profitability_Log, time,path)
pf.detectionsGraph_compare(num_detect_Log_out,time,path)
print(num_detect)
