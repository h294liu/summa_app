#!/usr/bin/env python
# coding: utf-8

import numpy as np
import datetime
from netCDF4 import Dataset, num2date
import pandas as pd
from calendar import month_abbr

def get_KGE(obs,sim):
    obs = np.asarray(obs)
    sim = np.asarray(sim)
    sim = np.reshape(sim, np.shape(obs))
    
    obs_cal = obs[~np.isnan(obs)]
    sim_cal = sim[~np.isnan(obs)]
    
    sd_sim=np.std(sim_cal, ddof=1)
    sd_obs=np.std(obs_cal, ddof=1)
    
    m_sim=np.mean(sim_cal)
    m_obs=np.mean(obs_cal)
    
    r=(np.corrcoef(sim_cal,obs_cal))[0,1]
    relvar=float(sd_sim)/float(sd_obs)
    bias=float(m_sim)/float(m_obs)
    
    kge=1.0-np.sqrt((r-1)**2 +(relvar-1)**2 + (bias-1)**2)
    return kge

def get_modified_KGE(obs,sim):
    obs = np.asarray(obs)
    sim = np.asarray(sim)
    sim = np.reshape(sim, np.shape(obs))
    
    obs_cal = obs[~np.isnan(obs)]
    sim_cal = sim[~np.isnan(obs)]
    
    sd_sim=np.std(sim_cal, ddof=1)
    sd_obs=np.std(obs_cal, ddof=1)
    
    m_sim=np.mean(sim_cal)
    m_obs=np.mean(obs_cal)
    
    r=(np.corrcoef(sim_cal,obs_cal))[0,1]
    relvar=(float(sd_sim)/float(m_sim))/(float(sd_obs)/float(m_obs))
    bias=float(m_sim)/float(m_obs)
    
    kge=1.0-np.sqrt((r-1)**2 +(relvar-1)**2 + (bias-1)**2)
    return kge

def get_RMSE(obs,sim):
    obs = np.asarray(obs)
    sim = np.asarray(sim)
    sim = np.reshape(sim, np.shape(obs))
    
    obs_cal = obs[~np.isnan(obs)]
    sim_cal = sim[~np.isnan(obs)]
    
    rmse = np.sqrt(np.nanmean(np.power((sim_cal -obs_cal),2)))
    return rmse

def get_mean_error(obs,sim):
    obs = np.asarray(obs)
    sim = np.asarray(sim)
    sim = np.reshape(sim, np.shape(obs))
    
    obs_cal = obs[~np.isnan(obs)]
    sim_cal = sim[~np.isnan(obs)]

    bias_err = np.nanmean(sim_cal - obs_cal)
    abs_err = np.nanmean(np.absolute(sim_cal - obs_cal))
    return bias_err, abs_err

def get_month_mean_flow(obs,sim,sim_time):
    obs = np.asarray(obs)
    sim = np.asarray(sim)
    sim = np.reshape(sim, np.shape(obs))
    
    month = [dt.month for dt in sim_time]

    data = {'sim':sim, 'obs':obs, 'month':month} 
    df = pd.DataFrame(data, index = sim_time)
    
    gdf = df.groupby(['month'])
    sim_month_mean = gdf.aggregate({'sim':np.nanmean})
    obs_month_mean = gdf.aggregate({'obs':np.nanmean})
    return obs_month_mean, sim_month_mean
    
# main script
sim_file='REPLACE_CALIB_DIR/model/route/output/all.nc'
q_vname2 = 'IRFroutedRunoff'
t_vname = 'time'
time_format='%Y-%m-%d'
obs_file='/glade/u/home/hongli/work/sharp/basins/tayprk/analysis/Taylor_park_09107000.txt'
outputfile = 'REPLACE_CALIB_DIR/Diagnostics.txt'

# read simulated flow (m^3/s)
f = Dataset(sim_file)
sim_irf = f.variables[q_vname2][:]
time = f.variables[t_vname]
sim_time = num2date(time[:], time.units)
f.close() 

# read observed flow (f^3/s)
obs = []
obs_time = []
with open(obs_file) as f:
    for line in f:
        line = line.strip()
        if line and line.startswith('USGS'):
            splits = line.split()
            obs_time.append(splits[2])
            if len(splits)>3:#flow data exists
                obs.append(float(splits[3])/35.315) #convert to m^3/s
            else:
                obs.append(np.nan)

# exclude warm-up period (useful time period starts at the second year's Oct. 01 and ends at the last year's Sept. 30 of the simulation period.)
useful_start = datetime.datetime(sim_time[0].year+1, 10, 1, 0, 0, 0) #datetime(year, month, day, hour, minute, second)
useful_end = datetime.datetime(sim_time[-1].year, 9, 30, 0, 0, 0)
useful_len = (useful_end - useful_start).days+1

# extract useful sim flow
sim_start = (useful_start - sim_time[0]).days
sim_useful = sim_irf[sim_start:sim_start+useful_len]
sim_time_useful = sim_time[sim_start:sim_start+useful_len]

# extract useful observed flow
obs_start= (useful_start - datetime.datetime.strptime(obs_time[0],time_format)).days
obs_useful = obs[obs_start:obs_start+useful_len]
         
# calculate diagnostics
# kge = get_KGE(obs=obs_useful, sim=sim_useful)
kge = get_modified_KGE(obs=obs_useful, sim=sim_useful)

# # KGE Log
# #reference:https://wiki.ewater.org.au/display/SD41/Bivariate+Statistics+SRG#BivariateStatisticsSRG-NSEofLogData
# c=max(1,np.percentile(obs_useful, 10)) 
# obs_log=np.log10(obs_useful+c)
# sim_log=np.log10(sim_useful+c)
# kge = get_modified_KGE(obs=obs_log, sim=sim_log)

rmse = get_RMSE(obs=obs_useful, sim=sim_useful)
bias_err, abs_err = get_mean_error(obs=obs_useful, sim=sim_useful)
# obs_month_mean, sim_month_mean = get_month_mean_flow(obs=obs_useful, sim=sim_useful, sim_time=sim_time_useful)

f = open(outputfile, 'w+')
f.write('%.6f' %kge + '\t#KGE\n')
f.write('%.6f' %rmse + '\t#RMSE (cms)\n')
f.write('%.6f' %bias_err + '\t#MBE (cms)\n')
f.write('%.6f' %abs_err + '\t#MAE (cms)\n')
f.close()