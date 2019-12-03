import numpy as np
from collections import defaultdict
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, HOURLY, MONTHLY 
import pdb

def input_filename_def(centerdata,indomain,idate=None,sdate=None,edate=None):
    nomads_dir='/d3/waterworld/nomads/'
    tigge_dir='/d3/waterworld/Tigge/'
    cmc_realtime_dir='/d3/waterworld/cmc_realtime/'
    ecmwf_realtime_dir='/d2/waterworld/ECMWF_realtime'
    pcp0p1deg_dir='/d3/waterworld/'
    nmme_dir='/d3/waterworld/NMME/hindcasts/'
    imerg_dir='/d2/waterworld/imerg/'

    #supply idate for initialization date of a forecast
    #supply sdate and edate for start and end datetimes of observational period that we are interested in
    filedata=[]
    center=centerdata['center_name']
    if  center in ['ecmf','cwao','egrr','kwbc','babj','sbsj','rjtd','lfpw']:
        basedir=tigge_dir+center+'/'
        filename=basedir+idate.strftime('%Y')+'/'+idate.strftime('%Y%m%d%H')\
                +'/'+center+'_'+idate.strftime('%Y%m%d%H')+'_'+indomain[0:-7]+'_accum_pf.grib2'
        filedata.append({'basedir':basedir,'filename':filename,'keys':input_key_def(center)})
    elif  center in ['ecmftmp','cwaotmp','egrrtmp','kwbctmp','babjtmp','sbsjtmp','rjtdtmp','lfpwtmp']:
        centershort=center[0:-3]
        basedir=tigge_dir+centershort+'/'
        filename=basedir+idate.strftime('%Y')+'/'+idate.strftime('%Y%m%d%H')\
                +'/'+centershort+'_'+idate.strftime('%Y%m%d%H')+'_'+indomain[0:-7]+'_inst_pf.grib2'
        filedata.append({'basedir':basedir,'filename':filename,'keys':input_key_def(center)})
    elif center in ['gefs','cmce']:
        basedir=nomads_dir+center+'/'
        filename=basedir+'/'+center+'_'+idate.strftime('%Y%m%d%H')+'_'+indomain+'.nc'
        filedata.append({'basedir':basedir,'filename':filename,'keys':input_key_def(center)})
    elif center in ['cmcRT']:
        basedir=cmc_realtime_dir+center+'/'
        filename=basedir+'/'+center+'_'+idate.strftime('%Y%m%d')+'_'+indomain+'.nc'
        filedata.append({'basedir':basedir,'filename':filename,'keys':input_key_def(center)})
    elif center in ['ecmf3hr']:
        basedir=ecmwf_realtime_dir+'/nc/'
        filename=basedir+'/ecmwf_hires_3hrly_'+idate.strftime('%Y%m%d%H')+'_'+indomain+'.nc'
        filedata.append({'basedir':basedir,'filename':filename,'keys':input_key_def(center)})
    elif center in ['kwbc3hr']:
        basedir=nomads_dir+'/gfs/'
        filename=basedir+'/gfs_'+idate.strftime('%Y%m%d%H')+'_'+indomain+'_acc3h.nc'
        filedata.append({'basedir':basedir,'filename':filename,'keys':input_key_def(center)})
    elif center in ['kwbc1hr']:
        basedir=nomads_dir+'/gfs/'
        filename=basedir+'/gfs_'+idate.strftime('%Y%m%d%H')+'_'+indomain+'_acc1h.nc'
        filedata.append({'basedir':basedir,'filename':filename,'keys':input_key_def(center)})
    elif center in ['ecmfRT']:
        basedir=ecmwf_realtime_dir+'/nc/'
        filename=basedir+'/ecmwf_ens_'+idate.strftime('%Y%m%d%H')+'_'+indomain+'.nc'
        filedata.append({'basedir':basedir,'filename':filename,'keys':input_key_def(center)})
    elif center in ['gefs_raw','cmce_raw']:
        basedir=nomads_dir+center+'/'
        for ei,ens in enumerate(centerdata['enslist']):
            for li,lead in enumerate(centerdata['fcstlist']):
                fname=basedir+ens+'_'+lead+'_'+idate.strftime('%Y%m%d%H')+'.grb2'
                filedata.append({'basedir':basedir,'filename':fname,'ens_i':ei,\
                'lead_i':li,'ens_str':ens,'lead_str':lead,'keys':input_key_def(center,lead=lead,ens=ens)})
    elif center in ['cmcRT_raw']:
        basedir=cmc_realtime_dir+center+'/'
        for li,lead in enumerate(centerdata['fcstlist']):
            fname=basedir+lead+'.grb2'
            filedata.append({'basedir':basedir,'filename':fname,\
            'lead_i':li,'lead_str':lead,'keys':input_key_def(center,lead=lead)})
    elif center in ['gfs_hires_1hrly','gfs_hires_3hrly']:
        basedir=nomads_dir+'/gfs_raw/'
        for li,lead in enumerate(centerdata['fcstlist']):
            fname=basedir+idate.strftime('%Y%m%d%H')+'_'+lead+'.grb2'
            filedata.append({'basedir':basedir,'filename':fname,\
                'ens_i':0,'lead_i':li,'lead_str':lead,'keys':input_key_def(center,lead=lead,li=li)})
    elif center in ['ecmwf_hires_3hrly']:
        basedir=ecmwf_realtime_dir+'/raw/'
        for li,lead in enumerate(centerdata['leads']):
            f=forecast_def(idate,[centerdata['timestep']/24.0,lead/24.0])
            fname=basedir+'B1D'+f['idate'].strftime('%m%d%H')+'00'+f['sdate'].strftime('%m%d%H')+'001.grb'
            filedata.append({'basedir':basedir,'filename':fname,\
                'ens_i':0,'lead_i':li,'lead_str':lead,'keys':input_key_def(center,lead=lead,li=li)})
    elif center in ['ecmwf_ens']:
        basedir=ecmwf_realtime_dir+'/raw/'
        for li,lead in enumerate(centerdata['leads']):
            f=forecast_def(idate,[centerdata['timestep']/24.0,lead/24.0])
            fname=basedir+'B1E'+f['idate'].strftime('%m%d%H')+'00'+f['sdate'].strftime('%m%d%H')+'001.grb'
            filedata.append({'basedir':basedir,'filename':fname,\
                'lead_i':li,'lead_str':lead,'keys':input_key_def(center,lead=lead,li=li)})
    elif center in ['CFSv2','CMC1','CMC2','GFDL','GFDLFLOR1','GFDLFLOR2','NASA','CESM','CCSM4','CPC-CMAP-URD']:
        basedir=nmme_dir+centerdata['long_name']+'/'
        filename=basedir+idate.strftime('%Y')+'/'+idate.strftime('%b')\
            +'-IC_'+idate.strftime('%Y')+'_'+centerdata['long_name']+'_'+indomain+'_prec.nc'
        filedata.append({'basedir':basedir,'filename':filename,'keys':input_key_def(center)})
    elif center in ['trmm','jaxa','merge','cmorph']:
        dshort=indomain.split('_')[0]
        basedir=pcp0p1deg_dir+'/0p1deg_precip_'+center+'/binary/'+dshort+'/'
        acc=centerdata['interval']
        #Get list of files between start and end dates
        if centerdata['timeunit'] in ['hours']:
            if centerdata['filedatedef']=='startaccum':
                alldates=rrule(freq=HOURLY,interval=acc,dtstart=sdate,until=edate-timedelta(hours=acc))
            elif centerdata['filedatedef']=='endaccum':
                alldates=rrule(freq=HOURLY,interval=acc,dtstart=sdate+timedelta(hours=acc),until=edate)
            elif centerdata['filedatedef']=='midaccum':
                alldates=rrule(freq=HOURLY,interval=acc,dtstart=sdate,until=edate)
        for date in alldates:
            fname=basedir+date.strftime('%Y')+'/'+date.strftime('%Y%m')+'/0p1deg_precip_'+center+'_'\
		+dshort+"_"+date.strftime('%Y%m%d%H')+".bin.dat"
            filedata.append({'basedir':basedir,'filename':fname,'keys':input_key_def(center)})
    elif center in ['CENTRENDS']:
        basedir=nmme_dir+'/CENTRENDS/'
        filename=basedir+'CenTrends_v1_monthly.nc'
        filedata.append({'basedir':basedir,'filename':filename,'keys':input_key_def(center)})
    elif center in ['imerg_raw_archive']:
        basedir=imerg_dir+'/raw/'
        filename=basedir+'imergF_'+sdate.strftime('%Y%m%d')+'.nc4'
        filedata.append({'basedir':basedir,'filename':filename,'keys':input_key_def(center)})
    elif center in ['imerg_raw_realtime']:
        basedir=imerg_dir+'/raw/'
        filename=basedir+'imergL_'+sdate.strftime('%Y%m%d')+'.nc4'
        filedata.append({'basedir':basedir,'filename':filename,'keys':input_key_def(center)})
    elif center in ['imerg']:
        basedir=imerg_dir
        filename=basedir+sdate.strftime('%Y')+'/'+'imerg_pcp_daily_'+indomain+'_'+sdate.strftime('%Y%m%d')+'.nc'
        filedata.append({'basedir':basedir,'filename':filename,'keys':input_key_def(center)})
    return filedata

