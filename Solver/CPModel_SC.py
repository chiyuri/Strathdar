# -*- coding: utf-8 -*-
"""
Created on Thu Jul 28 12:04:45 2022

@author: iainh
"""


from ortools.sat.python import cp_model

#from file_recall import file_recall
import os

'''
Used to generate a Constraint Programming model using google OR tools for Strathcube under 
conditions where it can do some processing on board but no real time processing

Inputs:
    
Any_Ilum_list: boolean list of lists containing the illuminators in view over time 
Gnd_stat_list: boolean list containing whether a ground station is in view
interval: the interval to be optimised over
start_shift: the shift that the model starts at (with reference to the indesx position in input lists)
obs_mem_size: the memory used to store one unit of observed dataset
obs_rate: the rate at which observed dataset units are produced while observing
pro_mem_size: the memory used to store one unit of processed dataset
pro_rate: the rate at which observed dataset units are processed into processed dataset units
down_rate: the rate at which processed data set units can be downlinked
memory_init: the initial memory in use
num_obs_init: the number of observations already stored
dt: the number of seconds for each shift
ilum_value_list: the value associated with each illiminator through time


Outputs:

model: the CP model
shifts: dict containing google or bool variables and used to describe what action the satellite is taking for a given shift
target_ilum: the illuminator targeted at a given shift
num_obs: the number of observations stored at the end of the interval
num_pro: the number of processed datasets stored at the end of the interval
num_down: the number of downlinked datasets at the end of the interval
memory: the memory in use at the end of the interval
'''




