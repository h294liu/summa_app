#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import numpy as np

def process_command_line():
    '''Parse the commandline'''
    parser = argparse.ArgumentParser(description='Script to idenfity the index of basin HUC ids among the UPCO HUC id list.')
    parser.add_argument('upco_hucid_file',
                        help='path of the UPCO hucid list file.')
    parser.add_argument('case_hucid_file', 
                        help='path of the case study hucid list file.')
    parser.add_argument('opath',
                        help='output file directory where case study hucid index will be written.')
    args = parser.parse_args()
    return(args)

# main
if __name__ == '__main__':

    # an example: python step2_huc_id_index_upco.py '/glade/u/home/hongli/work/sharp/basins/scripts/huc_id_upco.txt' '/glade/u/home/hongli/work/sharp/basins/scripts/step1_huc_id_riogrd.txt' '/glade/u/home/hongli/work/sharp/basins/scripts/step2_huc_id_index_riogrd.txt'
    
    # process command line
    args = process_command_line()

    # read huc id files
    upco_hucs = list(np.loadtxt(args.upco_hucid_file, dtype='str'))
    case_hucs = list(np.loadtxt(args.case_hucid_file, dtype='str'))

    # identify index
    index = []
    for huc_i in case_hucs:
        index.append(upco_hucs.index(huc_i))

    # save 
    np.savetxt(args.opath, index, fmt='%d')
