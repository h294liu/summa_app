import Nio
from datetime import datetime
from datetime import timedelta
import os
import itertools
import numpy as np
import pdb
import scipy.io.netcdf as S
import grid_utils
import definitions

def write_netcdf(variables,dimensions,attributes,filename):
    f=S.NetCDFFile(filename,mode='w')
    for d in dimensions:
        f.createDimension(d['name'],d['length'])
    var=[None]*len(variables)
    for i,v in enumerate(variables):
        var[i]=f.createVariable(v['name'],v['format'],v['dimension_tuple'])
        var[i].units=v['units']
        var[i].description=v['description']
        if 'missing_value' in v:
            var[i].missing_value=v['missing_value']
            if np.ma.is_masked(v['data']):
                v['data']=v['data'].filled(fill_value=v['missing_value'])
        var[i][:]=v['data']
    for a in attributes:
        f.description = a['description']
        f.history = a['history']
        if 'TimeZone' in a:
            f.TimeZone = a['TimeZone']
    f.close
    
def prepare_single_forecast_for_netcdf(data,center,idate):
    #Assumes single initialization time
    #Data is a dictionary with 'var','fcstlead','ens','lat',lon'
    #var has the dimensions (ens,lead,lat,lon)
    #center a string describing the center that made the forecast
    #idate is the initialization date for the forecast
    a=[None]*1 #Attributes
    d=[None]*4 #Dimensions
    v=[None]*5 #Variables
    v[4]={'name':'Precipitation','format':'f','dimension_tuple':(('Ens','Lead','Lat','Lon')),'data':data['var'],'units':'kg/m^2',\
            'description':'6 hour accumulated forecast precipitation'}
    v[0]={'name':'Lead','format':'f','dimension_tuple':(('Lead',)),'data':data['fcstlead'],'units':'hours','description':'Forecast Lead'}
    v[1]={'name':'Ens','format':'i','dimension_tuple':(('Ens',)),'data':np.array(data['ens']),'units':'unitless','description':'Ensemble Number'}
    v[2]={'name':'Lon','format':'f','dimension_tuple':(('Lon',)),'data':data['lon'],'units':'degrees','description':'Longitude'}
    v[3]={'name':'Lat','format':'f','dimension_tuple':(('Lat',)),'data':data['lat'],'units':'degrees','description':'Latitude'}
    d[0]={'name':'Lead','length':len(data['fcstlead'])}
    d[1]={'name':'Ens','length':len(data['ens'])}
    d[2]={'name':'Lon','length':len(data['lon'])}
    d[3]={'name':'Lat','length':len(data['lat'])}
    a[0]={'description':'Data from '+center+' from '+idate.strftime('%Y%m%d'),'history':'Created '+datetime.now().date().strftime('%Y%m%d')}
    return {'variables':v,'dimensions':d,'attributes':a}

def prepare_xyslice_for_netcdf(data,center,idate):
    #Assumes single initialization time
    #Data is a dictionary with 'var','fcstlead','ens','lat',lon'
    #var has the dimensions (ens,lead,lat,lon)
    #center a string describing the center that made the forecast
    #idate is the initialization date for the forecast
    a=[None]*1 #Attributes
    d=[None]*2 #Dimensions
    v=[None]*3 #Variables
    v[2]={'name':'Precipitation','format':'f','dimension_tuple':(('Lat','Lon')),'data':data['var'],'units':'kg/m^2',\
            'description':'6 hour accumulated forecast precipitation'}
    v[0]={'name':'Lon','format':'f','dimension_tuple':(('Lon',)),'data':data['lon'],'units':'degrees','description':'Longitude'}
    v[1]={'name':'Lat','format':'f','dimension_tuple':(('Lat',)),'data':data['lat'],'units':'degrees','description':'Latitude'}
    d[0]={'name':'Lon','length':len(data['lon'])}
    d[1]={'name':'Lat','length':len(data['lat'])}
    a[0]={'description':'Data from '+center+' from '+idate.strftime('%Y%m%d'),'history':'Created '+datetime.now().date().strftime('%Y%m%d')}
    return {'variables':v,'dimensions':d,'attributes':a}

