# -*- coding: utf-8 -*-
"""
Created on Wed Jul 27 10:18:21 2022

@author: iainh
"""

import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.io as pio
pio.renderers.default='svg'


# function for creating Gantt chart from a set of tasks completed at associated times, the time index they are against, and the task names
def ganttChart(df,titles):
    
    fig, ax = plt.subplots(1, figsize = (24,6))
    
    ax.barh(df.action , df.duration, left=df.start)
    fig.show()
    
    """
    fig = px.timeline(df, x_start ="start", x_end = "end", y = "action",color = "action") 
    fig.show()
    #fig.write_image(file="gantt_test", format='png', scale=1, width=2500, height=1250)
    """
    
def memoryGraph(memoryLog, time):
    
    plt.figure(2)
    plt.plot(time,memoryLog)
    plt.title("Storage use over time")
    plt.xlabel("time (s)")
    plt.ylabel("memory used (kB)")
    ax = plt.gca()
    ax.set_xticklabels([])
    
    
def ProObsGraph(ProObsLog,time):
    
    plt.figure(3)
    plt.plot(time, ProObsLog)
    plt.title("Processed and Observations over time")
    plt.xlabel("time (s)")
    plt.ylabel("number processed/observed datasets")
    plt.legend(["observations", "processed","Downlinked"])
    ax = plt.gca()
    ax.set_xticklabels([])
    
    
def downlinkingGraph(downlink, time):
    
    plt.figure(4)
    plt.plot(time, downlink)
    plt.title("downlinking activity over time")
    plt.xlabel("time (s)")
    plt.ylabel("downlinking (y/n)")
    ax = plt.gca()
    ax.set_xticklabels([])