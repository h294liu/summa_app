# script to make a spatial polygon plot from a shapefile and data
# to run, need python 2.7
# on cheyenne, type:  module load python/2.7.16; ncar_pylib

# set up modules
import sys
import numpy as np

sys.path.append('/glade/u/home/andywood/proj/jtti/scripts/analysis/utils/')
sys.path.append('/glade/work/eriddle/python_eriddle/lib/python2.7/site-packages/')
import plotting_utils
import Nio
import pdb

# variable to plot
plot_var = 'airtemp_mean'
data_tstep = 0    # timestep number to extract from data file

# filenames
data_file = '~/proj/SHARP/wreg/cali_huc12/output/3hr/cali_huc12.3hr.merged.nc'
shp_file  = '/glade/u/home/andywood/proj/SHARP/wreg/WORK/gis/shapes/cali_huc12/CALI_huc12_v5.shp'
plot_file = './'+plot_var+'.png'


# open data file
f = Nio.open_file(data_file)

# order number of attribute in shapefile that matches poly to data index ('datacid')
joinid_index = 20  # starting at 0 for first attribute

# read data
datacid = f.variables['hruId'][:]   # id in the data file that matches the shapes
data    = f.variables[plot_var][data_tstep,:]  # get timestep 0 for all hrus. [time,hru]


# plot data (call function from ./utils/ dir)
plotting_utils.catchment_plot(data, datacid, shp_file, joinid_index, plot_file)

sys.exit(0)
