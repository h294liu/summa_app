import numpy as np
from datetime import datetime
from datetime import timedelta
from dateutil.rrule import rrule, MONTHLY, DAILY
import scipy.sparse as sparse
from mpl_toolkits import basemap
import pdb
import definitions
import copy

def resample_xy_grid(xyslice,oldlat,oldlon,newlat,newlon,masked=False):
    #xyslice is a data grid of dimensions (oldlat,oldlon) 
    #newslice is a output data grid of dimensions (newlat,newlon)
    xout,yout=np.meshgrid(newlon,newlat)
    newslice=basemap.interp(xyslice,oldlon,oldlat,xout,yout,checkbounds=False,masked=masked,order=1)
    xout
    return newslice

def pad_xy_grid(xyslice,oldlat,oldlon,newlat,newlon,missingval):
    #xyslice is a data grid of dimensions (oldlat,oldlon) 
   #newlat newlon include oldlat and oldlon but include additional values at the same resolution
    #newslice is a output data grid of dimensions (newlat,newlon)
    newslice=np.full((len(newlat),len(newlon)),missingval)
    for i,lat in enumerate(newlat):
        for j,lon in enumerate(newlon):
            boolout=lat in oldlat and lon in oldlon
	    if boolout is True:
	    	val=xyslice[np.array([la==lat for la in oldlat]),np.array([lo==lon for lo in oldlon])]
	    	newslice[i,j]=val
    return newslice

def regrid_single_forecast(data,new_grid_name):
    #Data is a dictionary with 'var','fcstlead','ens','lat',lon'
    #var has the dimensions (ens,lead,lat,lon)
    #new_grid_name is a key that defines the new grid as defined in defitions.grid_def(new_grid_name)
    new_grid=definitions.grid_def(new_grid_name)
    newvar=np.full((len(data['ens']),len(data['fcstlead']),len(new_grid['lats']),len(new_grid['lons'])),None)
    for i,e in enumerate(data['ens']):
        for j,f in enumerate(data['fcstlead']):
    #        print str(e)+' '+str(f)
            xyslice=data['var'][i,j,:,:]
            newvar[i,j,:,:]=resample_xy_grid(xyslice,data['lat'],data['lon'],new_grid['lats'],new_grid['lons'])
    newdata=copy.copy(data)
    newdata['var']=newvar
    newdata['lat']=new_grid['lats']
    newdata['lon']=new_grid['lons']
    return newdata

def subset_grid(data,olddims,newdims):
# Takes a data array on a lat lon grid and chops it to a smaller domain
        mylist = [None]*len(data.shape)
	for i in range(len(data.shape)):
		mylist[i]=np.squeeze(np.where(np.in1d(np.around(olddims[i],decimals=4),np.around(newdims[i],decimals=4))))	
        indexA=np.ix_(*mylist)
        newdata=data[indexA]
        return newdata

def datetime2matlabdn(dt):
	# Converts a python datetime object to a matlab datenumber
	mdn=dt+timedelta(days=366)
	frac=(dt-datetime(dt.year,dt.month,dt.day,0,0,0)).seconds / (24.0 * 60.0 * 60.0)
	return mdn.toordinal() + frac
	
def matlabdn2datetime(dn):
# Converts a matlab datenumber to a python datetime object
	ord=int(np.floor(dn)-366)
	rem=(dn-np.floor(dn))*(24.0 * 60.0 * 60.0)
	return datetime.fromordinal(ord)+timedelta(seconds=rem)

