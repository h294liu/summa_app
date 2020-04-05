#!/glade/u/home/manab/anaconda3/bin/python

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import xarray as xr
import os
from glob import glob
import numpy as np

ncdir = 'REPLACE_CALIB_DIR/model/output/gmet_huc12_3hr/'
summa_output_24hr='output_output_day.nc'

outfilelist = glob((ncdir+'/output_output_G*_day.nc')) #list of all SUMMA day output files
outfilelist.sort()

# nclist = []  #List for storing the converted SUMMA output files
# for file in outfilelist:
#     ncconvert = xr.open_dataset(file)      
#     ncconvert['hru'].astype(np.int32)
#     nclist.append(ncconvert)
nclist = [xr.open_dataset(file, decode_times=False) for file in outfilelist]
ncconcat = xr.concat(nclist, dim='hru')
ncconcat.to_netcdf(os.path.join(ncdir, summa_output_24hr), 'w')