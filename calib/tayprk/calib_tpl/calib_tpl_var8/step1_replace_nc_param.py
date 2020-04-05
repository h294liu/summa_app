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
#===Modelers need to change this part according to their case study===

#read param names in string format
calib_param_names=[]
with open (param_txtfile_tmp, 'r') as f:
    for line in f:
        line=line.strip()
        if line and not line.startswith('!') and not line.startswith("'"):
            splits=line.split('|')
            if isinstance(splits[1].strip(), str):
                calib_param_names.append(splits[0].strip())

#read new param multiplier values in float format
calib_multipler_values=[]
with open (param_txtfile, 'r') as f:
    for line in f:
        line=line.strip()
        if line and not line.startswith('!') and not line.startswith("'"):
            splits=line.split('|')
            if splits[0].strip() in calib_param_names:
                calib_multipler_values.append(float(splits[1].strip()))
                
## Assume all HRUs share the same multiplier value
if path.exists(param_ncfile):
    remove(param_ncfile)
copyfile(param_pattern_ncfile, param_ncfile)

dataset = Dataset(param_ncfile,'r+')
for i in range(len(calib_param_names)):
    param_name=calib_param_names[i]
    
    if param_name in dataset.variables.keys():
        mask_array=dataset.variables[param_name][:]
        arr_value=mask_array.data * calib_multipler_values[i]
        dataset.variables[param_name][:]=np.ma.array(arr_value, mask=np.ma.getmask(mask_array), 
                         fill_value=mask_array.get_fill_value())
dataset.close() 