def forecast_average(data,leads,forecast_list,accumtype,mindata=-1,maxdata=40000,missingdata=-999):
    #assume data is from a single initialization time and is of the form
    #ens,lead,lat,lon
    s=data.shape
    #replace input data from leadtimes with specific forecasts we want
    dataout=np.ma.zeros((s[0],len(forecast_list[:]),s[2],s[3]))
    endl=leads
    #6 hourly accumulation
    for j,fdat in enumerate(forecast_list[:]):
        if accumtype == 'accum1mo':
            lead=fdat[1]
            aper=fdat[0]
            start=lead
            end=lead+aper
            endl=leads+0.5
            startl=leads-0.5
            mask=np.array([sl>=start and el<=end for sl,el in zip(startl,endl)])
            #take average only if data is available for the full period 
            if sum(mask) == int(fdat[0]):
                dataout[:,j,:,:]=np.ma.mean(data[:,mask,:,:],1)
            else:
                dataout[:,j,:,:]=np.nan
                dataout=np.ma.masked_invalid(dataout)
        if accumtype == 'accum6hr':
            lead=fdat[1]*24
            aper=fdat[0]*24
            start=lead
            end=lead+aper
        #if the data is 6 hours accumulations
            startl=leads-6
            mask=np.array([sl>=start and el<=end for sl,el in zip(startl,endl)])
            #take average only if data is available for the full period 
            if sum(mask) == int(fdat[0]*4):
                dataout[:,j,:,:]=np.ma.sum(data[:,mask,:,:],1)
            else:
                dataout[:,j,:,:]=np.nan
                dataout=np.ma.masked_invalid(dataout)
        if accumtype == 'accum3hr':
            lead=fdat[1]*24
            aper=fdat[0]*24
            start=lead
            end=lead+aper
        #if the data is 3 hours accumulations
            startl=leads-3
            mask=np.array([sl>=start and el<=end for sl,el in zip(startl,endl)])
            #take average only if data is available for the full period
            if sum(mask) == int(fdat[0]*8):
                dataout[:,j,:,:]=np.ma.sum(data[:,mask,:,:],1)
            else:
                dataout[:,j,:,:]=np.nan
                dataout=np.ma.masked_invalid(dataout)
        if accumtype == 'accum1hr':
            lead=fdat[1]*24
            aper=fdat[0]*24
            start=lead
            end=lead+aper
        #if the data is 1 hours accumulations
            startl=leads-1
            mask=np.array([sl>=start and el<=end for sl,el in zip(startl,endl)])
            #take average only if data is available for the full period
            if sum(mask) == int(fdat[0]*24):
                dataout[:,j,:,:]=np.ma.sum(data[:,mask,:,:],1)
            else:
                dataout[:,j,:,:]=np.nan
                dataout=np.ma.masked_invalid(dataout)
        if accumtype == 'inst':
            lead=fdat[1]*24
            aper=fdat[0]*24
            start=lead
            end=lead+aper
        #if the data is instantaneous
            startl=leads
            mask=np.array([sl>=start and el<end for sl,el in zip(startl,endl)])
            #take average only if data is available for the full period 
            if sum(mask) == int(fdat[0]*4):
                dataout[:,j,:,:]=np.ma.average(data[:,mask,:,:],1)
            else:
                dataout[:,j,:,:]=np.nan
                dataout=np.ma.masked_invalid(dataout)
        if accumtype == 'accum':
            lead=fdat[1]*24
            aper=fdat[0]*24
            start=lead
            end=lead+aper
        #if the data is accumulation from the begining of the model run
            ind2=np.array([e == end for e in endl])
            ind1=np.array([e == start for e in endl])
            if sum(ind2)==1 and (sum(ind1)==1 or start==0):
                val2=np.ma.squeeze(data[:,ind2,:,:])
                if start == 0:
                    val1=np.ma.zeros((s[0],s[2],s[3]))
                    val1=np.ma.masked_where(np.ma.getmask(val2)==True,val1)
                else:
                    val1=np.ma.squeeze(data[:,ind1,:,:])
                dataout[:,j,:,:]=(val2-val1)/(1.0*fdat[0])
            else:
                dataout[:,j,:,:]=np.nan
                dataout=np.ma.masked_invalid(dataout)
    dataout=np.ma.masked_invalid(dataout)
    dataout=np.ma.masked_equal(dataout,missingdata)
    dataout=np.ma.masked_less(dataout,mindata)
    dataout=np.ma.masked_greater(dataout,maxdata)
    dataout[np.ma.array(dataout<0)&np.ma.array(dataout>=mindata)]=0
    return dataout

def collapse_dims(var,dims_in,dims_out,masked=True):
    #dims_in is a tuple with the names of the input dimensions
    #dims_out is a tuple with lists as its elements.  The lists
    #are comprised of the dimensions in dims_in and "allelse"
    #One list for every output dimension with all the dimensions
    #that are to be consolidated
    dms=var.shape
    out=np.full((len(dims_out)),1)
    wildout=np.product(dms)
    for i,dm in enumerate(dims_out):
        for j in dm:
            if j == 'allelse':
               wildi=i 
            else:
               if j in dims_in:
                   mask=np.array([p==j for p in dims_in])
                   dimval=float(np.array(dms)[mask])
                   out[i]=out[i]*dimval
                   wildout=wildout/dimval
    out[wildi]=wildout
    if masked == True:
        return np.ma.reshape(var,tuple(out))
    elif masked == False:
        return np.reshape(var,tuple(out))

