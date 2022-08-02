# -*- coding: utf-8 -*-
"""
Created on Mon Aug  1 11:13:01 2022

@author: iainh
"""





def memoryLogAssem(schedule, obs_mem_size, pro_mem_size, obs_rate, pro_rate, down_rate,dt):
    
    # creates graphs logging the memory used for a given schedule
    
    all_action = range(len(schedule))
    all_shifts = range(len(schedule[0]))
    
    mem_log = [[0 for s in all_shifts] for a in all_action]
    num_log = [[0 for s in all_shifts] for a in all_action]
    num = [0 for a in all_action]
    
    for s in all_shifts:
        if schedule[0][s] == 1:
            num[0] += obs_rate
        
        if schedule[1][s] == 1:
            num[1] += pro_rate
            num[0] += -pro_rate
        if schedule[2][s] == 1:                  
            num[1] += -down_rate
            num[2] += down_rate
        
        # for observation
        num_log[0][s] = num[0]
        mem_log[0][s] = num_log[0][s] * obs_mem_size*dt
        
        # for processing
        num_log[1][s] = num[1]
        mem_log[1][s] = num_log[1][s] * pro_mem_size*dt
        
        # for downlinking
        
        num_log[2][s] = num[2] 
        mem_log[2][s] = num_log[2][s]*dt
        # overall memory use
        mem_log[3][s] = mem_log[0][s]+mem_log[1][s]
    
    
    
    
    return mem_log, num_log