def load_correspondence_file(longgridname,longbasinname):
    cf_fn='Correspondence_Files/cf_'+longgridname+'_to_'+longbasinname+'.npz'
    cf=np.load(cf_fn)
    return cf

def get_cf_grid(outname,center):
    #look up grid of correspondence file for a given basin and a given center
    resolution=center_def(center)['resolution']
    if outname in ['sudan_z1','sudan_z2','ea_z1','ea_z2','blue_nile','white_nile','whole_nile','Sudan_delineations','east_africa_0p5deg']:
        if resolution < 0.49:
            cfgrid='east_africa_0p1deg'
        else:
            cfgrid='east_africa_0p5deg'
    elif outname in ['ethiopia_z1','ethiopia_z2']:
        if resolution < 0.49:
            cfgrid='ethiopia_0p1deg'
        else:
            cfgrid='ethiopia_0p5deg'
    elif outname in ['gbm_z1','gbm_z2','bihar_z1','bihar_z2','gbm_gage','bihar_0p5deg','bihar_0p1deg','assam_0p1deg','dudhnoi_0p1deg','digaru_0p1deg','dikhow_0p1deg','gbm_0p5deg','BagmatiAdhwara_z1','BagmatiAdhwara_z2','Rapti','KRB_SBU','BagmatiRMSI']:
        if resolution < 0.49:
            cfgrid='gbm_0p1deg'
        else:
            cfgrid='gbm_0p5deg'
    elif outname in ['nepal_points']:
        #Nepal data needs to be interpolated to 0.1 degree first
        cfgrid='gbm_0p1deg'
    elif outname in ['periyar','kerala_0p1deg','kerala_0p5deg']:
        if resolution < 0.49:
            cfgrid='kerala_0p1deg'
        else:
            cfgrid='kerala_0p5deg'
    else:
        print 'Unrecognied basin name'
        cfgrid=None
    return cfgrid

def get_input_grid(outname,center):
    #look up grid of input file for a given basin and a given center
    if center in ['CENTRENDS']:
        if outname in ['ethiopia_z1','ethiopia_z2','blue_nile']:
            ingrid='horn_afr_0p1deg'
        else:
            print 'Basin not available for this dataset'
            ingrid=None
    elif center in ['imerg_raw_archive','imerg_raw_realtime']:
        if outname in ['ethiopia_z1','ethiopia_z2','sudan_z1','sudan_z2','ea_z1','ea_z2','blue_nile','white_nile','whole_nile','Sudan_delineations',\
                'gbm_z1','bihar_z1','bihar_z2','nepal_points','gbm_z2','gbm_gage','bihar_0p5deg','bihar_0p1deg','assam_0p1deg','dudhnoi_0p1deg','digaru_0p1deg','dikhow_0p1deg','east_africa_0p5deg','gbm_0p5deg','BagmatiAdhwara_z1',\
                'BagmatiAdhwara_z2','Rapti','KRB_SBU','BagmatiRMSI']:
            ingrid='global_0p1deg'
        else:
            print 'Basin not available or this dataset'
            ingrid=None
    elif center in ['CFSv2','CMC1','CMC2','GFDL','GFDLFLOR1','GFDLFLOR2','NASA','CESM','CCSM4','CPC-CMAP-URD']:
        if outname in ['ethiopia_z1','ethiopia_z2','sudan_z1','sudan_z2','ea_z1','ea_z2','blue_nile','white_nile','whole_nile','Sudan_delineations',\
                'gbm_z1','gbm_z2','bihar_z1','bihar_z2','gbm_gage','bihar_0p5deg','bihar_0p1deg','assam_0p1deg','dudhnoi_0p1deg','digaru_0p1deg','dikhow_0p1deg','east_africa_0p5deg','gbm_0p5deg','BagmatiAdhwara_z1',\
                'nepal_points','BagmatiAdhwara_z2','Rapti','KRB_SBU','BagmatiRMSI']:
            ingrid='afr_india_1deg'
        else:
            print 'Basin not available or this dataset'
            ingrid=None
    elif center in ['trmm','jaxa','merge','cmorph']:
        if outname in ['ethiopia_z1','ethiopia_z2','sudan_z1','sudan_z2','ea_z1','ea_z2','blue_nile','white_nile','whole_nile','Sudan_delineations','east_africa_0p5deg']:
            ingrid='africa_0p1deg'
        elif outname in ['gbm_z1','gbm_z2','bihar_z1','bihar_z2','nepal_points','gbm_gage','gbm_0p5deg','bihar_0p1deg','assam_0p1deg','dudhnoi_0p1deg','digaru_0p1deg','dikhow_0p1deg','bihar_0p5deg','BagmatiAdhwara_z1','BagmatiAdhwara_z2','Rapti','KRB_SBU','BagmatiRMSI']:
            ingrid='gbm_0p1deg'
        elif outname in ['kerala_0p1deg','kerala_0p5deg','periyar']:
            ingrid='kerala_0p1deg'
        else:
            print 'Basin not available for this dataset'
            ingrid=None
    elif center in ['ecmf','cwao','egrr','kwbc','babj','sbsj','rjtd','lfpw','ecmftmp','cwaotmp','egrrtmp','kwbctmp','babjtmp','sbsjtmp','rjtdtmp','lfpwtmp']:
        if outname in ['ethiopia_z1','ethiopia_z2','sudan_z1','sudan_z2','ea_z1','ea_z2','blue_nile','white_nile','whole_nile','Sudan_delineations','east_africa_0p5deg']:
            ingrid='africa_0p5deg'
        elif outname in ['gbm_z1','gbm_z2','bihar_z1','bihar_z2','nepal_points','gbm_gage','gbm_0p5deg','bihar_0p5deg','bihar_0p1deg','assam_0p1deg','dudhnoi_0p1deg','digaru_0p1deg','dikhow_0p1deg','BagmatiAdhwara_z1','BagmatiAdhwara_z2','Rapti','KRB_SBU','BagmatiRMSI']:
            ingrid='gbm_0p5deg'
        elif outname in ['kerala_0p1deg','kerala_0p5deg','periyar']:
            ingrid='kerala_0p5deg'
        else:
            print 'Basin not available for this dataset'
            ingrid=None
    elif center in ['cmce','gefs','cmcRT']:
        if outname in ['ethiopia_z1','ethiopia_z2','sudan_z1','sudan_z2','ea_z1','ea_z2','blue_nile',\
                'white_nile','whole_nile','Sudan_delineations','east_africa_0p5deg']:
            ingrid='east_africa_0p5deg'
        elif outname in ['gbm_z1','gbm_z2','bihar_z1','bihar_z2','nepal_points','gbm_gage',\
                'bihar_0p5deg','bihar_0p1deg','assam_0p1deg','dudhnoi_0p1deg','digaru_0p1deg','dikhow_0p1deg',\
                'gbm_0p5deg','BagmatiAdhwara_z1','BagmatiAdhwara_z2','Rapti','KRB_SBU','BagmatiRMSI']:
            ingrid='gbm_0p5deg'
        else:
            print 'Basin not available for this dataset'
            ingrid=None
    elif center in ['ecmfRT']:
        if outname in ['gbm_z1','gbm_z2','bihar_z1','bihar_z2','nepal_points','gbm_gage',\
                'bihar_0p5deg','bihar_0p1deg','assam_0p1deg','dudhnoi_0p1deg','digaru_0p1deg','dikhow_0p1deg',\
                'gbm_0p5deg','BagmatiAdhwara_z1','BagmatiAdhwara_z2','Rapti','KRB_SBU','BagmatiRMSI']:
            ingrid='gbm_0p5deg'
        else:
            print 'Basin not available for this dataset'
            ingrid=None
    elif center in ['kwbc3hr','kwbc1hr','ecmf3hr']:
        if outname in ['gbm_z1','gbm_z2','bihar_z1','bihar_z2','nepal_points','gbm_gage',\
                'bihar_0p5deg','bihar_0p1deg','assam_0p1deg','dudhnoi_0p1deg','digaru_0p1deg','dikhow_0p1deg',\
                'gbm_0p5deg','BagmatiAdhwara_z1','BagmatiAdhwara_z2','Rapti','KRB_SBU','BagmatiRMSI']:
            ingrid='gbm_0p1degv2'
        else:
            print 'Basin not available for this dataset'
            ingrid=None

    else: 
        print 'Center not available'
        ingrid=None
    return ingrid

