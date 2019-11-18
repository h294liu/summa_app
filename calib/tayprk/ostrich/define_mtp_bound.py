#!/usr/bin/env python
# coding: utf-8

# determine ostIx.txt multiplier range
# determine ostIx.txt multiplier range

import numpy as np
from netCDF4 import Dataset
from os import path, remove
from shutil import copyfile

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
mtp_tpl = 'nc_multiplier.tpl'
trail_param_pattern = 'trialParams.tayprk_huc12.v1.nc_pattern'
local_param = 'model/settings/localParams.v1.txt'
basin_param = 'model/settings/basinParams.v1.txt'
ostin_tmp = 'ostIn.tpl'
ostin_txt = 'ostIn.txt'
mtp_min_default = 0.5
mtp_max_default = 1.5
#===Modelers need to change this part according to their case study===

#read variable & multiplier names
var_names=[]
mtp_names=[]
with open (mtp_tpl, 'r') as f:
    for line in f:
        line=line.strip()
        if line and not line.startswith('!') and not line.startswith("'"):
            splits=line.split('|')
            if isinstance(splits[1].strip(), str):
                var_names.append(splits[0].strip())
                mtp_names.append(splits[1].strip())

# read variable initial values and get min/max
dataset = Dataset(trail_param_pattern,'r+')
var_ini_range = []
for i in range(len(var_names)):
    var_name = var_names[i]
    mtp_name = mtp_names[i]
    
    if not var_name in dataset.variables.keys():
        print(var+' is not in TrialParam.nc')
    else:
        mask_array=dataset.variables[var_name][:]
        var_ini_range.append([var_name, mtp_name, min(mask_array.data), max(mask_array.data)])         
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
mtp_names = []
mtp_min = []
mtp_max = []
for i in range(len(var_ini_range)):
    var_name = var_ini_range[i][0]
    mtp_name = var_ini_range[i][1]
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
        var_min = mtp_min_default
        var_max = mtp_max_default
        
    mtp_names.append(mtp_name) 
    mtp_min.append(float(var_min)/float(var_ini_min))
    mtp_max.append(float(var_max)/float(var_ini_max))    
                
# write ostIn.txt
if path.exists(ostin_txt):
    remove(ostin_txt)
    
f_out=open(ostin_txt,'w')
with open(ostin_tmp) as f:
    content= f.readlines()
for line in content:
    line_strip = line.strip()    
    if line_strip and (not (line_strip.startswith('#'))):         
        for i in range(len(mtp_names)):
            if (mtp_names[i] in line_strip):
                line_strip=line_strip.replace('lwr',str(round(mtp_min[i],4)))
                line_strip=line_strip.replace('upr',str(round(mtp_max[i],4)))
    new_line=line_strip+'\n'
    f_out.write(new_line)
f_out.close()