def write_fcstsummarymap_to_netcdf(fn,data,center,outtype,variabledata=None):
    if variabledata is None:
        #Default values
        variabledata={}
        variabledata['name']='Precipitation'
        variabledata['description']='Accumulated Forecast Precipitation'
        variabledata['mising_value']=-999
        variabledata['units']='mm'
    a=[None]*1 #Attributes
    a[0]={'description':data['description'],'history':'Created '+datetime.now().date().strftime('%Y%m%d'),'TimeZone':'UTC'}
    if outtype in ['grid']:
        d=[None]*3 #Dimensions
        v=[None]*5 #Variables
        v[0]={'name':'Lon','format':'f','dimension_tuple':(('Lon',)),'data':data['lon'],'units':'degrees','description':'Longitude'}
        v[1]={'name':'Lat','format':'f','dimension_tuple':(('Lat',)),'data':data['lat'],'units':'degrees','description':'Latitude'}
        d[0]={'name':'Lon','length':len(data['lon'])}
        d[1]={'name':'Lat','length':len(data['lat'])}
        d[2]={'name':'NMod','length':len(data['leads'])}
        v[2]={'name':variabledata['name'],'format':'f','dimension_tuple':(('Lat','Lon')),'data':data['pcp'],'units':variabledata['units'],\
                'description':variabledata['description'],'missing_value':variabledata['missing_value']}
        v[3]={'name':'Leads','format':'f','dimension_tuple':(('NMod',)),'data':data['leads'],'units':'hours','description':'Lead Time for each model used'}
        v[4]={'name':'Weights','format':'f','dimension_tuple':(('NMod',)),'data':data['weights'],'units':'unitless','description':'Weights used for each model used'}
    if outtype in ['catch']:
        d=[None]*2 #Dimensions
        v=[None]*4 #Variables
        v[0]={'name':'CatchID','format':'f','dimension_tuple':(('Catch',)),'data':data['cid'],'units':'unitless','description':'Catchment ID Number'}
        d[0]={'name':'Catch','length':len(data['cid'])}
        d[1]={'name':'NMod','length':len(data['leads'])}
        v[1]={'name':variabledata['name'],'format':'f','dimension_tuple':(('Catch',)),'data':data['pcp'],'units':variabledata['units'],\
                'description':variabledata['description'],'missing_value':variabledata['missing_value']}
        v[2]={'name':'Leads','format':'f','dimension_tuple':(('NMod',)),'data':data['leads'],'units':'hours','description':'Lead Time for each model used'}
        v[3]={'name':'Weights','format':'f','dimension_tuple':(('NMod',)),'data':data['weights'],'units':'unitless','description':'Weights used for each model used'}
    write_netcdf(v,d,a,fn)
    return {'variables':v,'dimensions':d,'attributes':a}

def write_clim_to_netcdf(fn,data,center,data_attributes):
    #Data is a dictionary with 'mean','stdev','all_sorted','starttime', and 'cid' 
    a=[None]*1 #Attributes
    a[0]={'description':'Data from '+center,'history':'Created '+datetime.now().date().strftime('%Y%m%d')}
    d=[None]*2
    v=[None]*4
    v[0]={'name':'CatchID','format':'f','dimension_tuple':(('Catch',)),'data':data['cid'],'units':'unitless','description':'Catchment ID Number'}
    v[1]={'name':'data_mean','format':'f','dimension_tuple':(('Catch',)),'data':data['mean'],'units':data_attributes['units'],\
        'description':data_attributes['description']}
    v[2]={'name':'data_stdev','format':'f','dimension_tuple':(('Catch',)),'data':data['stdev'],'units':data_attributes['units'],\
        'description':data_attributes['description']}
    v[3]={'name':'data_sorted','format':'f','dimension_tuple':(('Years','Catch')),'data':data['cdf'],'units':data_attributes['units'],\
        'description':data_attributes['description']}

    d[0]={'name':'Catch','length':len(data['cid'])}
    d[1]={'name':'Years','length':data['cdf'].shape[0]}
    write_netcdf(v,d,a,fn)
    return {'variables':v,'dimensions':d,'attributes':a}

