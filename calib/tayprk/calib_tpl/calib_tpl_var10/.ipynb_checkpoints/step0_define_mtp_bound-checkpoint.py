#!/usr/bin/env python
# coding: utf-8

# determine ostIx.txt multiplier range

import numpy as np
from netCDF4 import Dataset
from os import path, remove
from shutil import copyfile
import time

def read_paramfile(filename):
    var_names = []
    var_min = []
    var_max =[]
    with open (filename, 'r') as f:
        for line in f:
            line=line.strip()
            if line and not line.startswith('!') and not line.startswith("'"):
                splits=line.split('|')
                if isinstance(splits[0].strip(), str):
                    var_names.append(splits[0].strip())
                    var_min.append(str_to_float(splits[2].strip()))
                    var_max.append(str_to_float(splits[3].strip()))
    return var_names, var_min, var_max

def str_to_float(data_str):
    if 'd' in data_str:
        x = data_str.split('d')[0]+'e'+data_str.split('d')[1]
        return float(x)
    else:
        return float(data_str)

#===Modelers need to change this part according to their case study===
param_tpl = 'REPLACE_CALIB_DIR/nc_multiplier.tpl'
trail_param_pattern = 'REPLACE_CALIB_DIR/trialParams.model_huc12_3hr.v1.nc_pattern'
local_param = 'REPLACE_CALIB_DIR/model/settings/localParams.v1.txt'
basin_param = 'REPLACE_CALIB_DIR/model/settings/basinParams.v1.txt'

ostin_tpl = 'REPLACE_CALIB_DIR/ostIn_KGE.tpl'
# ostin_tpl = 'REPLACE_CALIB_DIR/ostIn_RMSE.tpl'

ostin_txt = 'REPLACE_CALIB_DIR/ostIn.txt'
param_min_default = 0.2 # for multiplier
param_max_default = 2 
rand_num_digit=9
#===Modelers need to change this part according to their case study===

#read variable & multiplier names
var_names=[]
param_names=[]
with open (param_tpl, 'r') as f:
    for line in f:
        line=line.strip()
        if line and not line.startswith('!') and not line.startswith("'"):
            splits=line.split('|')
            if isinstance(splits[1].strip(), str):
                var_names.append(splits[0].strip())
                param_names.append(splits[1].strip())

# read variable initial values and get min/max
dataset = Dataset(trail_param_pattern,'r+')
var_ini_range = []
for i in range(len(var_names)):
    var_name = var_names[i]
    param_name = param_names[i]
    
    if not var_name in dataset.variables.keys():
        print(var_name+' is not in TrialParam.nc')
    else:
        mask_array=dataset.variables[var_name][:]
        var_ini_range.append([var_name, param_name, min(mask_array.data), max(mask_array.data)])         
dataset.close()

# read variable range from Local and Basin param files
local_var_names, local_var_min, local_var_max = read_paramfile(local_param)
basin_var_names, basin_var_min, basin_var_max = read_paramfile(basin_param)

# Add constrains to theta-sat min
# theta_sat min needs to be larger than the max initial values of the other four soil parameters. 
if 'theta_sat' in local_var_names:
    index = local_var_names.index('theta_sat')    

    dataset = Dataset(trail_param_pattern,'r+')
    soil_var_names = ['theta_res', 'critSoilWilting', 'critSoilTranspire', 'fieldCapacity']
    soil_var_max = []
    for soil_var_name in soil_var_names:
        soil_mask_array = dataset.variables[soil_var_name][:]
        soil_var_max.append(max(soil_mask_array.data))
    local_var_min[index] = max([local_var_min[index], max(soil_var_max)]) 
    dataset.close()

# Determine min and max for multipliers
param_names = []
param_min = []
param_max = []
for i in range(len(var_ini_range)):
    var_name = var_ini_range[i][0]
    param_name = var_ini_range[i][1]
    var_ini_min = var_ini_range[i][2]
    var_ini_max = var_ini_range[i][3]
    
    if var_name in local_var_names:
        index = local_var_names.index(var_name)
        var_min = local_var_min[index]
        var_max = local_var_max[index]
    elif var_name in basin_var_names:
        index = basin_var_names.index(var_name)
        var_min = basin_var_min[index]
        var_max = basin_var_max[index]
    else:
        var_min = param_min_default
        var_max = param_max_default
        
    param_names.append(param_name) 
    param_min.append(float(var_min)/float(var_ini_min))
    param_max.append(float(var_max)/float(var_ini_max))    
                
# write ostIn.txt
if path.exists(ostin_txt):
    remove(ostin_txt)
    
f_out=open(ostin_txt,'w')
with open(ostin_tpl) as f:
    content= f.readlines()
for line in content:
    line_strip = line.strip()    
    if line_strip and (not (line_strip.startswith('#'))):         
        for i in range(len(param_names)):
            if (param_names[i] in line_strip):
                if 'lwr' in line_strip:
                    line_strip=line_strip.replace('lwr',str(round(param_min[i],4)))
                if 'upr' in line_strip:
                    line_strip=line_strip.replace('upr',str(round(param_max[i],4)))
        if ('xxxxxxxxx' in line_strip):
            t=int(time.time()*(10**rand_num_digit))
            t_cut=t-(int(t/(10**rand_num_digit)))*(10**rand_num_digit)
            line_strip=line_strip.replace('xxxxxxxxx',str(t_cut))
        if ('OstrichWarmStart' in line_strip):
            if path.exists('OstModel0.txt'):
                line_strip = 'OstrichWarmStart yes' # default is no 
    new_line=line_strip+'\n'
    f_out.write(new_line)
f_out.close()
