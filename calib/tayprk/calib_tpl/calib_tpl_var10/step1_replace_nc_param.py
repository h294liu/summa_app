# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 12:55:32 2019

@author: hongli
"""
import numpy as np
from netCDF4 import Dataset
from os import path, remove
from shutil import copyfile

#===Modelers need to change this part according to their case study===
param_txtfile_tmp = 'REPLACE_CALIB_DIR/nc_multiplier.tpl'
param_txtfile = 'REPLACE_CALIB_DIR/nc_multiplier.txt'
param_pattern_ncfile = 'REPLACE_CALIB_DIR/trialParams.model_huc12_3hr.v1.nc_pattern'
param_ncfile = 'REPLACE_CALIB_DIR/model/settings/trialParams.model_huc12_3hr.v1.nc'
direct_param_list = ['heightCanopyTop_value']
#===Modelers need to change this part according to their case study===

#read param names in string format
var_names=[]
param_names=[]
with open (param_txtfile_tmp, 'r') as f:
    for line in f:
        line=line.strip()
        if line and not line.startswith('!') and not line.startswith("'"):
            splits=line.split('|')
            if isinstance(splits[1].strip(), str):
                var_names.append(splits[0].strip())
                param_names.append(splits[1].strip())
                
#read new param multiplier values in float format
param_values=[]
with open (param_txtfile, 'r') as f:
    for line in f:
        line=line.strip()
        if line and not line.startswith('!') and not line.startswith("'"):
            splits=line.split('|')
            if splits[0].strip() in var_names:
                param_values.append(float(splits[1].strip()))

## Assume all HRUs share the same multiplier value
if path.exists(param_ncfile):
    remove(param_ncfile)
copyfile(param_pattern_ncfile, param_ncfile)

dataset = Dataset(param_ncfile,'r+')
for i in range(len(var_names)):
    var_name=var_names[i]
    
    if var_name in dataset.variables.keys(): # new_value = multipler * defaul_value
        if not var_name in direct_param_list:
            mask_array=dataset.variables[var_name][:]
            arr_value=mask_array.data * param_values[i]
            dataset.variables[var_name][:]=np.ma.array(arr_value,mask=np.ma.getmask(mask_array),fill_value=mask_array.get_fill_value())
        elif var_name in direct_param_list: # new_value = Ostrich value
            mask_array=dataset.variables[var_name][:]
            arr_value=np.ones_like(mask_array.data) * param_values[i]
            dataset.variables[var_name][:]=np.ma.array(arr_value,mask=np.ma.getmask(mask_array),fill_value=mask_array.get_fill_value())
            
dataset.close() 