def get_grid_dict(outputlist,center):
    #defines correspondence between the basin list, ingrids(input grids) and cfgrids(correspondence file grids)
    #input is the input basinlist and the center
    #output is a nested dictionary with entries showing the input grids -> cf grids (for that input grid) -> basins (for that cf grid)
    c=center_def(center)
    grid_dict=defaultdict(lambda:'No Key')
    for b in outputlist:
        cfgrid=get_cf_grid(b,center)
        ingrid=get_input_grid(b,center)
        if ingrid not in grid_dict:
            grid_dict[ingrid]=defaultdict(lambda:'No Key')
        if cfgrid not in grid_dict[ingrid]:
            grid_dict[ingrid][cfgrid]=[b]
        else:
            grid_dict[ingrid][cfgrid].append(b)
    return grid_dict

def catchment_def(catchname):
    #Defines catchments that are used in the analysis
    catchments=\
        {'ethiopia_z1':\
            {'ethiopia_0p5deg':'Correspondence_Files/cf_ethiopia_griddat_0p5deg_to_ethiopia_basins.npz',\
            'ethiopia_0p1deg':'Correspondence_Files/cf_ethiopia_griddat_0p1deg_to_ethiopia_basins.npz',\
            'ncatch':12,'shapefile':'shapefiles/river_basins_eth.shp','joinid_index':0},\
         'ethiopia_z2':\
            {'ethiopia_0p5deg':'Correspondence_Files/cf_ethiopia_griddat_0p5deg_to_omo_gibe_delineations.npz',\
            'ethiopia_0p1deg':'Correspondence_Files/cf_ethiopia_griddat_0p1deg_to_omo_gibe_delineations.npz',\
            'ncatch':16,'shapefile':'shapefile/Wsheds_Snap0.shp','joinid_index':0},\
         'ea_z1':\
            {'east_africa_0p5deg':'Correspondence_Files/cf_east_africa_griddat_0p5deg_to_hydroBASINS_level4.npz',\
             'east_africa_0p1deg':'Correspondence_Files/cf_east_africa_griddat_0p1deg_to_hydroBASINS_level4.npz',\
             'ncatch':83,'shapefile':'shapefile/hybas_af_lev04_v1c_EA','joinid_index':0},\
         'ea_z2':\
            {'east_africa_0p5deg':'Correspondence_Files/cf_east_africa_griddat_0p5deg_to_hydroBASINS_level6.npz',\
             'east_africa_0p1deg':'Correspondence_Files/cf_east_africa_griddat_0p1deg_to_hydroBASINS_level6.npz',\
             'ncatch':1527,'shapefile':'shapefiles/hybas_af_lev06_v1c_EA','joinid_index':8},\
         'sudan_z1':\
            {'east_africa_0p5deg':'Correspondence_Files/cf_east_africa_0p5deg_to_sudan_z1.npz',\
             'east_africa_0p1deg':'Correspondence_Files/cf_east_africa_0p1deg_to_sudan_z1.npz',\
             'ncatch':1,'shapefile':'shapefiles/smallBlueNile','joinid_index':8},\
         'sudan_z2':\
            {'east_africa_0p5deg':'Correspondence_Files/cf_east_africa_0p5deg_to_sudan_z2.npz',\
             'east_africa_0p1deg':'Correspondence_Files/cf_east_africa_0p1deg_to_sudan_z2.npz',\
             'ncatch':29,'shapefile':'shapefiles/deim_subbasin','joinid_index':8},\
         'sudan_dilineations':\
            {'east_africa_0p5deg':'Correspondence_Files/cf_east_africa_griddat_0p5deg_to_Sudan_delineations.npz',\
             'east_africa_0p1deg':'Correspondence_Files/cf_east_africa_griddat_0p1deg_to_Sudan_delineations.npz',\
             'ncatch':6,'shapefile':'shapefiles/watershed_polygons.shp','joinid_index':0},\
         'whole_nile':\
             {'east_africa_0p5deg':'Correspondence_Files/cf_east_africa_griddat_0p5deg_to_Nile.npz',\
             'east_africa_0p1deg':'Correspondence_Files/cf_east_africa_griddat_0p1deg_to_Nile.npz',\
             'ncatch':1,'shapefile':'shapefiles/Nile_Pfaf3_172_erase','joinid_index':0},\
         'blue_nile':\
             {'east_africa_0p5deg':'Correspondence_Files/cf_east_africa_griddat_0p5deg_to_Blue_Nile.npz',\
             'east_africa_0p1deg':'Correspondence_Files/cf_east_africa_griddat_0p1deg_to_Blue_Nile.npz',\
             'ncatch':1,'shapefile':'shapefiles/Blue_Nile_Pfaf4_1724','joinid_index':0},\
         'white_nile':\
             {'east_africa_0p5deg':'Correspondence_Files/cf_east_africa_griddat_0p5deg_to_White_Nile.npz',\
             'east_africa_0p1deg':'Correspondence_Files/cf_east_africa_griddat_0p1deg_to_White_Nile.npz',\
             'ncatch':1,'shapefile':'shapefiles/White_Nile_Pfaf4_dissolve_erase','joinid_index':0},\
         'gbm_z1':\
             {'gbm_0p5deg':'Correspondence_Files/cf_gbm_griddat_0p5deg_to_GBM_Major_Catchments.npz',\
             'gbm_0p1deg':'Correspondence_Files/cf_gbm_griddat_0p1deg_to_GBM_Major_Catchments.npz',\
             'ncatch':28,'shapefile':'shapefiles/GBM_Major_Sub','joinid_index':3},\
         'gbm_z2':\
             {'gbm_0p5deg':'Correspondence_Files/cf_gbm_griddat_0p5deg_to_GBM_Subcatchments.npz',\
             'gbm_0p1deg':'Correspondence_Files/cf_gbm_griddat_0p1deg_to_GBM_Subcatchments.npz',\
             'ncatch':4696,'shapefile':'shapefiles/Catchments_GBM','joinid_index':0},\
         'bihar_z1':\
             {'gbm_0p5deg':'Correspondence_Files/cf_gbm_griddat_0p5deg_to_GBM_Major_Catchments.npz',\
             'gbm_0p1deg':'Correspondence_Files/cf_gbm_griddat_0p1deg_to_GBM_Major_Catchments.npz',\
             'ncatch':28,'shapefile':'shapefiles/GBM_Major_Sub','joinid_index':3},\
         'bihar_z2':\
             {'gbm_0p5deg':'Correspondence_Files/cf_gbm_griddat_0p5deg_to_bihar_z2.npz',\
             'gbm_0p1deg':'Correspondence_Files/cf_gbm_griddat_0p1deg_to_bihar_z2.npz',\
             'ncatch':23,'shapefile':'shapefiles/Basin_bih_np_UTM','joinid_index':0},\
         'gbm_gage':\
             {'gbm_0p5deg':'Correspondence_Files/cf_gbm_griddat_0p5deg_to_gaged_catchments.npz',\
             'gbm_0p1deg':'Correspondence_Files/cf_gbm_griddat_0p1deg_to_gaged_catchments.npz',\
             'ncatch':360,'shapefile':'shapefiles/All_Stations_Wsheds_2016_02_02','joinid_index':0},\
         'nepal_points':\
             {'gbm_0p5deg':'Correspondence_Files/cf_gbm_griddat_0p5deg_to_nepal_points.npz',\
             'gbm_0p1deg':'Correspondence_Files/cf_gbm_griddat_0p1deg_to_nepal_points.npz',\
             'ncatch':525,'shapefile':'shapefiles/All_Stations_Wsheds_2016_02_02','joinid_index':0},\
         'periyar':\
             {'kerala_0p5deg':'Correspondence_Files/cf_kerala_griddat_0p5deg_to_periyar.npz',\
             'kerala_0p1deg':'Correspondence_Files/cf_kerala_griddat_0p1deg_to_periyar.npz',\
             'ncatch':1,'shapefile':'shapefiles/All_Stations_Wsheds_2016_02_02','joinid_index':0},\
         'BagmatiAdhwara_z1':\
             {'gbm_0p5deg':'Correspondence_Files/cf_gbm_griddat_0p5deg_to_Bagmati-Adhwara_catch_boundary_region.npz',\
             'gbm_0p1deg':'Correspondence_Files/cf_gbm_griddat_0p1deg_to_Bagmati-Adhwara_catch_boundary_region.npz',\
             'ncatch':1,'shapefile':'shapefiles/Bagmati-Adhwara_catchment_boundary_region','joinid_index':0},\
         'BagmatiAdhwara_z2':\
             {'gbm_0p5deg':'Correspondence_Files/cf_gbm_griddat_0p5deg_to_Bagmati-Adhwara_rain_regions_v1.npz',\
             'gbm_0p1deg':'Correspondence_Files/cf_gbm_griddat_0p1deg_to_Bagmati-Adhwara_rain_regions_v1.npz',\
             'ncatch':7,'shapefile':'shapefiles/Bagmati-Adhwara_rain_regions_v1_region','joinid_index':4},\
         'BagmatiRMSI':\
             {'gbm_0p5deg':'Correspondence_Files/cf_gbm_griddat_0p5deg_to_Sub_basin_Bagmati.npz',\
             'gbm_0p1deg':'Correspondence_Files/cf_gbm_griddat_0p1deg_to_Sub_basin_Bagmati.npz',\
             'ncatch':19,'shapefile':'shapefiles/Bagmati','joinid_index':3},\
         'Rapti':\
             {'gbm_0p5deg':'Correspondence_Files/cf_gbm_griddat_0p5deg_to_Subbasin195.npz',\
             'gbm_0p1deg':'Correspondence_Files/cf_gbm_griddat_0p1deg_to_Subbasin195.npz',\
             'ncatch':31,'shapefile':'shapefiles/Rapti','joinid_index':0},\
         'KRB_SBU':\
             {'gbm_0p5deg':'Correspondence_Files/cf_gbm_griddat_0p5deg_to_KRB_SBU_17Feb2018.npz',\
             'gbm_0p1deg':'Correspondence_Files/cf_gbm_griddat_0p1deg_to_KRB_SBU_17Feb2018.npz',\
             'ncatch':92,'shapefile':'shapefiles/KRB_SBU_17Feb2018','joinid_index':1}}
             
    if catchname in catchments:
        return catchments[catchname] 
    else:
        print 'Catchment name not defined'
        return None

