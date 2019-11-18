#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import numpy as np
from geopandas import read_file
from sys import exit

def process_command_line():
    '''Parse the commandline'''
    parser = argparse.ArgumentParser(description='Script to idenfity basin HUC ids based on outlet flow gauge HUC id.')
    parser.add_argument('shpfile',
                        help='path of the HUC12 shapefile.')
    parser.add_argument('hucid', 
                        help='HUC12 Id of the outlet flow gauge (in string). Obtained by viewing usgs_gauge_conus.shp and Catchment_UCOplus.shp.')
    parser.add_argument('opath',
                        help='output file directory where basin HUC id will be written.')
    args = parser.parse_args()
    return(args)

def unique(list1):
    list_uniqe = []
    for x in list1:
        if not x in list_uniqe:
            list_uniqe.append(x)
    return list_uniqe

# main
if __name__ == '__main__':

    # an example: python step1_basin_huc_id.py '/glade/u/home/hongli/data/shapefile/upco_huc12_shapefile/UPCO_huc12_v3.shp' '130100011306' '/glade/u/home/hongli/work/sharp/basins/scripts/step1_huc_id_riogrd.txt'
    
    # process command line
    args = process_command_line()
    
    # read HUC12 shapefile
    print('read shapefile')
    data = read_file(args.shpfile)
    if not 'HUC12' in data.columns.values:
        exit('HUC12 column does not exist in shapefile.')
    else:
        hucs = data['HUC12'].values
    if not 'ToHUC' in data.columns.values:
        exit('ToHUC12 column does not exist in shapefile.')
    else:
        tohucs = data['ToHUC'].values

    # search upstream HUCs
    basin_hucs = [args.hucid]
    huc_found = np.unique(hucs[np.where(tohucs==args.hucid)])
    basin_hucs.extend(list(huc_found))
    round_num = 0

    while len(huc_found) != 0:

        round_num = round_num+1
        print("Round %d. Totally %d HUCs are found." % (round_num, len(basin_hucs)))

        # search upstream hucs
        huc_found_next = []
        for huc_i in huc_found:
            huc_found_next.extend(list(hucs[np.where(tohucs==huc_i)]))
        huc_found_next = unique(huc_found_next)

        # identify if found HUC exists in upstrm_hucs
        huc_found = [huc for huc in huc_found_next if not huc in basin_hucs]
        basin_hucs.extend(huc_found)

    # save
    np.savetxt(args.opath, basin_hucs, fmt='%s')
    del data, hucs, tohucs, basin_hucs