def CPModel_SC_data(Any_Ilum_list,Gnd_stat_list, interval,start_shift, obs_mem_size, obs_rate, pro_mem_size,
                    pro_rate, down_rate,down_mem_size, memory_init, memory_storage, num_obs_init, num_pro_init, num_down_init,dt, ilum_value_list, switchtime, switching_constraint):
    
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
        
        #constraint to ensure that a illuminator is targeted when observing 
        model.Add(sum(target_ilum[(sat,s)] for sat in all_sats) > 0 ).OnlyEnforceIf(shifts[(0,s)])
        #constraint to ensure no illuminator is targetes when not observing
        model.Add(sum(target_ilum[(sat,s)] for sat in all_sats) == 0 ).OnlyEnforceIf(shifts[(0,s)].Not())
        
        if switching_constraint ==1:
            for sat in all_sats:
                if Any_Ilum_list[s][sat] == 1:
                    if s > switchtime-1 and s < interval-switchtime-1:
                      
                            model.Add(sum(target_ilum[(sat_mod,s_mod)] for sat_mod in range(0,sat-1) for s_mod in range(s-switchtime,s+switchtime ) )  == 0).OnlyEnforceIf(target_ilum[(sat,s)])
                            model.Add(sum(target_ilum[(sat_mod,s_mod)] for sat_mod in range(sat+1,65) for s_mod in range(s-switchtime,s+switchtime ) )  == 0).OnlyEnforceIf(target_ilum[(sat,s)])
                    elif s <= switchtime-1:
                        
                            model.Add(sum(target_ilum[(sat_mod,s_mod)] for sat_mod in range(0,sat-1) for s_mod in range(0,s+switchtime ) )  == 0).OnlyEnforceIf(target_ilum[(sat,s)])
                            model.Add(sum(target_ilum[(sat_mod,s_mod)] for sat_mod in range(sat+1,65) for s_mod in range(0,s+switchtime ) )  == 0).OnlyEnforceIf(target_ilum[(sat,s)])
                    elif s >= interval-switchtime-1:
                        
                            model.Add(sum(target_ilum[(sat_mod,s_mod)] for sat_mod in range(0,sat-1) for s_mod in range(s-switchtime, interval-1 ) )  == 0).OnlyEnforceIf(target_ilum[(sat,s)])
                            model.Add(sum(target_ilum[(sat_mod,s_mod)] for sat_mod in range(sat+1,65) for s_mod in range(s-switchtime, interval-1 ) )  == 0).OnlyEnforceIf(target_ilum[(sat,s)])   
                            '''
            if switching_constraint ==1:
            if any_ilum_list[s][sat] == 1
                if s > switchtime-1 and s < interval-switchtime-1:
                    for sat in all_sats:
                        model.Add(sum(target_ilum[(sat_mod,s_mod)] for sat_mod in range(0,sat-1) for s_mod in range(s-switchtime,s+switchtime ) )  == 0).OnlyEnforceIf(target_ilum[(sat,s)])
                        model.Add(sum(target_ilum[(sat_mod,s_mod)] for sat_mod in range(sat+1,65) for s_mod in range(s-switchtime,s+switchtime ) )  == 0).OnlyEnforceIf(target_ilum[(sat,s)])
                elif s <= switchtime-1:
                    for sat in all_sats:
                        model.Add(sum(target_ilum[(sat_mod,s_mod)] for sat_mod in range(0,sat-1) for s_mod in range(0,s+switchtime ) )  == 0).OnlyEnforceIf(target_ilum[(sat,s)])
                        model.Add(sum(target_ilum[(sat_mod,s_mod)] for sat_mod in range(sat+1,65) for s_mod in range(0,s+switchtime ) )  == 0).OnlyEnforceIf(target_ilum[(sat,s)])
                elif s >= interval-switchtime-1:
                    for sat in all_sats:
                        model.Add(sum(target_ilum[(sat_mod,s_mod)] for sat_mod in range(0,sat-1) for s_mod in range(s-switchtime, interval-1 ) )  == 0).OnlyEnforceIf(target_ilum[(sat,s)])
                        model.Add(sum(target_ilum[(sat_mod,s_mod)] for sat_mod in range(sat+1,65) for s_mod in range(s-switchtime, interval-1 ) )  == 0).OnlyEnforceIf(target_ilum[(sat,s)])   
         '''
             
    if b == 0 :
        memory = int(0) 

        num_obs = int( 0)
        num_pro = int(0)
        num_down = int(0)
    else:
        memory = memory_init  # needs to be replaced with a file read in
        num_obs = num_obs_init
        num_pro = num_pro_init
        num_down = num_down_init
        
    
    Log = [[],[],[],[]]
    for s in all_mod_shifts:
        
        num_obs += dt*(shifts[(0,s)] * obs_rate - shifts[(1,s)]  * pro_rate) #100 = one 1 seconde dataset
        Log[0].append(num_obs) 
        num_pro += dt*(shifts[(1,s)] * pro_rate - shifts[(2,s)] * down_rate) #100 = one 1 seconde dataset
        Log[1].append(num_pro)
        num_down += dt*(shifts[(2,s)] * down_rate) #100 = one 1 second dataset
        Log[2].append(num_down)
        #memory += (shifts[(0,s)] * obs_rate *obs_mem_size + shifts[(1,s)] *pro_rate* (pro_mem_size - obs_mem_size)   - shifts[(2,s)] *int( (down_rate)))
        #memory += *obs_mem_size + num_pro*pro_mem_size
        memory += dt*(shifts[(0,s)] * obs_rate *obs_mem_size  + shifts[(1,s)] *pro_rate* (pro_mem_size - obs_mem_size)- shifts[(2,s)] *down_rate*down_mem_size)
        Log[3].append(memory)
        # require data sets to be available for processing for processing to occur
        model.Add(num_obs >= pro_rate*dt).OnlyEnforceIf(shifts[(1,s)])
        # requires processed data sets to available for downlinking to occur
        model.Add(num_pro*pro_mem_size >= down_rate*dt).OnlyEnforceIf(shifts[(2,s)])
        #requires used memory to remain below memory available
        model.Add(memory < memory_storage)
        
    
    model.Maximize(sum(4*shifts[(2,s)]  + target_ilum[(sat,s)] * ilum_value_list[s][sat] for sat in all_sats for s in all_mod_shifts))
                                                                #^^sum( target_ilum[(sat,s)]for sat in all_satsilum_value_list[s][sat]
    
    return model, shifts, target_ilum, num_obs, num_pro, num_down, memory, Log
        

  
        
    