def grid_def(gridname):
    #Defines grids that are used in the analysis
    grids={'ethiopia_0p1deg':\
                {'lats':np.linspace(2.05,14.95,130,endpoint=True),\
                'lons':np.linspace(33.05,47.95,150,endpoint=True),\
                'nlats':130,\
                'nlons':150},\
            'ethiopia_0p5deg':\
                {'lats':np.linspace(2,15,27,endpoint=True),\
                'lons':np.linspace(33,48,31,endpoint=True),\
                'nlats':27,\
                'nlons':31},\
            'east_africa_0p1deg':\
                {'lats':np.linspace(-13.95,33.95,480,endpoint=True),\
                 'lons':np.linspace(14.05,54.95,410,endpoint=True),\
                 'nlats':480,\
                 'nlons':410},\
            'east_africa_0p5deg':\
                 {'lats':np.linspace(-14,34,97,endpoint=True),\
                 'lons':np.linspace(14,55,83,endpoint=True),\
                 'nlats':97,\
                 'nlons':83},\
            'gbm_0p1deg':\
                {'lats':np.linspace(22.05,31.95,100,endpoint=True),\
                 'lons':np.linspace(73.05,97.95,250,endpoint=True),\
                 'nlats':100,\
                 'nlons':250},\
            'gbm_0p1degv2':\
                {'lats':np.linspace(22,32,101,endpoint=True),\
                 'lons':np.linspace(73,98,251,endpoint=True),\
                 'nlats':101,\
                 'nlons':251},\
            'gbm_0p5deg':\
                {'lats':np.linspace(22,32,21,endpoint=True),\
                 'lons':np.linspace(73,98,51,endpoint=True),\
                 'nlats':21,\
                 'nlons':51},\
            'africa_0p1deg':\
                {'lats':np.linspace(-39.95,39.95,800,endpoint=True),\
                 'lons':np.linspace(-19.95,54.95,750,endpoint=True),\
                 'nlats':800,\
                 'nlons':750},\
            'africa_0p5deg':\
                {'lats':np.linspace(-40,40,161,endpoint=True),\
                 'lons':np.linspace(-20,55,151,endpoint=True),\
                 'nlats':161,\
                 'nlons':151},\
            'bihar_0p5deg':\
                {'lats':np.linspace(22,32,21,endpoint=True),\
                 'lons':np.linspace(81,91,21,endpoint=True),\
                 'nlats':21,\
                 'nlons':21},\
            'global_1deg':\
                {'lats':np.linspace(-90,90,181,endpoint=True),\
                 'lons':np.linspace(0,359,360,endpoint=True),\
                 'nlats':181,\
                 'nlons':360},\
            'global_0p5deg':\
                {'lats':np.linspace(-90,90,361,endpoint=True),\
                 'lons':np.linspace(0,359.5,720,endpoint=True),\
                 'nlats':361,\
                 'nlons':720},\
            'global_0p1deg':\
                {'lats':np.linspace(-89.95,89.95,1800,endpoint=True),\
                 'lons':np.linspace(-179.95,179.95,3600,endpoint=True),\
                 'nlats':181,\
                 'nlons':360},\
            'afr_india_1deg':\
                {'lats':np.linspace(-40,40,81,endpoint=True),\
                 'lons':np.linspace(-20,100,121,endpoint=True),\
                 'nlats':81,\
                 'nlons':121},\
            'assam_0p1deg':\
                {'lats':np.linspace(25.5,27.0,16,endpoint=True),\
                 'lons':np.linspace(90.5,95.5,51,endpoint=True),\
                 'nlats':16,\
                 'nlons':51},\
            'bihar_0p1deg':\
                {'lats':np.linspace(22,32,101,endpoint=True),\
                 'lons':np.linspace(81,91,101,endpoint=True),\
                 'nlats':101,\
                 'nlons':101},\
            'digaru_0p1deg':\
                {'lats':np.linspace(25.5,26.3,9,endpoint=True),\
                 'lons':np.linspace(91.5,92.3,9,endpoint=True),\
                 'nlats':9,\
                 'nlons':9},\
            'dikhow_0p1deg':\
                {'lats':np.linspace(26.0,27.0,11,endpoint=True),\
                 'lons':np.linspace(94.4,95.3,10,endpoint=True),\
                 'nlats':11,\
                 'nlons':10},\
            'dudhnoi_0p1deg':\
                {'lats':np.linspace(25.5,26.0,6,endpoint=True),\
                 'lons':np.linspace(90.6,91.4,9,endpoint=True),\
                 'nlats':6,\
                 'nlons':9},\
            'horn_afr_0p1deg':\
                {'lats':np.linspace(-15,18,331,endpoint=True),\
                 'lons':np.linspace(28,54,261,endpoint=True),\
                 'nlats':331,\
                 'nlons':261},\
            'kerala_0p1deg':\
                {'lats':np.linspace(8.05,12.95,50,endpoint=True),\
                 'lons':np.linspace(74.05,77.95,40,endpoint=True),\
                 'nlats':50,\
                 'nlons':40},\
            'kerala_0p5deg':\
                {'lats':np.linspace(8,13,11,endpoint=True),\
                 'lons':np.linspace(74,78,9,endpoint=True),\
                 'nlats':11,\
                 'nlons':9},\
            'global_0p24deg':\
                {'lats':np.linspace(-90,90,751,endpoint=True),\
                 'lons':np.linspace(0,359.76,1500,endpoint=True),\
                 'nlats':751,\
                 'nlons':1500},\
            'global_0p25deg':\
                {'lats':np.linspace(-90,90,721,endpoint=True),\
                 'lons':np.linspace(0,359.75,1440,endpoint=True),\
                 'nlats':721,\
                 'nlons':1440}}
                
    if gridname in grids:
        return grids[gridname] 
    else:
        print 'Grid name not defined'
        return None
                                            
def avgper2str(avgper):
    #Takes a relativedelta object and returns string giving the averaging period
    if avgper == relativedelta(hours=+6):
        avgperstr='6h'
    elif avgper == relativedelta(days=+1):
        avgperstr='24h'
    elif avgper == relativedelta(days=+5):
        avgperstr='5d'
    elif avgper == relativedelta(months=+1):
        avgperstr='1mo'
    elif avgper == relativedelta(months=+3):
        avgperstr='3mo'
    else:
        print 'Unexpected averaging period'
        avgperstr='Unknown'
    return avgperstr

def forecast_def_old(idn,fdat,fcsthr):
        aper=timedelta(days=fdat[0])
        lead=timedelta(days=fdat[1])
        if fcsthr>0:
                hr=timedelta(hours=24-fcsthr)
        else:
                hr=timedelta(hours=0)
        sdn=idn+lead+hr
        edn=idn+lead+aper+hr
        hrs=aper.total_seconds()//3600
        dys=aper.total_seconds()//(24*3600)
        if hrs<0:
                print 'averaging time less than zero'
        elif dys<=1:
                acctime='acc'+str(int(hrs))+'h'
                leadstr='d'+str(fdat[1])
        elif dys>1:
                acctime='acc'+str(int(dys))+'d'
                leadstr='d'+str(fdat[1])+'to'+str(fdat[1]+fdat[0]-1)
        data={'idate':idn,'edate':edn,'sdate':sdn,'accstr':acctime,'lead':lead,'acc':aper,'leadstr':leadstr}
        return data

