# Solver

Folder containing code for solving the scheduling problem  

- **CPModel_SC.py**  
    contains function CPModel_SC_Data which is used to generate the CP model of the satellite over an interval  
    This can have initil values for the memory if it is continuing from a previous schedule or it can start empty if it is the first scheudle
    
- **CP_SC_tester.py [legacy, use the CP_SC_tester.py in the Strathdar folder]**  
    Contains code which reads in data, runs CPModel_SC.py, solves it, runs post processing functions and then plots the results

- **HintFunctions.py**   
    -Contains functions for generating and adding hints for the CP Solver  
    -CreateManHint: function which uses manual scheduler to create a hint schedule  
    -AddHint: function which takes a hint schedule and adds it as a hint to the CPModel