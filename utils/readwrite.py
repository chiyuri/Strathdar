# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 12:18:32 2022

@author: iainh

xlsx out from input array and 

"""
import pandas as pd
import openpyxl

def     xlsxOut(data,titles,name,destination):
    
    
    
    ind = [i for i in range(0,len(data))]
    df = pd.DataFrame(data,index = ind, columns = titles)
    
    address = destination + name + ".xlsx"
    df.to_excel(address,sheet_name = "she7et1")
    
    print("succesfully wrote out")


#unfinished
def xlsxAppend(data, titles, name, destination):
    
    
    if fileExitsts == 1:
        
        
        print("Succesfully appended document")
    
    else:
        
        
        print("no document named " + name + "exists, new document made")
    
    

def df_to_xlsxOut(data,titles,name,destination):
    
    address = destination + name + ".xlsx"
    data.to_excel(address,sheet_name = "she7et1")
    
    print("succesfully wrote out")