def forecast_def(idn,fdat,timescale='medium_range'):
        if timescale in ['medium_range']:
            aper=timedelta(days=fdat[0])
            lead=timedelta(days=fdat[1])
            sdn=idn+lead
            edn=idn+lead+aper
            hrs=aper.total_seconds()//3600
            dys=aper.total_seconds()//(24*3600)
            if hrs<0:
                    print 'averaging time less than zero' 	
            elif dys<=1:
                    acctime='acc'+str(int(hrs))+'h'
                    leadstr='d'+str(fdat[1])
            elif dys>1:
                    acctime='acc'+str(int(dys))+'d' 
                    leadstr='d'+str(fdat[1])+'to'+str(fdat[1]+fdat[0]-1)
        elif timescale in ['seasonal']:
            aper=fdat[0]
            lead=fdat[1]
            sdn=idn+relativedelta(months=lead)
            edn=idn+relativedelta(months=lead+aper)
            acctime='acc'+str(aper)+'m'
            if aper==1:
                leadstr='m'+str(lead)
            elif aper>1:
                leadstr='m'+str(lead)+'to'+str(aper+lead-1)
            aper=edn-sdn
            lead=sdn-idn
        data={'idate':idn,'edate':edn,'sdate':sdn,'accstr':acctime,'lead':lead,'acc':aper,'leadstr':leadstr}
        return data

def obs_time_def(idate,aper):
        #idate is the reference date which is the same as the end of the averaging period
	aper=timedelta(days=aper)
        sdate=idate-aper
	edate=idate
        hrs=aper.total_seconds()//3600
        dys=aper.total_seconds()//(24*3600)
        if hrs<0:
		print 'averaging time less than zero' 	
        elif dys<=1:
        	acctime='acc'+str(int(hrs))+'h'
        elif dys>1:
		acctime='acc'+str(int(dys))+'d' 
	data={'idate':idate,'edate':edate,'sdate':sdate,'accstr':acctime,'acc':aper}
        return data


#def center_def():
#        center={'tigge':\
#                        {'ecmf':{'nens':50,'ntime':60},\
#                         'cwao':{'nens':20,'ntime':60},\
#                         'egrr':{'nens':11,'ntime':10},\
#                         'kwbc':{'nens':20,'ntime':60},\
#                         'babj':{'nens':14,'ntime':60},\
#                         'lfpw':{'nens':34},'ntime':60},\
#                         'rjtd':{'nens':26},'ntime':60},\
#                         'sbsj':{'nens':14},'ntime':60},\
#			 '
#                'nmme':\
#                        {'CFSv2':{'longname':'NCEP-CFSv2','nens':32},\
#                         'CMC1':{'longname':'CMC1-CanCM3','nens':10},\
#                         'CMC2':{'longname':'CMC2-CanCM4','nens':10},\
#                         'GFDL':{'longname':'GFDL-CM2p1-aer04','nens':10},\
#                         'GFDLFLOR1':{'longname':'GFDL-CM2p5-FLOR-A06','nens':12},\
#                         'GFDLFLOR2':{'longname':'GFDL-CM2p5-FLOR-B01','nens':12},\
#                         'NASA':{'longname':'NASA-GMAO-062012','nens':12},\
#                         'NCARCCSM4':{'longname':'COLA-RSMAS-CCSM4','nens':10},\
#                         'NCARCESM':{'longname':'NCAR-CESM1','nens':10}},
#		'ncep':\
#			{'gefs':{'
def input_key_def(center,ens=None,lead=None,li=None):
    if  center in ['ecmf','cwao','egrr','kwbc','babj','sbsj','rjtd']:
        keys={'lonkey':'lon_0','latkey':'lat_0','leadkey':'forecast_time0','enskey':'ensemble0','varkey':'tp_P11_L1_GLL0_acc'}
    elif center in ['lfpw']: 
        keys={'lonkey':'lon_0','latkey':'lat_0','leadkey':'forecast_time0'}
        keys['varkeys']=['tp_P11_L1_GLL0_acc']+['tp_P11_L1_GLL0_acc_'+str(ensnum) for ensnum in range(1,34)]
    elif center in ['gefs_raw','cmce_raw']:
        if lead == 'f06':
            keys={'lonkey':'lon_0','latkey':'lat_0','varkey':'APCP_P11_L1_GLL0_acc'}
        else:
            keys={'lonkey':'lon_0','latkey':'lat_0','varkey':'APCP_P11_L1_GLL0_acc6h'}
    elif center in ['gfs_hires_1hrly']:
        keys={'lonkey':'lon_0','latkey':'lat_0'}
        acvals1=['']*6+[str(r) for r in range(1,7)]*19
        acvals2=['']*6+['h']*114
        varkeylist=['APCP_P8_L1_GLL0_acc'+r+s for r,s in zip(acvals1,acvals2)]
        if li is None:
            keys['varkey']=varkeylist
        elif type(li) is int:
            keys['varkey']=varkeylist[li]
    elif center in ['gfs_hires_3hrly']:
        keys={'lonkey':'lon_0','latkey':'lat_0'}
        acvals1=['']*2+[str(r) for r in range(3,7,3)]*39
        acvals2=['']*2+['h']*78
        varkeylist=['APCP_P8_L1_GLL0_acc'+r+s for r,s in zip(acvals1,acvals2)]
        if li is None:
            keys['varkey']=varkeylist
        elif type(li) is int:
            keys['varkey']=varkeylist[li]
    elif center in ['ecmwf_hires_3hrly']:
        keys={'lonkey':'g0_lon_1','latkey':'g0_lat_0','varkey':'TP_GDS0_SFC'}
    elif center in ['ecmwf_ens']:
        keys={'lonkey':'g0_lon_2','latkey':'g0_lat_1','enskey':'ensemble0'}
        varkeylist=['TP_GDS0_SFC']*42+['TP_GDS0_SFC_10']*18
        if li is None:
            keys['varkey']=varkeylist
        elif type(li) is int:
            keys['varkey']=varkeylist[li]
    elif center in ['cmcRT_raw']:
        keys={'lonkey':'lon_0','latkey':'lat_0','enskey':'ensemble0','varkey':'APCP_P11_L1_GLL0_acc'}
    elif center in ['CFSv2','CMC1','CMC2','GFDL','GFDLFLOR1','GFDLFLOR2','NASA','CESM','CCSM4']:
        keys={'lonkey':'X','latkey':'Y','leadkey':'L','enskey':'M','varkey':'prec'}
    elif center in ['gefs','cmce','kwbc3hr','kwbc1hr','ecmf3hr','ecmfRT','cmcRT']:
        keys={'lonkey':'Lon','latkey':'Lat','leadkey':'Lead','enskey':'Ens','varkey':'Precipitation'}
    elif center in ['CENTRENDS']:
        keys={'lonkey':'longitude','latkey':'latitude','timekey':'time','varkey':'precip'}
    elif center in ['imerg_raw_archive','imerg_raw_realtime']:
        keys={'lonkey':'lon','latkey':'lat','varkey':'precipitationCal'}
    elif center in ['imerg']:
        keys={'lonkey':'Lon','latkey':'Lat','varkey':'Precipitation'}
    elif center in ['trmm','jaxa','cmorph','merge']:
        keys={'lonkey':'lon','latkey':'lat'}
    elif  center in ['ecmftmp','cwaotmp','egrrtmp','kwbctmp','babjtmp','sbsjtmp','rjtdtmp']:
        keys={'lonkey':'lon_0','latkey':'lat_0','leadkey':'forecast_time0','enskey':'ensemble0','varkey':'2t_P1_L103_GLL0'}
    elif center in ['lfpwtmp']: 
        keys={'lonkey':'lon_0','latkey':'lat_0','leadkey':'forecast_time0'}
        keys['varkeys']=['2t_P1_L103_GLL0_']+['2t_P1_L103_GLL0_'+str(ensnum) for ensnum in range(1,34)]

    else:
        print 'Center not found'
        keys=None
    return keys

