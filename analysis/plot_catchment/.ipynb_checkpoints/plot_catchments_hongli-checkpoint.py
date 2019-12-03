#!/usr/bin/env python
# coding: utf-8
# Note this cript supports python 2.7 on cheyenne, type: module load python/2.7.16; ncar_pylib (NEED MORE TESTS!)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib as mpl

import sys
sys.path.append('/glade/work/eriddle/python_eriddle/lib/python2.7/site-packages/')
import descartes

import os, argparse
import numpy as np
import pandas as pd
import geopandas as gpd
from netCDF4 import Dataset, num2date 
from datetime import datetime

def process_command_line():
    '''Parse the commandline'''
    parser = argparse.ArgumentParser(description='Script to plot netcdf variables for user specified HUCs, variables, and time period.')
    parser.add_argument('conf_file', help='path of configure file.')
    args = parser.parse_args()
    return(args)

def read_confg_file(conf_file):
    '''Read the configuration file'''
    conf = []
    with open(conf_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('!'):
                conf.append((line.split('!')[0]).strip())
    return conf

if __name__ == '__main__':
    
    # process command line
    args = process_command_line()
    
    # read configuration file
    conf = read_confg_file(args.conf_file) 
    # e.g. conf_file = /glade/u/home/hongli/github/summa_mizuroute_app/analysis/plot_catchment/plot_catchments_config_CALI.txt

    geo_file =  conf[0] 
    nc_file = conf[1]
    output_dir = conf[2]

    var_names = list(map(lambda x: x.strip(), conf[3].split(',')))
    start_time_str = conf[4]
    end_time_str = conf[5]

    GSHHS_coastline = conf[6]
    WDBII_country = conf[7]
    WDBII_state = conf[8]

    # pre-process configuration file
    start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # read research area shapefile 
    print('reading shapefiles and netcdf')
    geo_handle = gpd.read_file(geo_file)
    geo_huc_ids = geo_handle['HUC12'].values

    # read background shapefile
    coastline_bk = gpd.read_file(GSHHS_coastline)
    country_bk = gpd.read_file(WDBII_country)
    state_bk = gpd.read_file(WDBII_state)

    # re-project research area shapefile
    if not (geo_handle.crs == coastline_bk.crs):
        geo_handle.to_crs(coastline_bk.crs)

    # read and subset netcdf based on shapefile hucId and time
    f = Dataset(nc_file)
    hruId = f.variables['hruId'][:]
    time = f.variables['time']
    time = num2date(time[:], time.units)

    hruId_index = list((map(lambda x: str(x) in geo_huc_ids, hruId.data)))
    time_index = list(map(lambda x: (x >= start_time) & (x<= end_time), time))

    hruId_subset = list(map(lambda x: str(x), hruId[hruId_index]))
    time_subset = time[time_index]
    time_subset_str = list(map(lambda x: x.strftime('%Y-%m-%d %H'), time_subset))

    if len(hruId_subset) == 0 or len(time_subset_str) == 0:
        quit('Please provide a valid hurId or time period.')

    var_figs = []
    for var_name in var_names:

        # subset netcdt variable data
        var_value = f.variables[var_name][:]
        var_unit = f.variables[var_name].units

        if var_unit == "K":
            var_value = var_value-273.15  
            var_unit = "$^\circ$C"
            cmap_str = 'jet' #'Reds'
        elif var_unit == "kg m-2 s-1":
            var_value = var_value*24*3600
            var_unit = "mm/d"
            cmap_str = 'jet' #'Blues'
        else:
            cmap_str = 'jet'
        var_subset = var_value[time_index,:][:,hruId_index] #[time, hru]
        var_min = np.amin(var_subset)
        var_max = np.amax(var_subset)

        # construct a dataframe with hruId
        df1 = pd.DataFrame(data={'HUC12': hruId_subset})
        df2 = pd.DataFrame(var_subset.T, columns=time_subset_str)
        var_frame = pd.concat([df1, df2], axis = 1)                

        # join netcdf dataframe with shapefile geo-dataframe (once for each variable)
        geo_subset = geo_handle
        geo_subset = geo_subset.merge(var_frame, on='HUC12')
        xlim = ([geo_subset.total_bounds[0]*1.005, geo_subset.total_bounds[2]*0.995])
        ylim = ([geo_subset.total_bounds[1]*0.99, geo_subset.total_bounds[3]*1.01])

        # plot each time step 
        temp_figs = []  
        for t in time_subset_str:
            temp_fig = var_name+'_'+t+'.png'
            temp_figs.append(temp_fig)
            print('plotting ' + var_name + ' at ' + '{0:%Y-%m-%d %H:%M:%S}'.format(time_subset[time_subset_str.index(t)]))        
#             fig, ax = plt.subplots(figsize=(6,8))
            
            fig = plt.figure(figsize=(6,8))
            ax = fig.add_axes([0.0, 0.0, 1.0, 0.91])            
            ax.set_facecolor('lightskyblue')

            # define plot extent
            ax.set_xlim(xlim)
            ax.set_ylim(ylim)

            # plot background
            plt1 = coastline_bk.plot(color='seashell', edgecolor='grey', linewidth=1.0, ax=ax)
            plt2 = country_bk.plot(color='gray', linewidth=1.5, ax=ax, alpha=.7)
            plt3 = state_bk.plot(color='gray', linewidth=0.75, ax=ax, alpha=.7)

            # plot netcdf variable data
            norm = mpl.colors.Normalize(vmin=var_min,vmax=var_max)
            plt4 = geo_subset.plot(column = t, legend = False, vmin=var_min, vmax=var_max, ax=ax,
                                  cmap = cmap_str, alpha=0.9, edgecolor='grey', linewidth=0.4, label=var_name.capitalize())

            cbar_label = '('+var_unit+')'
            cmap = mpl.cm.ScalarMappable(norm=norm, cmap=cmap_str)
            cmap.set_array([])
            plt.colorbar(cmap, ax=ax, cmap=cmap_str, 
                         orientation='horizontal', label=cbar_label, shrink=0.8, pad=0.07)            
#             plt.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap_str), ax=ax, cmap=cmap_str, 
#                          orientation='horizontal', label=cbar_label, shrink=0.85, pad=0.05)  # inapplicable to python2.          

            ax.tick_params(labeltop=True, labelright=True)
            plt.grid(True, linestyle='--', linewidth=0.5)

            # title
            title_str = var_name.capitalize() + ' at {0:%Y-%m-%d %H:%M:%S}'.format(time_subset[time_subset_str.index(t)])
            fig.suptitle(title_str, fontweight='bold')
            
            # save plot
            fig = plt.gcf()
            fig.savefig(os.path.join(output_dir, temp_fig), dpi=200)
            plt.close(fig)
        del var_value, var_subset, df1, df2, var_frame, geo_subset
    f.close()
    del geo_handle, coastline_bk, country_bk, state_bk
    print('Done')

