#!/usr/bin/env python
# Script to subset a netcdf file based on a list of
# reachIDs. Currently this is hardwired for files that
# have seg and hru dimensions (individual variables
# do not have both)

import argparse
from datetime import datetime
import os
import sys
import xarray as xr
import numpy as np

print("\nThe Python version: %s.%s.%s" % sys.version_info[:3])
print(xr.__name__, xr.__version__)

#HARD CODED PARAMETER
segID='link'
hruID='idFeature'
segDim='linkDim'
hruDim='hru'

def process_command_line():
    '''Parse the commandline'''
    parser = argparse.ArgumentParser(description='Script to subset a netcdf file based on a list of IDs.')
    parser.add_argument('innc',
                        help='path of netcdf file that will be subset.')
    parser.add_argument('idfile',
                        help='path of file with list of reach ids.')
    parser.add_argument('outnc',
                        help='directory where subsetted file will be written.')
    # Optional arguments
    parser.add_argument('--remove', action='store_true', default=False,
                        help='Extract or eliminate matching ID' )

    args = parser.parse_args()

    return(args)

if __name__ == '__main__':
    # process command line
    args = process_command_line()

    # read the IDs to subset
    with open(args.idfile) as f:
        ids = [int(x) for x in f]

    # ingest the netcdf file
    ds_org = xr.open_dataset(args.innc)
    print(ds_org)

    # split reach dim data and hru dim data
    ds_hru = ds_org.drop_dims(segDim)
    ds_seg = ds_org.drop_dims(hruDim)

    # subset the netcdf file based on the hruId
    if (args.remove):
      ds_seg_subset = ds_seg.where(np.logical_not(ds_seg[segID].isin(ids)), drop=True)
      ds_hru_subset = ds_hru.where(np.logical_not(ds_hru[hruID].isin(ids)), drop=True)
    else:
      ds_seg_subset = ds_seg.where(ds_seg[segID].isin(ids), drop=True)
      ds_hru_subset = ds_hru.where(ds_hru[hruID].isin(ids), drop=True)

    # merge the hru and seg dimension variables with the result
    ds_subset = xr.merge([ds_seg_subset,ds_hru_subset])

    # update the history attribute
    history = '{}: {}\n'.format(datetime.now().strftime('%c'),
                                ' '.join(sys.argv))
    if 'history' in ds_subset.attrs:
        ds_subset.attrs['history'] = history + ds_subset.attrs['history']
    else:
        ds_subset.attrs['history'] = history

    # Write to file
    ds_subset.to_netcdf(args.outnc)

    # Write IDs from the ID file that were not in the NetCDF file to stdout
    if (args.remove):
      missing = set(ids).intersection(set(ds_subset[segID].values))
    else:
      missing = set(ids).difference(set(ds_subset[segID].values))
    if missing:
        print("Missing IDs: ")
        for x in missing:
            print(x)