#def in2out_griddef(center,outgrids):
#    #Defines correspondence between the output grids we want and the input grids that we download
#    #Need to define a different correspondce for each center and output grid
#    gridcor={}
#    if  center in ['ecmf','cwao','egrr','kwbc','babj','sbsj','rjtd','lfpw']:
#        for out in outgrids:
#            if out in ['gbm_z1','gbm_z2','bihar_z1','bihar_z2','gbm_gage','gbm_0p5deg','bihar_0p5deg','assam_0p1deg','dudhnoi_0p1deg','digaru_0p1deg','dikhow_0p1deg','BagmatiAdhwara_z1','BagmatiAdhwara_z2','Rapti','KRB_SBU','BagmatiRMSI','nepal_points']:
#                if 'gbm' not in gridcor:
#                    gridcor['gbm']=[out]
#                else:
#                    gridcor['gbm'].append(out)
#            if out in ['ethiopia_z1','ethiopia_z2','ea_z1','sudan_z1','sudan_z2','ea_z2','whole_nile','white_nile','blue_nile','nile_gage','ea_0p5deg']:
#                if 'africa' not in gridcor:
#                    gridcor['africa']=[out]
#                else:
#                    gridcor['africa'].append(out)
#            if out in ['periyar','kerala_0p5deg','kerala_0p1deg']:
#                if 'africa' not in gridcor:
#                    gridcor['kerala']=[out]
#                else:
#                    gridcor['kerala'].append(out)
#
#    if  center in ['gefs','cmce']:
#        for out in outgrids:
#            if out in ['gbm_z1','gbm_z2','bihar_z1','bihar_z2','gbm_gage','gbm_0p5deg','bihar_0p5deg','assam_0p1deg','dudhnoi_0p1deg','digaru_0p1deg','dikhow_0p1deg','nepal_points',\
#                       'ethiopia_z1','ethiopia_z2','sudan_z1','sudan_z2','ea_z1','ea_z2',\
#                       'whole_nile','white_nile','blue_nile','nile_gage','ea_0p5deg',\
#                       'BagmatiAdhwara_z1','BagmatiAdhwara_z2','Rapti','KRB_SBU','BagmatiRMSI']:
#                if 'global' not in gridcor:
#                    gridcor['global']=[out]
#                else:
#                    gridcor['global'].append(out)
#
#    if center in ['CFSv2','CMC1','CMC2','GFDL','GFDLFLOR1','GFDLFLOR2','NASA','CESM','CCSM4']:
#        for out in outgrids:
#            if out in ['gbm_z1','gbm_z2','bihar_z1','bihar_z2','gbm_gage','gbm_0p5deg','assam_0p1deg','dudhnoi_0p1deg','digaru_0p1deg','dikhow_0p1deg','bihar_0p5deg','nepal_points',\
#                       'ethiopia_z1','ethiopia_z2','sudan_z1','sudan_z2','ea_z1','ea_z2',\
#                       'whole_nile','white_nile','blue_nile','nile_gage','ea_0p5deg',\
#                       'BagmatiAdhwara_z1','BagmatiAdhwara_z2','Rapti','KRB_SBU','BagmatiRMSI']:
#                if 'afr_india' not in gridcor:
#                    gridcor['afr_india']=[out]
#                else:
#                    gridcor['afr_india'].append(out)
#    return gridcor
#
def center_def(center):
    c={}
    #Tigge Definitions
    if  center in ['ecmf','cwao','egrr','kwbc','babj','sbsj','rjtd','lfpw']:
        c={'center_name':center,'center_category':'tigge','ingrids':['africa_0p5deg','gbm_0p5deg','kerala_0p5deg'],\
            'latdir':'NtoS','infile_keys':input_key_def(center),\
            'infile_format':'grb2','type':'forecast_onefile','file_dimension_type':'4D',\
            'missingdata':-999,'multiplier':1,'mindata':-3,'maxdata':40000,\
            'units':'mm','accumtype':'accum','timestep':6,'lead_unit':'hours','resolution':0.5}
        if center == 'ecmf':
            c['nens']=50
            c['nfcst']=60
            c['fcst_hrs']=['00']
            c['ensdata']='one_variable'
        elif center == 'cwao':
            c['nens']=21
            c['nfcst']=64
            c['fcst_hrs']=['00']
            c['ensdata']='one_variable'
        elif center == 'egrr':
            c['nens']=23 #this is quite variable over the record
            c['nfcst']=29
            c['fcst_hrs']=['00']
            c['ensdata']='one_variable'
        elif center == 'kwbc':
            c['nens']=21 #This is to match the realtime gefs that has 21 (and includes control)
            c['nfcst']=64
            c['fcst_hrs']=['00']
            c['ensdata']='one_variable'
        elif center == 'babj':
            c['nens']=14
            c['nfcst']=60
            c['fcst_hrs']=['00']
            c['ensdata']='one_variable'
        elif center == 'lfpw':
            c['nens']=34
            c['nfcst']=18
            c['fcst_hrs']=['18']
            c['ensdata']='separate_variables'
        elif center == 'rjtd':
            c['nens']=26
            c['nfcst']=44
            c['fcst_hrs']=['12']
            c['ensdata']='one_variable'
        elif center == 'sbsj':
            c['nens']=14
            c['nfcst']=60
            c['fcst_hrs']=['00']
            c['ensdata']='one_variable'
        c['leads']=np.arange(0,c['nfcst'])*c['timestep']+c['timestep']

    elif center in ['multimodel']:
        c={'center_name':center,'center_category':'multimodel','type':'forecast_onefile','nens':1}

    elif  center in ['ecmftmp','cwaotmp','egrrtmp','kwbctmp','babjtmp','sbsjtmp','rjtdtmp','lfpwtmp']:
        c={'center_name':center,'center_category':'tigge','ingrids':['africa_0p5deg','gbm_0p5deg'],\
            'latdir':'NtoS','infile_keys':input_key_def(center),\
            'infile_format':'grb2','type':'forecast_onefile','file_dimension_type':'4D',\
            'missingdata':-999,'multiplier':1,'mindata':0,'maxdata':4000,\
            'units':'K','accumtype':'inst','timestep':6,'lead_unit':'hours','resolution':0.5}
        if center == 'ecmftmp':
            c['nens']=50
            c['nfcst']=61
            c['fcst_hrs']=['00']
            c['ensdata']='one_variable'
        elif center == 'cwaotmp':
            c['nens']=21
            c['nfcst']=65
            c['fcst_hrs']=['00']
            c['ensdata']='one_variable'
        elif center == 'egrrtmp':
            c['nens']=23 #this is quite variable over the record
            c['nfcst']=30
            c['fcst_hrs']=['00']
            c['ensdata']='one_variable'
        elif center == 'kwbctmp':
            c['nens']=21 #This is to match the realtime gefs that has 21 (and includes control)
            c['nfcst']=65
            c['fcst_hrs']=['00']
            c['ensdata']='one_variable'
        elif center == 'babjtmp':
            c['nens']=14
            c['nfcst']=61
            c['fcst_hrs']=['00']
            c['ensdata']='one_variable'
        elif center == 'lfpwtmp':
            c['nens']=34
            c['nfcst']=19
            c['fcst_hrs']=['18']
            c['ensdata']='separate_variables'
        elif center == 'rjtdtmp':
            c['nens']=26
            c['nfcst']=45
            c['fcst_hrs']=['12']
            c['ensdata']='one_variable'
        elif center == 'sbsjtmp':
            c['nens']=14
            c['nfcst']=61
            c['fcst_hrs']=['00']
            c['ensdata']='one_variable'
        c['leads']=np.arange(0,c['nfcst'])*c['timestep']

    if  center in ['gefs_raw']:
        #list of strings that specify all ensemble members and lead times in the individual file names
        enslist=['gec00']+['gep'+str(num).zfill(2) for num in range(1,21)]
        fcstlist=['f'+str(num).zfill(2) for num in range(6,99,6)]+['f'+str(num).zfill(3) for num in range(102,385,6)]
        tstep=6

        c={'center_name':center,'center_category':'nomads','ingrids':['global_1deg'],\
            'latdir':'NtoS','infile_keys':input_key_def(center),\
            'infile_format':'grb2','type':'forecast_manyfiles','file_dimension_type':'2D',\
            'missingdata':1e20,'multiplier':4,'mindata':-3,'maxdata':40000,\
            'units':'kg m-2','accumtype':'accum6hr','timestep':tstep,'lead_unit':'hours',\
            'enslist':enslist,'fcstlist':fcstlist,'nens':len(enslist),\
            'nfcst':len(fcstlist),'resolution':1}
        c['leads']=np.arange(0,c['nfcst'])*c['timestep']+c['timestep']

    if  center in ['gfs_hires_1hrly']:
        #list of strings that specify all ensemble members and lead times in the individual file names
        fcstlist=['f'+str(num).zfill(3) for num in range(1,121,1)]
        tstep=1

        c={'center_name':center,'center_category':'nomads','ingrids':['global_0p25deg'],\
            'latdir':'NtoS','infile_keys':input_key_def(center),\
            'infile_format':'grb2','type':'forecast_manyfiles','file_dimension_type':'2D',\
            'missingdata':1e20,'multiplier':24,'mindata':-3,'maxdata':40000,\
            'units':'kg m-2','accumtype':'accum_gfs_mixed','timestep':tstep,'lead_unit':'hours',\
            'fcstlist':fcstlist,'nens':1,\
            'nfcst':len(fcstlist),'resolution':0.25}
        c['leads']=np.arange(0,c['nfcst'])*c['timestep']

    if  center in ['gfs_hires_3hrly']:
        #list of strings that specify all ensemble members and lead times in the individual file names
        fcstlist=['f'+str(num).zfill(3) for num in range(3,243,3)]
        tstep=3

        c={'center_name':center,'center_category':'nomads','ingrids':['gbm_0p1degv2'],\
            'latdir':'NtoS','infile_keys':input_key_def(center),\
            'infile_format':'grb2','type':'forecast_manyfiles','file_dimension_type':'2D',\
            'missingdata':1e20,'multiplier':24,'mindata':-3,'maxdata':40000,\
            'units':'kg m-2','accumtype':'accum_gfs_mixed','timestep':tstep,'lead_unit':'hours',\
            'fcstlist':fcstlist,'nens':1,\
            'nfcst':len(fcstlist),'resolution':0.25}
        c['leads']=np.arange(0,c['nfcst'])*c['timestep']

    if  center in ['ecmwf_hires_3hrly']:
        #list of strings that specify all ensemble members and lead times in the individual file names
        tstep=3
        c={'center_name':center,'center_category':'ecmwfftp','ingrids':['gbm_0p1degv2'],\
            'latdir':'NtoS','infile_keys':input_key_def(center),\
            'infile_format':'grb','type':'forecast_manyfiles','file_dimension_type':'2D',\
            'missingdata':1e20,'multiplier':800,'mindata':-3,'maxdata':40000,\
            'units':'kg m-2','accumtype':'accum','timestep':tstep,'lead_unit':'hours',\
            'nens':1,\
            'nfcst':48,'resolution':0.1}
        c['leads']=np.arange(0,c['nfcst'])*c['timestep']+c['timestep'] #Accumulate precip lead is end of per

    if  center in ['ecmwf_ens']:
        #list of strings that specify all ensemble members and lead times in the individual file names
        tstep=6
        c={'center_name':center,'center_category':'ecmwfftp','ingrids':['gbm_0p5deg'],\
            'latdir':'NtoS','infile_keys':input_key_def(center),\
            'infile_format':'grb','type':'forecast_manyfiles','file_dimension_type':'3D_ens',\
            'missingdata':1e20,'multiplier':800,'mindata':-3,'maxdata':40000,\
            'units':'kg m-2','accumtype':'accum','timestep':tstep,'lead_unit':'hours',\
            'nens':51,\
            'nfcst':60,'ensdata':'one_variable','resolution':0.5}
        c['leads']=np.arange(0,c['nfcst'])*c['timestep']+c['timestep'] #Accumulate precip lead is end of per

    if  center in ['cmcRT_raw']:
        #list of strings that specify all ensemble members and lead times in the individual file names
        tstep=6
        fcstlist=[str(num).zfill(3) for num in range(6,384,6)]
        c={'center_name':center,'center_category':'cmcftp','ingrids':['global_0p5deg'],\
            'latdir':'StoN','infile_keys':input_key_def(center),\
            'infile_format':'grb2','type':'forecast_manyfiles','file_dimension_type':'3D_ens',\
            'missingdata':1e20,'multiplier':1,'mindata':-3,'maxdata':40000,\
            'units':'kg m-2','accumtype':'accum','timestep':tstep,'lead_unit':'hours',\
            'fcstlist':fcstlist,'nens':21,\
            'nfcst':64,'ensdata':'one_variable','resolution':0.5}
        c['leads']=np.arange(0,c['nfcst'])*c['timestep']+c['timestep'] #Accumulate precip lead is end of per

    if  center in ['gem_raw']:
        #list of strings that specify all ensemble members and lead times in the individual file names
        fcstlist=[str(num).zfill(3) for num in range(0,243,3)]
        tstep=3

        c={'center_name':center,'center_category':'nomads','ingrids':['global_0p24deg'],\
            'latdir':'NtoS','infile_keys':input_key_def(center),\
            'infile_format':'grb2','type':'forecast_manyfiles','file_dimension_type':'2D',\
            'missingdata':1e20,'multiplier':1,'mindata':-3,'maxdata':40000,\
            'units':'kg m-2','accumtype':'accum','timestep':tstep,'lead_unit':'hours',\
            'fcstlist':fcstlist,'nens':1,\
            'nfcst':len(fcstlist),'resolution':0.24}
        c['leads']=np.arange(0,c['nfcst'])*c['timestep']+c['timestep']

    if  center in ['cmce_raw']:
        #list of strings that specify all ensemble members and lead times in the individual file names
        fcstlist=[str(num).zfill(3) for num in range(0,195,3)]+[str(num).zfill(3) for num in range(198,774,6)]
        tstep=3

        c={'center_name':center,'center_category':'nomads','ingrids':['global_0p5deg'],\
            'latdir':'NtoS','infile_keys':input_key_def(center),\
            'infile_format':'grb2','type':'forecast_manyfiles','file_dimension_type':'2D',\
            'missingdata':1e20,'multiplier':1,'mindata':-3,'maxdata':40000,\
            'units':'kg m-2','accumtype':'accum','timestep':tstep,'lead_unit':'hours',\
            'fcstlist':fcstlist,'nens':1,\
            'nfcst':len(fcstlist),'resolution':0.5}
        c['leads']=np.arange(0,c['nfcst'])*c['timestep']+c['timestep']

    if  center in ['gefs','cmce']:
        tstep=6
        nfcst=64
        nens=21
        c={'center_name':center,'center_category':'nomads','ingrids':['gbm_0p5deg','east_africa_0p5deg'],\
            'latdir':'StoN','infile_keys':input_key_def(center),\
            'infile_format':'netcdf','type':'forecast_onefile','file_dimension_type':'4D',\
            'missingdata':1e20,'multiplier':1,'mindata':-3,'maxdata':40000,\
            'units':'mm/day','accumtype':'accum6hr','timestep':tstep,'lead_unit':'hours',\
            'leads':np.arange(0,nfcst)*tstep+tstep,'fcst_hrs':['00'],'nens':nens,\
            'ensdata':'one_variable','nfcst':nfcst,'resolution':0.5}
        if center == 'gefs':
            c['out_name']='kwbc'
        if center == 'cmce':
            c['out_name']='cwao'
            
    if  center in ['cmcRT']:
        tstep=6
        nfcst=64
        nens=21
        c={'center_name':center,'center_category':'cmcftp','ingrids':['gbm_0p5deg','east_africa_0p5deg'],\
            'latdir':'StoN','infile_keys':input_key_def(center),\
            'infile_format':'netcdf','type':'forecast_onefile','file_dimension_type':'4D',\
            'missingdata':1e20,'multiplier':1,'mindata':-3,'maxdata':40000,\
            'units':'mm/day','accumtype':'accum','timestep':tstep,'lead_unit':'hours',\
            'leads':np.arange(0,nfcst)*tstep+tstep,'fcst_hrs':['00'],'nens':nens,\
            'out_name':'cwao','ensdata':'one_variable','nfcst':nfcst,'resolution':0.5}
            
    if  center in ['ecmf3hr']:
        tstep=3
        nfcst=48
        nens=1
        c={'center_name':center,'center_category':'ecmwf','ingrids':['gbm_0p1degv2'],\
            'latdir':'StoN','infile_keys':input_key_def(center),\
            'infile_format':'netcdf','type':'forecast_onefile','file_dimension_type':'4D',\
            'missingdata':1e20,'multiplier':1,'mindata':-3,'maxdata':40000,\
            'units':'mm/day','accumtype':'accum','timestep':tstep,'lead_unit':'hours',\
            'leads':np.arange(0,nfcst)*tstep+tstep,'fcst_hrs':['00','06','12','18'],'nens':nens,\
            'ensdata':'one_variable','nfcst':nfcst,'resolution':0.1}

    if  center in ['kwbc3hr']:
        tstep=3
        nfcst=80
        nens=1
        c={'center_name':center,'center_category':'ecmwf','ingrids':['gbm_0p1degv2'],\
            'latdir':'StoN','infile_keys':input_key_def(center),\
            'infile_format':'netcdf','type':'forecast_onefile','file_dimension_type':'4D',\
            'missingdata':1e20,'multiplier':1,'mindata':-3,'maxdata':40000,\
            'units':'mm/day','accumtype':'accum3hr','timestep':tstep,'lead_unit':'hours',\
            'leads':np.arange(0,nfcst)*tstep+tstep,'fcst_hrs':['00','06','12','18'],'nens':nens,\
            'ensdata':'one_variable','nfcst':nfcst,'resolution':0.1}
            
    if  center in ['ecmfRT']:
        tstep=6
        nfcst=60
        nens=51
        c={'center_name':center,'center_category':'ecmwf','ingrids':['gbm_0p5'],\
            'latdir':'StoN','infile_keys':input_key_def(center),\
            'infile_format':'netcdf','type':'forecast_onefile','file_dimension_type':'4D',\
            'missingdata':1e20,'multiplier':1,'mindata':-3,'maxdata':40000,\
            'units':'mm/day','accumtype':'accum','timestep':tstep,'lead_unit':'hours',\
            'leads':np.arange(0,nfcst)*tstep+tstep,'fcst_hrs':['00'],'nens':nens,\
            'ensdata':'one_variable','nfcst':nfcst,'resolution':0.5,'out_name':'ecmf'}

    if  center in ['CFSv2','CMC1','CMC2','GFDL','GFDLFLOR1','GFDLFLOR2','NASA','CCSM4','CESM']:
        c={'center_name':center,'center_category':'nmme','ingrids':['afr_india_1deg'],\
            'latdir':'StoN','infile_keys':input_key_def(center),\
            'infile_format':'netcdf','type':'forecast_onefile','file_dimension_type':'4D',\
            'missingdata':1e20,'multiplier':1,'mindata':-3,'maxdata':40000,'ensdata':'one_variable',\
            'units':'mm/day','accumtype':'accum1mo','timestep':1,'lead_unit':'months','resolution':1}
        if center == 'CFSv2':
            c['long_name']='NCEP-CFSv2'
            c['nens']=32
            c['nfcst']=10
            c['fcst_hrs']=['00']
        elif center == 'CMC1':
            c['long_name']='CMC1-CanCM3'
            c['nens']=10
            c['nfcst']=12
            c['fcst_hrs']=['00']
        elif center == 'CMC2':
            c['long_name']='CMC2-CanCM4'
            c['nens']=10 #this is quite variable over the record
            c['nfcst']=12
            c['fcst_hrs']=['00']
        elif center == 'GFDL':
            c['long_name']='GFDL-CM2p1-aer04'
            c['nens']=10
            c['nfcst']=12
            c['fcst_hrs']=['00']
        elif center == 'GFDLFLOR1':
            c['long_name']='GFDL-CM2p5-FLOR-A06'
            c['nens']=12
            c['nfcst']=12
            c['fcst_hrs']=['00']
        elif center == 'GFDLFLOR2':
            c['long_name']='GFDL-CM2p5-FLOR-B01'
            c['nens']=12
            c['nfcst']=12
            c['fcst_hrs']=['00']
        elif center == 'NASA':
            c['long_name']='NASA-GMAO-062012'
            c['nens']=12
            c['nfcst']=9
            c['fcst_hrs']=['00']
        elif center == 'CCSM4':
            c['long_name']='COLA-RSMAS-CCSM4'
            c['nens']=10
            c['nfcst']=12
            c['fcst_hrs']=['00']
        elif center == 'CESM':
            c['long_name']='NCAR-CESM1'
            c['nens']=10
            c['nfcst']=12
            c['fcst_hrs']=['00']
        c['leads']=np.arange(0,c['nfcst'])*c['timestep']+0.5

    if  center in ['gefs_raw']:
        #list of strings that specify all ensemble members and lead times in the individual file names
        enslist=['gec00']+['gep'+str(num).zfill(2) for num in range(1,21)]
        fcstlist=['f'+str(num).zfill(2) for num in range(6,99,6)]+['f'+str(num).zfill(3) for num in range(102,385,6)]
        tstep=6
        c={'center_name':center,'center_category':'ncep','ingrids':['global_1deg'],\
            'latdir':'NtoS','infile_keys':input_key_def(center),\
            'infile_format':'grb2','type':'forecast_manyfiles','file_dimension_type':'2D',\
            'missingdata':1e20,'multiplier':4,'mindata':-3,'maxdata':40000,\
            'units':'kg m-2','accumtype':'accum6hr','timestep':tstep,'lead_unit':'hours',\
            'enslist':enslist,'fcstlist':fcstlist,'nens':len(enslist),'nfcst':len(fcstlist),\
            'leads':np.arange(0,len(fcstlist))*tstep+tstep,'fcst_hrs':['00'],'resolution':1}
    if center in ['CENTRENDS']:
        c={'center_name':center,'center_cateory':'centrends','ingrids':['horn_afr_0p1deg'],\
            'latdir':'NtoS','infile_keys':input_key_def(center),\
            'infile_format':'netcdf','type':'obs_onefile','file_dimension_type':'3D',\
            'missingdata':-999,'multiplier':1,'mindata':-3,'maxdata':40000,\
            'units':'mm/month','accumtype':'accum1mo','timestep':1,'time_unit':'months',\
            'ref_date':'01-01-1900','dates':'variable','resolution':0.1}
    if center in ['imerg_raw_archive','imerg_raw_realtime']:
        c={'center_name':center,'center_cateory':'imerg','ingrids':['global_0p1deg'],\
            'latdir':'StoN','infile_keys':input_key_def(center),\
            'infile_format':'netcdf','type':'obs_onefile','file_dimension_type':'2D',\
            'missingdata':-999,'multiplier':1,'mindata':-3,'maxdata':40000,\
            'units':'mm/day','accumtype':'accum1day','resolution':0.1}
    if center in ['imerg']:
        c={'center_name':center,'center_cateory':'imerg','ingrids':['east_africa_0p1deg','gbm_0p1deg'],\
            'latdir':'StoN','infile_keys':input_key_def(center),\
            'infile_format':'netcdf','type':'obs_onefiles','file_dimension_type':'2D',\
            'missingdata':-999,'multiplier':1,'mindata':-0.1,'maxdata':40000,\
            'units':'mm/day','accumtype':'accum1day','resolution':0.1}
    if center in ['trmm','jaxa','merge','cmorph']:
        c={'center_name':center,'center_cateory':'obs','ingrids':['africa_0p1deg','gbm_0p1deg','kerala_0p1deg'],\
            'latdir':'StoN','infile_keys':input_key_def(center),\
            'infile_format':'binaryf4','header_length':5,'dimensions':('lat','lon'),\
            'type':'obs_manyfiles','file_dimension_type':'2D',\
            'missingdata':-999,'multiplier':24,'mindata':-0.1,'maxdata':2000,\
            'units':'mm','accumtype':'accum3hr','resolution':0.1,'interval':3,'timeunit':'hours',\
            'filedatedef':'midaccum'}
    if center in ['gauge']:
        c={'center_name':center,'center_cateory':'obs','ingrids':['east_africa_0p1deg','gbm_0p1deg'],\
            'latdir':'NtoS','infile_keys':input_key_def(center),\
            'infile_format':'binaryf4','header_length':5,'dimensions':('lat','lon'),'type':'obs_onefiles','file_dimension_type':'2D',\
            'missingdata':-999,'multiplier':1,'mindata':-0.1,'maxdata':40000,\
            'units':'mm/day','accumtype':'accum3hr','resolution':0.1}
    return c