def write_forecast_one_initialization(fn,data,center,idate,outtype,accumunit='Days'):
    #Assumes single initialization time
    #Data is a dictionary with 'var','starttime','endtime','accumper','lead','cid','ens'
    #var has the dimensions (nens,nfcst,ncatch)
    #center a string describing the center that made the forecast
    #idate is the initialization date for the forecast
    #outtype is "catch" or "grid"
    a=[None]*1 #Attributes
    if outtype in ['catch']:
        d=[None]*3 #Dimensions
        v=[None]*7 #Variables
        v[5]={'name':'CatchID','format':'f','dimension_tuple':(('Catch',)),'data':data['cid'],'units':'unitless','description':'Catchment ID Number'}
        v[6]={'name':'Precipitation','format':'f','dimension_tuple':(('Ens','Fcst','Catch')),'data':data['var'],'units':'mm/day',\
            'description':'Average Precipitation Rate over Forecast Period'}
        d[2]={'name':'Catch','length':len(data['cid'])}
    elif outtype in ['grid']:
        d=[None]*4 #Dimensions
        v=[None]*8 #Variables
        v[5]={'name':'Lon','format':'f','dimension_tuple':(('Lon',)),'data':data['lon'],'units':'degrees','description':'Longitude'}
        v[6]={'name':'Lat','format':'f','dimension_tuple':(('Lat',)),'data':data['lat'],'units':'degrees','description':'Latitude'}
        v[7]={'name':'Precipitation','format':'f','dimension_tuple':(('Ens','Fcst','Lat','Lon')),'data':data['var'],'units':'mm/day',\
                'description':'Average Precipitation Rate over Forecast Period'}
        d[2]={'name':'Lon','length':len(data['lon'])}
        d[3]={'name':'Lat','length':len(data['lat'])}

    v[0]={'name':'StartDate','format':'f','dimension_tuple':(('Fcst',)),'data':data['starttime'],'units':'Days since 01Jan0000',\
            'description':'Beginning of the averaging period of the Forecast Precipitation'}
    v[1]={'name':'EndDate','format':'f','dimension_tuple':(('Fcst',)),'data':data['endtime'],'units':'Days since 01Jan0000',\
            'description':'End of the averaging period of the Forecast Precipitation'}
    v[2]={'name':'Lead','format':'f','dimension_tuple':(('Fcst',)),'data':data['lead'],'units':accumunit,\
            'description':'Time in between the Initialization Date and the Start Date'}
    v[3]={'name':'AccumPer','format':'f','dimension_tuple':(('Fcst',)),'data':data['accumper'],'units':accumunit,\
            'description':'Accumulation Period between the Start Date and the End Date'}
    v[4]={'name':'Ens','format':'i','dimension_tuple':(('Ens',)),'data':np.array(data['ens']),'units':'unitless','description':'Ensemble Number'}

    d[0]={'name':'Fcst','length':len(data['lead'])}
    d[1]={'name':'Ens','length':len(data['ens'])}

    a[0]={'description':'Data from '+center+' from '+idate.strftime('%Y%m%d'),'history':'Created '+datetime.now().date().strftime('%Y%m%d')}
    write_netcdf(v,d,a,fn)
    return {'variables':v,'dimensions':d,'attributes':a}

