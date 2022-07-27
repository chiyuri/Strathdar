# -*- coding: utf-8 -*-
"""
Created on Mon Jul 25 11:39:55 2022

@author: iainh

Script used to create an offline schedule using a manual heuristic for STRATHcube

non optimal and will prioritise tasks based on only information at a single point in time
will prioritise:
    Downlinking    
    Observing
    Processing
    Idle
these actions are held in an action array where 
0 = observing
1 = downlink
2 = Processing
3 = idle
"""


# code to import the potential target data



import pandas as pd
import numpy as np
from readwrite import xlsxOut
import plotFunctions


dt = 5

#read in the illuminator data value (avg objects detected in time increment)
data = pd.read_csv("../Data/5s, 5d, polar/Avg objects Detection log.csv ")
target_value = data.values.tolist()

data = pd.read_csv("../Data/5s, 5d, polar/Illuminator view data log.csv")
ilum_in_view = data.values.tolist()

#read in the downlink data times
data = pd.read_csv("../Data/5s, 5d, polar/Communications Data log.csv")
datals= data.values.tolist() 



downlink_possible = [datals[i][0] for i in range(0, len(datals))]
    


num_T = len(target_value) # final time incriment
num_sats = 66   # illuminating satellites
num_actions = 4
all_sats = range(num_sats)   
all_T = range(num_T)
all_actions = range(num_actions)

action = [[0 for a in all_actions ] for t in all_T] #4 by time length variable
actionABS = [0 for t in all_T] # measure task in int value between 0 and 3
target_sat = [[0 for s in all_sats] for t in all_T]
memoryLog = [0 for t in all_T]
time = [[i*dt] for i in range(0,len(data))]
#constrained resource variables
# note memory is in kB
maxStorage = 64e3
dataPerObs = 1500
dataPerPro = 29

obsSize = 50
proSize = 10
dowSize = 100



storedData= 0
ObsStored = 0
Processed = 0 
Downlinks = 0
ObservedValue = []
ObsValIndex = 0
ProcessedValue = []
ProValIndex = 0
DownlinkedValue = []
DownValIndex = 0

# Heuristic implementation within loop
for t in all_T:
    
    if downlink_possible[t] == 1 and Processed > 1: # downlink decision (pos 2)
        
        #DownlinkedValue.append(ProcessedValue[ProValIndex])
        actionABS[t] = "downlink" 
        action[t][2] = 1
        
        storedData = storedData - 250
        memoryLog[t] = storedData
        
        Downlinks += dowSize
        Processed -= dowSize
        
        
    elif sum(ilum_in_view[t][s] for s in all_sats)== 1 and storedData <= maxStorage + dataPerObs:  # observe decision pos 0
        actionABS[t] = "observe"
        action[t][0] = 1
        #ObservedValue.append(max(target_value[t][s] for s in all_sats))
        #storedData = storedData + dataPerObs
        
        
        ObsStored += obsSize
        
    elif ObsStored > 1:      # process decision  (pos 1)
    
        actionABS[t] = "process"
        action[t][1] = 1
        #ProcessedValue.append(ObservedValue[ObsValIndex])
        ObsValIndex += 1
        
        ObsStored -= proSize
        Processed += proSize
        
        #storedData = storedData - dataPerObs + dataPerPro
        #memoryLog[t] = storedData
        
    else:
        action[t][3] =1     # idle decision pos 3
        actionABS[t] = "idle"
        #memoryLog[t] = storedData
        
    storedData = ObsStored*dataPerObs + Processed*dataPerPro
    memoryLog[t] = storedData
    
    
titles = ['Time (s)','Observing', 'Processing', 'downlinking', 'idling']
name = 'Manual Heuristic results'
destination = "../results/manual heuristic/"
actionOut = time
for t in all_T:
    for a in all_actions:
        actionOut[t].append(action[t][a])
    
xlsxOut(actionOut,titles,name,destination)


# need to learn hoew to make gantt chart better
titles = ['Observing', 'Processing', 'downlinking', 'idling']
data = []
for t in all_T:
    tempDict = dict(start = t*dt, duration = dt, end = (t+1)*dt, action = actionABS[t])
    data.append(tempDict)
df = pd.DataFrame(data)

plotFunctions.ganttChart(df,titles)

time = [t*dt for t in all_T]
plotFunctions.memoryGraph(memoryLog,time)


print("completed manual heuristic")







