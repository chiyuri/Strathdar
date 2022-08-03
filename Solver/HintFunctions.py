# -*- coding: utf-8 -*-
"""
Created on Wed Aug  3 10:49:27 2022

@author: iainh
"""


def CreateManHint(ilum_in_view,target_value, gnd_in_view, all_action,all_shifts, all_sat, obs_mem_size, obs_rate, pro_mem_size,
                    pro_rate, down_rate, memory_init, memory_storage, num_obs_init,num_pro_init, dt):
            
    hint_shifts = [[0 for s in all_shifts ] for a in all_action] #4 by time length variable
    hint_target_ilum = [[0 for s in all_shifts] for sat in all_sat]
    
    memory = memory_init
    num_pro = num_pro_init
    num_obs = num_obs_init
    
    for s in all_shifts:
        
        if gnd_in_view[s] == 1 and num_pro> down_rate*dt:
            hint_shifts[2][s] = 1
            num_pro -= down_rate*dt
        
        elif sum(ilum_in_view[s][sat] for sat in all_sat) > 0 and memory <= memory_storage - obs_mem_size*obs_rate*dt:
            hint_shifts[0][s] = 1
            num_obs
        elif num_obs > pro_rate*dt:
            hint_shifts[1][s] = 1
            num_obs -= pro_rate*dt
            num_pro += pro_rate*dt
        else:
            hint_shifts[3][s] = 0
        
        if max(target_value[s]) > 0:
            maxval=0
            index = 0
            for sat in all_sat:
                if target_value[s][sat]>maxval:
                    maxval = target_value[s][sat]
                    index = sat
            hint_target_ilum[index][s] = 1

    return hint_shifts, hint_target_ilum

def AddHint(model, shifts, target_ilum, hint_shifts, hint_target_ilum, all_mod_shifts, all_action, all_sats):
        
        
    for s in all_mod_shifts:
        for a in all_action:
            if hint_shifts[a][s] == 1:
                model.AddHint(shifts[(a,s)], 1)
        for sat in all_sats:
            if hint_target_ilum[sat][s] == 1:
                model.AddHint(target_ilum[(sat,s)], 1)
        
        
        
    return model, shifts, target_ilum