def write_forecast_many_initializations(fn,data,center,outtype,missingval=None):
    #Assumes single initialization time
    #Data is a dictionary with 'var','starttime','endtime','accumper','lead','cid','ens'
    #var has the dimensions (nens,nfcst,ncatch)
    #center a string describing the center that made the forecast
    #idate is the initialization date for the forecast
    #outtype is "catch" or "grid"
    a=[None]*1 #Attributes
    if outtype in ['catch']:
        d=[None]*4 #Dimensions
        v=[None]*8 #Variables
        v[6]={'name':'CatchID','format':'f','dimension_tuple':(('Catch',)),'data':data['cid'],'units':'unitless','description':'Catchment ID Number'}
        if missingval is None:
            v[7]={'name':'Precipitation','format':'f','dimension_tuple':(('InitDate','Ens','Fcst','Catch')),'data':data['var'],'units':'mm/day',\
            'description':'Average Precipitation Rate over Forecast Period'}
        else:
            v[7]={'name':'Precipitation','format':'f','dimension_tuple':(('InitDate','Ens','Fcst','Catch')),'data':data['var'],'units':'mm/day',\
                    'description':'Average Precipitation Rate over Forecast Period','missing_value':missingval}

        d[3]={'name':'Catch','length':len(data['cid'])}
    elif outtype in ['grid']:
        d=[None]*5 #Dimensions
        v=[None]*9 #Variables
        v[6]={'name':'Lon','format':'f','dimension_tuple':(('Lon',)),'data':data['lon'],'units':'degrees','description':'Longitude'}
        v[7]={'name':'Lat','format':'f','dimension_tuple':(('Lat',)),'data':data['lat'],'units':'degrees','description':'Latitude'}
        if missingval is None:
            v[8]={'name':'Precipitation','format':'f','dimension_tuple':(('InitDate','Ens','Fcst','Lat','Lon')),'data':data['var'],'units':'mm/day',\
                'description':'Average Precipitation Rate over Forecast Period'}
        else:
            v[8]={'name':'Precipitation','format':'f','dimension_tuple':(('InitDate','Ens','Fcst','Lat','Lon')),'data':data['var'],'units':'mm/day',\
                'description':'Average Precipitation Rate over Forecast Period','missing_value':missingval}
        d[3]={'name':'Lon','length':len(data['lon'])}
        d[4]={'name':'Lat','length':len(data['lat'])}

    v[0]={'name':'StartDate','format':'f','dimension_tuple':(('InitDate','Fcst')),'data':data['starttime'],'units':'Days since 01Jan0000',\
            'description':'Beginning of the averaging period of the Forecast Precipitation'}
    v[1]={'name':'EndDate','format':'f','dimension_tuple':(('InitDate','Fcst')),'data':data['endtime'],'units':'Days since 01Jan0000',\
            'description':'End of the averaging period of the Forecast Precipitation'}
    v[2]={'name':'Lead','format':'f','dimension_tuple':(('Fcst',)),'data':data['lead'],'units':'Days',\
            'description':'Time in between the Initialization Date and the Start Date'}
    v[3]={'name':'AccumPer','format':'f','dimension_tuple':(('Fcst',)),'data':data['accumper'],'units':'Days',\
            'description':'Accumulation Period between the Start Date and the End Date'}
    v[4]={'name':'Ens','format':'i','dimension_tuple':(('Ens',)),'data':np.array(data['ens']),'units':'unitless','description':'Ensemble Number'}
    v[5]={'name':'InitDate','format':'f','dimension_tuple':(('InitDate',)),'data':data['idate'],'units':'Days since 01Jan0000',\
            'description':'Date and time of when the model was initialized'}

    d[0]={'name':'Fcst','length':len(data['lead'])}
    d[1]={'name':'Ens','length':len(data['ens'])}
    d[2]={'name':'InitDate','length':len(data['idate'])}
    a[0]={'description':'Data from '+center,'history':'Created '+datetime.now().date().strftime('%Y%m%d')}
    write_netcdf(v,d,a,fn)
    return {'variables':v,'dimensions':d,'attributes':a}


