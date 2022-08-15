# -*- coding: utf-8 -*-
"""
Created on Wed Jul 27 10:18:21 2022

@author: iainh
"""

#import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
#import plotly.io as pio
#pio.renderers.default='svg'



def ganttChart(df,titles):
    
    # function for creating Gantt chart from a set of tasks completed at associated times, the time index they are against, and the task names
    
    
    
    fig, ax = plt.subplots(1, figsize = (15,6))
    
    ax.barh(df.action , df.duration, left=df.start)
    fig.show()
    
    """
    fig = px.timeline(df, x_start ="start", x_end = "end", y = "action",color = "action") 
    fig.show()
    #fig.write_image(file="gantt_test", format='png', scale=1, width=2500, height=1250)
    """
    
def memoryGraph(memoryLog, time):
    
    #Creates a plot of the memory used storying observed and processed datasets as well as the total memory use
    
    plt.figure(2)
    plt.plot(time,memoryLog[0], color = 'green')
    plt.plot(time,memoryLog[1], color = 'blue')
    plt.plot(time,memoryLog[3], color = 'grey', linestyle='dashed')
    plt.title("Storage use over time")
    plt.xlabel("time (hr)")
    plt.ylabel("memory used (MB)")
    plt.legend(["Observation Data set memory use","processed data set memory use","Max storage"])
    ax = plt.gca()
    #ax.set_xticklabels([])

    plt.figure(3)
    plt.plot(time,memoryLog[1],color = 'blue')
    plt.plot(time,memoryLog[2],color = 'red')
    plt.title("storage used and downlniked over time ")
    plt.legend(["Processed","Downlinked"])
    plt.xlabel("time (hr)")
    plt.ylabel("memory used (MB)")
    ax = plt.gca()
    #ax.set_xticklabels([])    
    
def ProObsGraph(ProObsLog,time):
    
    # plots the number of processed and observed datasets over time as well as overall memory use
    
    plt.figure(4)
    plt.plot(time, ProObsLog)
    plt.title("Processed and Observations over time")
    plt.xlabel("time (hr)")
    plt.ylabel("number processed/observed datasets")
    plt.legend(["observations", "processed","Downlinked"])
    ax = plt.gca()
    #ax.set_xticklabels([])
    
    
def downlinkingGraph(downlink, time):
    
    # plots whenever the satellite is downlinking 
    
    plt.figure(5)
    plt.plot(time, downlink)
    plt.title("downlinking activity over time")
    plt.xlabel("time (hr)")
    plt.ylabel("downlinking (y/n)")
    ax = plt.gca()
    ax.set_xticklabels([])
    

def ObsValueGraph(ilum_value_list,target_ilum, action, time, all_T, all_sats):
    
    #plots the observed value and the value available
    
    allvalue = [0 for t in all_T]
    valueObs = [0 for t in all_T]
    
    for t in all_T:
        allvalue[t] = max(ilum_value_list[t][sat] for sat in all_sats)
        valueObs[t] = sum(target_ilum[sat][t]*ilum_value_list[t][sat] for sat in all_sats)
        valueObsCheck = allvalue[t]* action[0][t]    
        if valueObsCheck != valueObs[t]:
            print("error in targeting")
            print("csp targets sat with value %i" % valueObs[t])
            print("highest value available is %i" % valueObsCheck)
    
    
    
    
    plt.figure(6)
    
    plt.plot(time, allvalue)
    plt.plot(time, valueObs)
    
    plt.title("Iluminator value, tatgeted and available")
    plt.xlabel("time (hr)")
    plt.ylabel("iluminator value (avg objects detected)")
    plt.legend(["Ilum value available","Target Ilum Value"])
    ax = plt.gca()
    #ax.set_xticklabels([])
    #ax.set_yticklabels([])
    
    
    
def ProfitGraph(profitability, time):
     
    # plots the schedules profitability over time
    
    plt.figure(5)
    plt.plot(time, profitability)
    plt.title("schedule profit over time")
    plt.xlabel("time (hr)")
    plt.ylabel("profit")
    ax = plt.gca()

    
    
    
    
    
    
    
    
    