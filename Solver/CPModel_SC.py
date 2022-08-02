# -*- coding: utf-8 -*-
"""
Created on Thu Jul 28 12:04:45 2022

@author: iainh
"""


from ortools.sat.python import cp_model

#from file_recall import file_recall
import os



def CPModel_SC_data(Any_Ilum_list,Gnd_stat_list, interval,start_shift, obs_mem_size, obs_rate, pro_mem_size,
                    pro_rate, down_rate, memory_init, memory_storage, num_obs_init,dt, ilum_value_list):
    
    model = cp_model.CpModel()
    
    num_actions = 4
    num_sats = 66
    all_action = range(num_actions)
    all_mod_shifts = range(interval)
    all_shifts = range(start_shift, interval + start_shift)
    all_sats = range(num_sats)
    
    b = start_shift
 
    
    # making the boolean variable which contains the action chosen by the optimiser
    shifts = {}
    target_ilum = {}
    index = {}
    for s in all_mod_shifts:
        
        
        for a in all_action:
            shifts[(a,s)] = model.NewBoolVar('Shift_A%i_S%i' % (a,s))
        for sat in all_sats:
            target_ilum[(sat,s)] = model.NewBoolVar('Target_Ilum_Sat%i_S%i' % (sat,s))
            
            #indexed positions are:
            # 0 = observing
            # 1 = processing
            # 2 = downlinking
            # 3 = idling
      
    # limits the optimiser to one action at any time
    
    for s in all_mod_shifts:
        model.AddExactlyOne(shifts[(a,s)] for a in all_action)
        model.AddAtMostOne(target_ilum[(sat,s)] for sat in all_sats)
        
        
    for s in all_mod_shifts:
        # requires an illuminator to be in view for observing to occur
        AnyIlum = sum(Any_Ilum_list[s][sat] for sat in all_sats)
        model.Add( AnyIlum > 0).OnlyEnforceIf(shifts[(0,s)])
        # requires a ground station to be in view for downlinking to occur
        model.Add(Gnd_stat_list[s] > 0).OnlyEnforceIf(shifts[(2,s)])
        
        model.Add(sum(target_ilum[(sat,s)] for sat in all_sats) > 0 ).OnlyEnforceIf(shifts[(0,s)])
        model.Add(sum(target_ilum[(sat,s)] for sat in all_sats) == 0 ).OnlyEnforceIf(shifts[(0,s)].Not())
        
    if b == 0 :
        memory = int(0) 
        
        num_obs = int( 0)
        num_pro = int(0)
        num_down = int(0)
    else:
        memory = memory_init  # needs to be replaced with a file read in
        num_obs = num_obs_init
        
    for s in all_mod_shifts:
        
        num_obs += dt*(shifts[(0,s)] * obs_rate - shifts[(1,s)]  * pro_rate) #100 = one 1 seconde dataset
        
        num_pro += dt*(shifts[(1,s)] * pro_rate - shifts[(2,s)] * down_rate) #100 = one 1 seconde dataset
        
        num_down += dt*(shifts[(2,s)] * down_rate) #100 = one 1 seconde dataset
        
        #memory += (shifts[(0,s)] * obs_rate *obs_mem_size + shifts[(1,s)] *pro_rate* (pro_mem_size - obs_mem_size)   - shifts[(2,s)] *int( (down_rate)))
        #memory += *obs_mem_size + num_pro*pro_mem_size
        memory += shifts[(0,s)] * obs_rate *obs_mem_size  + shifts[(1,s)] *pro_rate* (pro_mem_size - obs_mem_size)- shifts[(2,s)] *down_rate
        # require data sets to be available for processing for processing to occur
        model.Add(num_obs >= pro_rate).OnlyEnforceIf(shifts[(1,s)])
        # requires processed data sets to available for downlinking to occur
        model.Add(num_pro*pro_mem_size >= down_rate).OnlyEnforceIf(shifts[(2,s)])
        #requires used memory to remain below memory available
        model.Add(memory < memory_storage)
        
    
    model.Maximize(sum(4*shifts[(2,s)] + sum( target_ilum[(sat,s)]*ilum_value_list[s][sat] for sat in all_sats) for s in all_mod_shifts))
    #model.Maximize 
    
    return model, shifts, target_ilum, num_obs, num_pro, num_down, memory
        
        
        
        