def make_outtype(outdomtype,outdomlist):
    outtype={}
    for ot,dom in zip(outdomtype,outdomlist):
        outtype[dom]=ot
    return outtype

def basetime_def(basetimestep):
    t={}
    if basetimestep in ['acc3h']:
        t['out_forecast_accum']=[0.125]
        t['out_obs_accum']=0.125
        t['out_forecast_leads']=[list(np.arange(0,10,0.125))]
        t['obstimestep']=0.125
        t['fcst_initiailziation_timestep']=1 #Timestepbetween each output file in days.  For now, this can only be 1 because if have 1 initialization per day
    elif basetimestep in ['acc6h']:
        t['out_forecast_accum']=[0.25]
        t['out_obs_accum']=0.25
        t['out_forecast_leads']=[list(np.arange(0,16.25,0.25))]
        t['obstimestep']=0.25
        t['fcst_initiailziation_timestep']=1 #Timestepbetween each output file in days.  For now, this can only be 1 because if have 1 initialization per day
    elif basetimestep in ['acc24h']:
        t['out_forecast_accum']=[1]
        t['out_obs_accum']=1
        t['out_forecast_leads']=[list(np.arange(0,17,1))]
        t['obstimestep']=1
        t['fcst_initiailziation_timestep']=1 #Timestepbetween each output file in days.  For now, this can only be 1 because if have 1 initialization per day
    elif basetimestep in ['acc5d']:
        t['out_forecast_accum']=[5]
        t['out_obs_accum']=5
        t['out_forecast_leads']=[list(np.arange(0,17,1))]
        t['obstimestep']=1
        t['fcst_initiailziation_timestep']=1 #Timestepbetween each output file in days.  For now, this can only be 1 because if have 1 initialization per day
    elif basetimestep in ['acc1mo']:
        t['out_forecast_accum']=[1]
        t['out_obs_accum']=1
        t['out_forecast_leads']=[list(np.arange(0,17,1))]
        t['obstimestep']=1
        t['fcst_initiailziation_timestep']=1 #Timestepbetween each output file in months.  For now, this can only be 1 because if have 1 initialization per day
    elif basetimestep in ['acc3mo']:
        t['out_forecast_accum']=[3]
        t['out_obs_accum']=3
        t['out_forecast_leads']=[list(np.arange(0,17,1))]
        t['obstimestep']=1
        t['fcst_initiailziation_timestep']=1 #Timestepbetween each output file in days.  For now, this can only be 1 because if have 1 initialization per day
    return t
