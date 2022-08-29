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



def ganttChart(df,titles,path):
    
    # function for creating Gantt chart from a set of tasks completed at associated times, the time index they are against, and the task names
    
    
    
    fig, ax = plt.subplots(1, figsize = (15,6))
    
    ax.barh(df.action , df.duration, left=df.start)
    fig.show()
    name = path + "/ganttChart.png"
    fig.savefig(name)
    
    """
    fig = px.timeline(df, x_start ="start", x_end = "end", y = "action",color = "action") 
    fig.show()
    #fig.write_image(file="gantt_test", format='png', scale=1, width=2500, height=1250)
    """
    
def memoryGraph(memoryLog, time,path):
    
    #Creates a plot of the memory used storying observed and processed datasets as well as the total memory use
    
    plt.figure(2)
    plt.plot(time,memoryLog[0], color = 'green')
    plt.plot(time,memoryLog[2], color = 'blue')
    #plt.plot(time,memoryLog[3], color = 'grey', linestyle='dashed')
    plt.title("Storage use over time")
    plt.xlabel("Time (hr)")
    plt.ylabel("memory used (MB)")
    plt.legend(["Observation Data Use","Downlinked Data"])
    ax = plt.gca()
    #ax.set_xticklabels([])
    name = path + "/unprocessed_memory.png"
    plt.savefig(name)

    plt.figure(3)
    plt.plot(time,memoryLog[1],color = 'blue')
    plt.plot(time,memoryLog[2],color = 'red')
    plt.title("Processed and Downlniked data over time ")
    plt.legend(["Processed","Downlinked"])
    plt.xlabel("time (hr)")
    plt.ylabel("Data (MB)")
    ax = plt.gca()
    #ax.set_xticklabels([])    
    name = path + "/processed_memory.png"
    plt.savefig(name)

def ProObsGraph(ProObsLog,time,path):
    
    # plots the number of processed and observed datasets over time as well as overall memory use
    
    plt.figure(4)
    plt.plot(time, ProObsLog)
    plt.title("Processed and Observations over time")
    plt.xlabel("time (hr)")
    plt.ylabel("number processed/observed datasets")
    plt.legend(["observations", "processed","Downlinked"])
    ax = plt.gca()
    name = path + "/prosObsGraph_memory.png"
    plt.savefig(name)
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
    
    
    
def ProfitGraph(profitability, time,path):
     
    # plots the schedules profitability over time
    
    plt.figure(5)
    plt.plot(time, profitability)
    plt.title("Schedule profit over time")
    plt.xlabel("time (hr)")
    plt.ylabel("profit")
    ax = plt.gca()

    name = path + "/profit_graph.png"
    plt.savefig(name)
    
def detectionsGraph(detections, time,path):
    
    # plots expexted detections against time
    
    plt.figure(6)
    plt.plot(time, detections)
    plt.title("Expected destections over time")
    plt.xlabel("Time (hr)")
    plt.ylabel("Detections")
    ax = plt.gca()
    name = path + "/detections_graph.png"
    plt.savefig(name)
    
    
    
def memoryGraph_compare(memoryLog1,memoryLog2, time,path):
    
    
    
    
    #Creates a plot of the memory used storying observed and processed datasets as well as the total memory use
    plt.figure(2)
    plt.plot(time,memoryLog1[0], color = 'green', linewidth=0.5)
    plt.plot(time,memoryLog1[1], color = 'blue',linewidth=0.5)
    plt.plot(time,memoryLog2[0], color = 'orange',linewidth=0.5)
    plt.plot(time,memoryLog2[1], color = 'red',linewidth=0.5)
    plt.plot(time,memoryLog1[3], color = 'grey', linestyle='dashed',linewidth=0.5)
    plt.title("Storage use over time")
    plt.xlabel("Time (hr)")
    plt.ylabel("memory used (MB)")
    plt.legend(["Observation Data set memory use (optimised)","processed data set memory use(optimised)","Observation Data set memory use (manual)","processed data set memory use(manual)","Max storage"])
    ax = plt.gca()
    #ax.set_xticklabels([])
    name = path + "/unprocessed_memory.png"
    plt.savefig(name)

    plt.figure(3)
    plt.plot(time,memoryLog1[1],color = 'blue')
    plt.plot(time,memoryLog1[2],color = 'red')
    plt.plot(time,memoryLog2[1],color = 'green')
    plt.plot(time,memoryLog2[2],color = 'orange')
    plt.title("Processed and Downlniked data over time ")
    plt.legend(["Processed (optimised)","Downlinked (optimised)","Processed (manual)","Downlinked (manual)"])
    plt.xlabel("time (hr)")
    plt.ylabel("Data (MB)")
    ax = plt.gca()
    #ax.set_xticklabels([])    
    name = path + "/processed_memory.png"
    plt.savefig(name)

def detectionsGraph_compare(detections, time,path):
    
    # plots expexted detections against time
    
    plt.figure(6)
    plt.plot(time, detections[0], color = "red")
    plt.plot(time, detections[1], color = "blue")
    plt.title("Expected destections over time")
    plt.xlabel("Time (hr)")
    plt.ylabel("Detections")
    plt.legend(["optimised", "manual"])
    ax = plt.gca()
    name = path + "/detections_graph.png"
    plt.savefig(name)
    
    
    