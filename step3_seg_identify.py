#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Script to subset a netcdf file based on a list of IDs

import argparse
import xarray as xr
import numpy as np

def process_command_line():
    '''Parse the commandline'''
    parser = argparse.ArgumentParser(description='Script to idenfity the outlet flow gauge index of NHD route links.')
    parser.add_argument('ncfile',
                        help='path of the route/ancillary_data/RouteLink netcdf file.')
    parser.add_argument('comid', 
                        help='COMID of the outlet flow gauge. Obtained by viewing usgs_gauge_conus.shp and Flowline_UCOplus.shp.')
    parser.add_argument('opath',
                        help='output file directory where outlet seg id will be written.')
    args = parser.parse_args()
    return(args)


# main
if __name__ == '__main__':
    
    # An example: python step3_seg_identify.py /glade/u/home/hongli/work/sharp/basins/riogrd/model/route/ancillary_data/RioGrandeRiver_RouteLink__plusHRUs.nc 17906875 /glade/u/home/hongli/work/sharp/basins/scripts/step3_seg_riogrd.txt
    # process command line
    args = process_command_line()

    # ingest the netcdf file
    ds = xr.open_dataset(args.ncfile, decode_times=False)
    link =  ds['link'].values
    seg = np.where(link==int(args.comid))[0]
    
    np.savetxt(args.opath, seg, fmt='%d')
    print('seg index = ', str(seg))