def grid2catchments(cfmat,pcpin,thresh=1):
	#cfmat is the correspondence matrix with lats*lons* as the first dimension and # catch as the second 
	#pcpin is the input precip as a 2d array with lat*lons as the final dimension
        #thresh is the fraction of a catchment that needs to have data in order for the catchment to have data
        #for example, if thresh is .5 then 50% or more of the catchment area needs not to be missing for the
        #resulting catchment to not be filled with missing data.  Default is 1 so all data needs to be available
        #or else the catchment will have missing data
        thresh=thresh-0.001 #To account for rounding errors
        numerator=1.0*sparse.csr_matrix.dot(sparse.csr_matrix(pcpin.filled(0)),cfmat).todense()
        denominator=1.0*sparse.csr_matrix.dot(sparse.csr_matrix(1-np.ma.getmaskarray(pcpin)*1),cfmat).todense()
        catchpcp=np.array(numerator/denominator)
        catchpcp=np.ma.array(catchpcp,mask=(denominator<thresh))
	return catchpcp

def make_time_average(pcpin,infreq,ininterval,instartdates,outstartdates,outenddates):
#   pcpin 2 dimensions, the first is time
#freq is DAILY or HOURLY, etc - the frequency of the input data.
#interval is the interval - 6 for 6 hourly
    dumarr=np.full((len(outstartdates),pcpin.shape[1]),None)
    dummask=np.ones((len(outstartdates),pcpin.shape[1]))
    meanpcp=np.ma.masked_array(dumarr,mask=dummask)
    for i,(s,e) in enumerate(zip(outstartdates,outenddates)):
        if infreq is 'HOURLY':
            td=timedelta(hours=ininterval)
            dum=rrule(freq=HOURLY,interval=ininterval,dtstart=s,until=e-td)
        if infreq is 'DAILY':
            td=timedelta(days=ininterval)
            dum=rrule(freq=DAILY,interval=ininterval,dtstart=s,until=e-td)
        mylist=[d for d in dum]
        #Find indices of input data that match this list
        inds=np.array([sdt in mylist for sdt in instartdates])
        pcpwindow=pcpin[inds,:]
        mask=np.zeros((pcpwindow.shape[0],pcpwindow.shape[1]))
        mask[pcpwindow<-0.1]=1
        mask[pcpwindow>1000]=1
        mask[np.isnan(pcpwindow)]=1
        pcpwin=np.ma.array(pcpwindow,mask=mask)
        meanpcp[i,:]=np.ma.mean(pcpwin)
    return meanpcp

def find_common_dates(datelist1,datelist2):
    i1=np.array([d in datelist2 for d in datelist1])
    i2=np.array([d in datelist1 for d in datelist2])
    return i1,i2

#def pull_clim(outdate,clim_fn,percentile=50):
#    read_input_file.read_file(clim_fn,'netcdf')

def calc_clim_obs(archivepcp,archivedates,percentiles=[50],smoothfilter=np.ones(31)):
    #calculate climatology value at a given percentile level
    #dates in the smoothing window around the date to be displayed
    smoothwindow=len(smoothfilter)
    date1=datetime(2000,1,1)-timedelta(days=(smoothwindow-1.0)/2.0)
    refdates1=[date1+timedelta(days=d) for d in range(366+smoothwindow)]
    refdates1=np.array([d.replace(year=2000) for d in refdates1])
    date2=datetime(2000,1,1)
    refdates2=[date2+timedelta(days=d) for d in range(366)]
    alldates=np.array([d.replace(year=2000) for d in archivedates])
    pcp_percent=np.zeros((len(percentiles),len(refdates1)))
    outpcp=np.zeros((366,len(percentiles),))
    for i,dt in enumerate(refdates1):
        climdat=archivepcp[np.array([d==dt for d in alldates])].compressed()
        for j,percentile in enumerate(percentiles):
            pcp_percent[j,i]=np.percentile(climdat,percentile) 
    for i,dt in enumerate(refdates2):
        outpcp[i,:]=np.dot(pcp_percent[:,i:i+smoothwindow],smoothfilter)/np.float(np.sum(smoothfilter))
    return outpcp

def calc_clim4date_obs(outdate,archivepcp,archivedates,percentiles=[50],smoothfilter=np.ones(31)):
    #calculate climatology value at a given percentile level
    #dates in the smoothing window around the date to be displayed
    smoothwindow=len(smoothfilter)
    refdates=[outdate + timedelta(days=dd) for dd in np.arange(-1.0*(smoothwindow-1.0)/2.0,(smoothwindow-1)/2.0+1.0)]
    refdates=np.array([d.replace(year=2000) for d in refdates])
    alldates=np.array([d.replace(year=2000) for d in archivedates])
    pcp_percent=np.zeros((len(percentiles),len(refdates)))
    outpcp=np.zeros((len(percentiles),))
    for i,dt in enumerate(refdates):
        climdat=archivepcp[np.array([d==dt for d in alldates])].compressed()
        for j,percentile in enumerate(percentiles):
            pcp_percent[j,i]=np.percentile(climdat,percentile) 
    outpcp=np.dot(pcp_percent,smoothfilter)/np.float(np.sum(smoothfilter))
    return outpcp
