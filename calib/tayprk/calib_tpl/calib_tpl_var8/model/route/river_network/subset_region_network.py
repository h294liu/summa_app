#!/usr/bin/env python

import sys
import re
import numpy as np
import xarray as xr
import pandas as pd

print(xr.__name__, xr.__version__)
print(np.__name__, np.__version__)

region = 'UCOplus'
pfaf_list = 'UCOplus.list'

df_pfaf = pd.read_csv(pfaf_list, header=0, dtype='str')
print(df_pfaf.pfaf)

encoding={'pCode':{'dtype':'S1'},
          'pCode_hru':{'dtype':'S1'}
         }

ncin  = './NHDPlus2/RouteLink_2019_08_13__plusHRUs.nc'
ncout = './%s_RouteLink_2019_08_13__plusHRUs1.nc'%(region)

pcode_name = 'pCode'
pcode_hru_name = 'pCode_hru'

print('\n1. Reading nhdplus pcode data')
ds_pfaf = xr.open_dataset(ncin)
print(ds_pfaf)

print('\n2. Extract pcode array as numpy string array\n')
pfaf_seg = [x.strip() for x in ds_pfaf[pcode_name].values.astype(str)]
pfaf_hru = [x.strip() for x in ds_pfaf[pcode_hru_name].values.astype(str)]

print('\n3. Extract matching reach and hru to regional pfaf code')
idx_seg = np.array([],dtype=int)
idx_hru = np.array([],dtype=int)
for pf in df_pfaf.pfaf:
  print('working on%s'%pf)
  subPfaf_seg = np.array([x[:len(pf)] for x in pfaf_seg])
  subPfaf_hru = np.array([x[:len(pf)] for x in pfaf_hru])

  idx = np.where(subPfaf_seg == pf)
  idx_seg = np.concatenate((idx_seg,idx[0]), axis=0)

  idx = np.where(subPfaf_hru == pf)
  idx_hru = np.concatenate((idx_hru,idx[0]), axis=0)

ds_sub = ds_pfaf.isel(linkDim=idx_seg)
ds_sub = ds_sub.isel(hru=idx_hru)

print(ds_sub)

print('4. Output subset nhdplus pcode data\n')
ds_sub.to_netcdf(ncout, format='NETCDF4', encoding=encoding)