def write_to_netcdf(filename,tmpfilename,newpreciparray,new_idates,old_idates,all_idates,cid,ens,missingval,fdat,codepath):
	#convert idate lists to matlab datenumbers (days since jan 1 0000)
	oldidns=[float]*len(old_idates)
	newidns=[float]*len(new_idates)
	sdn_out=[float]*len(all_idates)
	edn_out=[float]*len(all_idates)
	idn_out=[float]*len(all_idates)
	for i,idat in enumerate(old_idates):
		oldidns[i]=grid_utils.datetime2matlabdn(idat)
	for i,idat in enumerate(new_idates):
		newidns[i]=grid_utils.datetime2matlabdn(idat)
	for i,idat in enumerate(all_idates):
		f=definitions.forecast_def(idat,fdat,0)
		sdn_out[i]=grid_utils.datetime2matlabdn(f['sdate'])
		edn_out[i]=grid_utils.datetime2matlabdn(f['edate'])
		idn_out[i]=grid_utils.datetime2matlabdn(f['idate'])

	if os.path.isfile(filename):
		#open netcdf file
		f = S.NetCDFFile(filename,"r")
	
		#read netcdf data to append
		pcp=f.variables["Forecast Precip"][:]
        	idns=f.variables["InitializationDate"][:]

		#Get values from original netcdf file that are not missing
		vals2retain=np.in1d(idns,oldidns)
		pcpold=np.squeeze(pcp[vals2retain,:,:])

		#Concatinate all the data together then sort based on the initialization date
		pcpall=np.concatenate((pcpold,newpreciparray),0)
		idnall=np.concatenate((oldidns,newidns),0)
		pcp_out=pcpall[np.argsort(idnall),:,:]
		idn_out2=np.sort(idnall)
		f.close()

		f2=S.NetCDFFile(tmpfilename,mode='w')
		f2.createDimension('Number of Catchments',len(cid))
		f2.createDimension('Number of Ensemble Members',len(ens))
		f2.createDimension('Days',len(idn_out))
		fp=f2.createVariable('Forecast Precip','f',('Days','Number of Ensemble Members','Number of Catchments'))
		fcid=f2.createVariable('Catchment ID','i',('Number of Catchments',))
		fsd=f2.createVariable('StartDate','f',('Days',))
		fid=f2.createVariable('InitializationDate','f',('Days',))
		fed=f2.createVariable('EndDate','f',('Days',))
		fens=f2.createVariable('Ensembles','i',('Number of Ensemble Members',))
		#Add data
		fp[:]=pcp_out[:]
		fcid[:]=cid[:]
		fsd[:]=sdn_out[:]
		fid[:]=idn_out[:]
		fed[:]=edn_out[:]
		fens[:]=ens[:]
		f2.close()
	 	os.rename(tmpfilename,filename)	

	else:
		f=S.NetCDFFile(filename,mode='w')
		f.createDimension('Number of Catchments',len(cid))
		f.createDimension('Number of Ensemble Members',len(ens))
		f.createDimension('Days',len(idn_out))
		fp=f.createVariable('Forecast Precip','f',('Days','Number of Ensemble Members','Number of Catchments'))
		fcid=f.createVariable('Catchment ID','i',('Number of Catchments',))
		fsd=f.createVariable('StartDate','f',('Days',))
		fid=f.createVariable('InitializationDate','f',('Days',))
		fed=f.createVariable('EndDate','f',('Days',))
		fens=f.createVariable('Ensembles','i',('Number of Ensemble Members',))
		#Add data
		fp[:]=newpreciparray[:]
		fcid[:]=cid[:]
		fsd[:]=sdn_out[:]
		fid[:]=idn_out[:]
		fed[:]=edn_out[:]
		fens[:]=ens[:]
		f.close()

def scan_netcdf(filename,idatelist,missingval):
	#Find dates with data missing in the netcdf file and returns a list with these dates
        missingdates=[]
	fulldates=[]
        if(os.path.isfile(filename)):
                f=Nio.open_file(filename,"r")
                ncpcp=f.variables["Forecast Precip"][:]
                ncdates=f.variables["InitializationDate"][:]
		f.close()
                for idat in idatelist:
                	date_found=False
                       	mdn = grid_utils.datetime2matlabdn(idat)
                        if mdn in ncdates:
                                if ncpcp[(ncdates == mdn),0,0] != missingval:
                                        date_found=True
                        		fulldates.append(idat)
               		if not date_found:
                        	missingdates.append(idat)
        else:
                missingdates=idatelist
		fulldates=[]
	
        return {'missing':missingdates,'notmissing':fulldates} 

def read_netcdf(filename,idat,missingval):
	#Read pcp data for a particular date
        if(os.path.isfile(filename)):
                f=Nio.open_file(filename,"r")
                ncpcp=f.variables["Forecast Precip"][:]
                ncdates=f.variables["InitializationDate"][:]
                sdates=f.variables["StartDate"][:]
                edates=f.variables["EndDate"][:]
                cid=f.variables["Catchment ID"][:]
		f.close()
                mdn = grid_utils.datetime2matlabdn(idat)
                if mdn in ncdates:
                	if ncpcp[(ncdates == mdn),0,0] != missingval:
				pcp=np.squeeze(ncpcp[(ncdates == mdn),:,:])
				sdate=grid_utils.matlabdn2datetime(sdates[(ncdates == mdn)][0])
				edate=grid_utils.matlabdn2datetime(edates[(ncdates == mdn)][0])
               		else:		
				print "Missing precip values for date requested"
				pcp=None
			  	cid=None
				sdate=None
				edate=None				
		else:

			print "No precip available for date requested"
			pcp=None
		  	cid=None
			sdate=None
			edate=None				
        else:
		print "Can't fild netcdf file: "+filename
		pcp=None
	  	cid=None
		sdate=None
		edate=None				
	
        return {'pcp':pcp,'idate':idat,'cid':cid,'sdate':sdate,'edate':edate} 
