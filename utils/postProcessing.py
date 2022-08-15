# -*- coding: utf-8 -*-
"""
Created on Mon Aug  1 11:13:01 2022

@author: iainh
"""





def memoryLogAssem(schedule, obs_mem_size, pro_mem_size, obs_rate, pro_rate, down_rate,dt):
    
    # creates graphs logging the memory used for a given schedule
    
    all_action = range(len(schedule))
    all_shifts = range(len(schedule[0]))
    
    scalefactor= 10000 # used to modify the memory to be in MB
    
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
        mem_log[0][s] = num_log[0][s] * obs_mem_size*dt/scalefactor
        
        # for processing
        num_log[1][s] = num[1]
        mem_log[1][s] = num_log[1][s] * pro_mem_size*dt/scalefactor
        
        # for downlinking
        
        num_log[2][s] = num[2] 
        mem_log[2][s] = num_log[2][s]*dt/scalefactor
        # overall memory use
        mem_log[3][s] = 64e3#mem_log[0][s]+mem_log[1][s]/scalefactor
    
    
    
    
    return mem_log, num_log

def target_printer(solver, shifts, target_ilum, ilum_value, all_shifts,all_action,all_sat):
    
    for s in all_shifts:
        text = "Shift %i satellite targets: \n" % (s)
        
        n=0
        for sat in all_sat:
            
            if solver.Value(target_ilum[(sat,s)]) != 0:
                n = 1
                text = text + "illuminator %i for value: %i  \n" % (sat, ilum_value[s][sat]) 
        if n == 1:        
            print(text)
    
    
    
    return