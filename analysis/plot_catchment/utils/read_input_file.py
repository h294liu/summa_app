import definitions
import numpy as np
import Nio
import os
import pdb

def open_file(filename,fileformat):
    #Takes a filedata dictionary and returns the open file object 
    if fileformat in ['grb2','netcdf','grb']:
        file=Nio.open_file(filename,"r")
    elif fileformat in ['binaryf4']:
        file=np.fromfile(filename,dtype='f4')
    return file
    
def read_in_1D_var(file,key,ref_dat=None,thresh=None,latdir=None):
    #Read in variable 
    data_available=True
    if key in file.variables:
        var=np.array(file.variables[key].get_value())
        if latdir=="NtoS":
            var=var[::-1]
        #Check data with reference data
        if ref_dat is not None:
            if not np.allclose(var,ref_dat,thresh):
                data_available=False
                print "Error: Unexpected ",key," data in file."
    else:
        data_availble=False
        print "Can not find ",key," variable"
    if data_available is False:
        var=None
    return var

def read_obs_file(indata):
    #Reads in data from a single grib or netcdf file
    centerdat=indata['centerdata']
    domaindat=indata['domaindata']
    filedat=indata['filedata']
    lat_dat=domaindat['lats']
    lon_dat=domaindat['lons']
    keys=filedat['keys']
    data_available=True

    #Try to open file
    try:
        file=open_file(filedat['filename'],centerdat['infile_format'])
    except:
        data_available=False
        print "Can not open file"

    if centerdat['infile_format'] in ['binaryf4']:
        if data_available:
            data=file[centerdat['header_length']:-1] #remove header information
            d=centerdat['dimensions']
            
            if centerdat['file_dimension_type']=='2D':
                nd=[]
                for dim in d:
                    if dim == keys['latkey']:
                        nd.append(len(lat_dat))
                    if dim == keys['lonkey']:
                        nd.append(len(lon_dat))
                #Check that the length of the data is correct
                if len(data) != nd[0]*nd[1]:
                    data_available==False
                    print "Incorrect number of data values"
                else:
                    var=data.reshape(nd[0],nd[1])
                    lon=lon_dat
                    lat=lat_dat
            else:
                print 'For now, observational binary data files must have just one lat-lon grid per file'
                data_available='False'

    elif centerdat['infile_format'] in ['grb2','netcdf','grb']:
        #Read in longitude
        if data_available:
            lon=read_in_1D_var(file,keys['lonkey'],ref_dat=lon_dat,thresh=.001)
        if lon is None:
            data_available = False
        #Read in latitude
        if data_available:
            lat=read_in_1D_var(file,keys['latkey'],ref_dat=lat_dat,thresh=.001,latdir=centerdat['latdir'])
        if lat is None:
            data_available = False
        #Read in time dimension if needed
        if centerdat['file_dimension_type']=='3D':
            if data_available:
                time=read_in_1D_var(file,keys['timekey'])
            if time is None:
                data_available = False
        #Read in Variable (e.g., Precipitation)
        if data_available:
            if keys["varkey"] in file.variables:
                var=file.variables[keys["varkey"]].get_value()
                d=file.variables[keys["varkey"]].dimensions
            else:
                data_availble=False
                print "Can not find precip variable"
        if data_available: #Fill masked array if it is initially masked
            if np.ma.isMaskedArray(var):
                var=np.ma.filled(var,fill_value=None)

    if data_available:
        #Reorder the precip dimensions if needed to [TIME,LAT,LON] or [LAT,LON]
        if centerdat['file_dimension_type']=='3D':
            order=(d.index(keys["timekey"]),d.index(keys["latkey"]),d.index(keys["lonkey"]))
            var=np.transpose(var,order)
            if centerdat["latdir"]=="NtoS":
                var=var[:,::-1,:]
        elif centerdat['file_dimension_type']=='2D':
            order=(d.index(keys["latkey"]),d.index(keys["lonkey"]))
            var=np.transpose(var,order)
            if centerdat["latdir"]=="NtoS":
                var=var[::-1,:]

        #Initialize masked variables
        var_dat=var
        var_mask=np.full_like(var,False,dtype=bool)

        #Mask out missing data or data that doesn't look good
        #var_mask[var_dat==centerdat["missingdata"]]=True
        #var_mask[np.isnan(var_dat)]=True
        #var_mask[var_dat<centerdat["mindata"]]=True
        #var_mask[var_dat>centerdat["maxdata"]]=True
    else:
    #if read failed mask whole arrays
        if centerdat['file_dimension_type']=='3D':
            var_dat=np.full((1,domaindat['nlats'],domaindat['nlons']),None)
            var_mask=np.full((1,domaindat['nlats'],domaindat['nlons']),True,dtype=bool)
        elif centerdat['file_dimension_type']=='2D':
            var_dat=np.full((domaindat['nlats'],domaindat['nlons']),None)
            var_mask=np.full((domaindat['nlats'],domaindat['nlons']),True,dtype=bool)
    #Create masked arrays for the variable and convert to mm/day at this stage.  All output should be in mm/day
    var=np.ma.array(var_dat*centerdat["multiplier"],mask=var_mask)
    var=np.ma.masked_invalid(var)
    var=np.ma.masked_equal(var,centerdat["missingdata"])
    var=np.ma.masked_less(var,centerdat["mindata"])
    var=np.ma.masked_greater(var,centerdat["maxdata"])
    var[np.ma.array(var<0)&np.ma.array(var>=centerdat["mindata"])]=0
    if centerdat['file_dimension_type']=='3D':
        return {'var':var,'time':time,'lat':lat_dat,'lon':lon_dat,'data_available':data_available,'dims':('time','lat','lon')}
    elif centerdat['file_dimension_type']=='2D':
        return {'var':var,'lat':lat_dat,'lon':lon_dat,'data_available':data_available,'dims':('lat','lon')}

def read_forecast_file(indata):
    #Reads in data from a single grib or netcdf file
    #Assume single initialization time 
    #Dimensions of output variable are consistent with file and domain definitions (see definitions.py) 
    #If the dimensions of the actual data don't match the expected dimensions, then they are padded with missing values, cropped or an error is given (in the case of lat and lon)
    #Latitude of the returned variable is from South to North
    #Also returns ensmemble,lead,latitude,longitude data
    #Variable data is a masked array
    centerdat=indata['centerdata']
    domaindat=indata['domaindata']
    filedat=indata['filedata']
    #Initialize output arrays
    if centerdat["file_dimension_type"]=='4D':
        var_dat=np.full((centerdat['nens'],centerdat['nfcst'],domaindat['nlats'],domaindat['nlons']),None,dtype=None)
        var_mask=np.full((centerdat['nens'],centerdat['nfcst'],domaindat['nlats'],domaindat['nlons']),False,dtype=bool)
        ens_dat=np.arange(centerdat['nens'])
        ens_mask=np.full((centerdat['nens']),False,dtype=bool)
        file_ens_mask=np.full((centerdat['nens']),False,dtype=bool)
        fcstlead_dat=centerdat['leads']
        fcstlead_mask=np.full((centerdat['nfcst']),False,dtype=bool)
        file_fcstlead_mask=np.full((centerdat['nfcst']),False,dtype=bool)
    elif centerdat["file_dimension_type"]=='3D_ens':
        var_dat=np.full((centerdat['nens'],domaindat['nlats'],domaindat['nlons']),None,dtype=None)
        var_mask=np.full((centerdat['nens'],domaindat['nlats'],domaindat['nlons']),False,dtype=bool)
        ens_dat=np.arange(centerdat['nens'])
        ens_mask=np.full((centerdat['nens']),False,dtype=bool)
        file_ens_mask=np.full((centerdat['nens']),False,dtype=bool)
    elif centerdat["file_dimension_type"]=='3D_lead':
        var_dat=np.full((centerdat['nfcst'],domaindat['nlats'],domaindat['nlons']),None,dtype=None)
        var_mask=np.full((centerdat['nfcst'],domaindat['nlats'],domaindat['nlons']),False,dtype=bool)
        fcstlead_dat=centerdat['leads']
        fcstlead_mask=np.full((centerdat['nfcst']),False,dtype=bool)
        file_fcstlead_mask=np.full((centerdat['nfcst']),False,dtype=bool)
    elif centerdat['file_dimension_type']=='2D':
        var_dat=np.full((domaindat['nlats'],domaindat['nlons']),None,dtype=None)
        var_mask=np.full((domaindat['nlats'],domaindat['nlons']),False,dtype=bool)
    #elif centerdat['file_dimension_type']=='3D':

    lat_dat=domaindat['lats']
    lon_dat=domaindat['lons']

    data_available=True

    #Try to open file
    try:
        file=open_file(filedat['filename'],centerdat['infile_format'])
    except:
        data_available=False
        print "Can not open file"

    #Read in longitude
    if data_available:
        keys=filedat['keys']
        if keys["lonkey"] in file.variables:
            lons=np.array(file.variables[keys["lonkey"]].get_value())
            if max(lons)>360:
                lons=lons-360
            if not np.allclose(lons,lon_dat,.001):
                data_availble=False
                print "Error: Unexpected longitude data in file."
        else:
            data_availble=False
            print "Can not find longitude variable"

    #Read in latitude
    if data_available:
        if keys["latkey"] in file.variables:
            lats=np.array(file.variables[keys["latkey"]].get_value())
            if centerdat["latdir"]=="NtoS":
                lats=lats[::-1]
            if not np.allclose(lats,lat_dat,.001):
                data_availble=False
                print "Error: Unexpected latitude data in file."
        else:
            data_availble=False
            print "Can not find latitude variable"

    if centerdat['file_dimension_type']=='4D':
    #Read in lead time if there is lead time in file
        if data_available:
            if keys["leadkey"] in file.variables:
                forecast_time=np.array(file.variables[keys["leadkey"]].get_value())
                nft=len(forecast_time)
                if nft != len(fcstlead_dat):
                    fcstlead_mask=np.invert(np.in1d(fcstlead_dat,forecast_time))
                    #file_fcstlead_mask is a mask showing which of the leads in the file are expected
                    #will be true there are extra leads in the file that are not expected
                    #same length as forecast_time
                    file_fcstlead_mask=np.invert(np.in1d(forecast_time,fcstlead_dat))
                    print "Warning: The forecast times don't match all expected times."
            else:
                data_availble=False
                print "Can not find forecast time variable"

    #Read in ensemble member data
        if data_available:
            if centerdat["ensdata"]=="one_variable":
                #If we expect to find the ensemble data all in one variable
                if keys["enskey"] in file.variables:
                    ne=len(file.variables[keys["enskey"]].get_value())
                else:
                    data_availble=False
                    print "Can not find ensemble variable"

            elif centerdat["ensdata"]=="separate_variables":
                #If we expect to find the ensemble data in separate variables
                #Then read the number of ensemble member variables that are in the file
                varlist=np.intersect1d(keys["varkeys"],file.variables.keys())
                ne=len(varlist)
                
            #ne is the number of ensemble members read in the file (files)
            #centerdat["nens"] is the number of ensemble members expected in the center definition file

            if ne>0: 
                if ne < centerdat["nens"]:
                    print "Warning: Fewer than expected Ensemble members"
                    #ens_mask is True for expected ensemble members that are missing 
                    file_ens_mask=np.full(ne,False,dtype=bool)
                    ens_mask[ne:]=True
                elif ne > centerdat["nens"]:
                    print "Warning: More than expected Ensemble members"
                    #ens_mask is True for ensemble members that are read in but not expected
                    #length of file
                    file_ens_mask=np.full(ne,False,dtype=bool)
                    file_ens_mask[centerdat["nens"]:]=True
            else:
                data_available==False
                print 'Error: Can not find any ensemble members'
        #Read in Variable (e.g., Precipitation)
        if data_available:
            if centerdat["ensdata"]=="one_variable": #All data is in the same variable
                if keys["varkey"] in file.variables:
                    var=file.variables[keys["varkey"]].get_value()
                    d=file.variables[keys["varkey"]].dimensions
                else:
                    data_availble=False
                    print "Can not find precip variable"
                    
            elif centerdat["ensdata"]=="separate_variables": #Each ensemble member is in a different variable
                mylist=[]
                for v in varlist:
                   mylist.append(file.variables[v].get_value())
                var=np.array(mylist)
                d=('ens',)+file.variables[varlist[0]].dimensions
                keys['enskey']='ens'
            #var=var*centerdat["multiplier"]


    elif centerdat['file_dimension_type']=='3D_lead':
    #Read in lead time if there is lead time in file
        if data_available:
            if keys["leadkey"] in file.variables:
                forecast_time=np.array(file.variables[keys["leadkey"]].get_value())
                nft=len(forecast_time)
                if nft != len(fcstlead_dat):
                    fcstlead_mask=np.invert(np.in1d(fcstlead_dat,forecast_time))
                    #file_fcstlead_mask is a mask showing which of the leads in the file are expected
                    #will be true there are extra leads in the file that are not expected
                    #same length as forecast_time
                    file_fcstlead_mask=np.invert(np.in1d(forecast_time,fcstlead_dat))
                    print "Warning: The forecast times don't match all expected times."
            else:
                data_availble=False
                print "Can not find forecast time variable"

        #Read in Variable (e.g., Precipitation)
        if data_available:
            if keys["varkey"] in file.variables:
                var=file.variables[keys["varkey"]].get_value()
                d=file.variables[keys["varkey"]].dimensions
            else:
                data_availble=False
                print "Can not find precip variable"
                    

    elif centerdat['file_dimension_type']=='3D_ens':
    #Read in ensemble data from file
        if data_available:
            if centerdat["ensdata"]=="one_variable":
                #If we expect to find the ensemble data all in one variable
                if keys["enskey"] in file.variables:
                    ne=len(file.variables[keys["enskey"]].get_value())
                else:
                    data_availble=False
                    print "Can not find ensemble variable"

            elif centerdat["ensdata"]=="separate_variables":
                #If we expect to find the ensemble data in separate variables
                #Then read the number of ensemble member variables that are in the file
                varlist=np.intersect1d(keys["varkeys"],file.variables.keys())
                ne=len(varlist)
                
            #ne is the number of ensemble members read in the file (files)
            #centerdat["nens"] is the number of ensemble members expected in the center definition file

            if ne>0: 
                if ne < centerdat["nens"]:
                    print "Warning: Fewer than expected Ensemble members"
                    #ens_mask is True for expected ensemble members that are missing 
                    file_ens_mask=np.full(ne,False,dtype=bool)
                    ens_mask[ne:]=True
                elif ne > centerdat["nens"]:
                    print "Warning: More than expected Ensemble members"
                    #ens_mask is True for ensemble members that are read in but not expected
                    #length of file
                    file_ens_mask=np.full(ne,False,dtype=bool)
                    file_ens_mask[centerdat["nens"]:]=True
            else:
                data_available==False
                print 'Error: Can not find any ensemble members'
        #Read in Variable (e.g., Precipitation)
        if data_available:
            if centerdat["ensdata"]=="one_variable": #All data is in the same variable
                if keys["varkey"] in file.variables:
                    var=file.variables[keys["varkey"]].get_value()
                    d=file.variables[keys["varkey"]].dimensions
                else:
                    data_availble=False
                    print "Can not find precip variable"
                    
            elif centerdat["ensdata"]=="separate_variables": #Each ensemble member is in a different variable
                mylist=[]
                for v in varlist:
                   mylist.append(file.variables[v].get_value())
                var=np.array(mylist)
                d=('ens',)+file.variables[varlist[0]].dimensions
                keys['enskey']='ens'

    elif centerdat["file_dimension_type"]=='2D':
        if data_available:
            print keys['varkey']
            if keys["varkey"] in file.variables:
                var=file.variables[keys["varkey"]].get_value()
                d=file.variables[keys["varkey"]].dimensions
            else:
                data_availble=False
                print "Can not find precip variable"

    #Make output masked arrays of the expected shape
    if data_available:
        var=np.ma.filled(var,fill_value=None)

        #Reorder the precip dimensions if needed to [ENS,FCST TIME,LAT,LON]
        if centerdat['file_dimension_type']=='4D':
            squeezedims=[]
            for myi,(numel,keyname) in enumerate(zip(var.shape,d)):
                if keyname not in [keys["enskey"],keys["leadkey"],keys["latkey"],keys["lonkey"]]:
                    if numel==1:
                        #squeeze singleton dimensions that are not part of the expected dimensions
                        var=np.squeeze(var,axis=myi)
                        squeezedims.append(myi)
                    elif numel>1:
                        data_available=False
                        print "Unexpected extra dimension in data"
            if len(squeezedims) > 0:            
                d=[val for i,val in enumerate(d) if i not in squeezedims] 
            order=(d.index(keys["enskey"]),d.index(keys["leadkey"]),d.index(keys["latkey"]),d.index(keys["lonkey"]))
            var=np.transpose(var,order)
            if centerdat["latdir"]=="NtoS":
                var=var[:,:,::-1,:]
            #Fill variable data array to fit the expected dimensions and mask out any ensemble members or forecast times that are missing
            #This step is needed in case ensemble members or forecast leads are missing
            ixgrid1=np.ix_(np.invert(ens_mask),np.invert(fcstlead_mask),\
		np.full(domaindat['nlats'],True,dtype=bool),np.full(domaindat['nlons'],True,dtype=bool))
            ixgrid2=np.ix_(np.invert(file_ens_mask),np.invert(file_fcstlead_mask),\
		np.full(domaindat['nlats'],True,dtype=bool),np.full(domaindat['nlons'],True,dtype=bool))
            var_dat[ixgrid1]=var[ixgrid2]
            var_mask[ens_mask,:,:,:]=True
            var_mask[:,fcstlead_mask,:,:]=True

        #Reorder the precip dimensions if needed to [ENS,LAT,LON]
        elif centerdat['file_dimension_type']=='3D_ens':
            squeezedims=[]
            for myi,(numel,keyname) in enumerate(zip(var.shape,d)):
                if keyname not in [keys["enskey"],keys["latkey"],keys["lonkey"]]:
                    if numel==1:
                        #squeeze singleton dimensions that are not part of the expected dimensions
                        var=np.squeeze(var,axis=myi)
                        squeezedims.append(myi)
                    elif numel>1:
                        data_available=False
                        print "Unexpected extra dimension in data"
            if len(squeezedims) > 0:            
                d=[val for i,val in enumerate(d) if i not in squeezedims] 
            order=(d.index(keys["enskey"]),d.index(keys["latkey"]),d.index(keys["lonkey"]))
            var=np.transpose(var,order)
            if centerdat["latdir"]=="NtoS":
                var=var[:,::-1,:]
            #Fill variable data array to fit the expected dimensions and mask out any ensemble members or forecast times that are missing
            #This step is needed in case ensemble members or forecast leads are missing
            ixgrid1=np.ix_(np.invert(ens_mask),\
		np.full(domaindat['nlats'],True,dtype=bool),np.full(domaindat['nlons'],True,dtype=bool))
            ixgrid2=np.ix_(np.invert(file_ens_mask),\
		np.full(domaindat['nlats'],True,dtype=bool),np.full(domaindat['nlons'],True,dtype=bool))
            var_dat[ixgrid1]=var[ixgrid2]
            var_mask[ens_mask,:,:]=True
        #Reorder the precip dimensions if needed to [FCST LEAD,LAT,LON]
        elif centerdat['file_dimension_type']=='3D_lead':
            squeezedims=[]
            for myi,(numel,keyname) in enumerate(zip(var.shape,d)):
                if keyname not in [keys["leadkey"],keys["latkey"],keys["lonkey"]]:
                    if numel==1:
                        #squeeze singleton dimensions that are not part of the expected dimensions
                        var=np.squeeze(var,axis=myi)
                        squeezedims.append(myi)
                    elif numel>1:
                        data_available=False
                        print "Unexpected extra dimension in data"
            if len(squeezedims) > 0:            
                d=[val for i,val in enumerate(d) if i not in squeezedims] 
            order=(d.index(keys["leadkey"]),d.index(keys["latkey"]),d.index(keys["lonkey"]))
            var=np.transpose(var,order)
            if centerdat["latdir"]=="NtoS":
                var=var[:,::-1,:]
            #Fill variable data array to fit the expected dimensions and mask out any ensemble members or forecast times that are missing
            #This step is needed in case ensemble members or forecast leads are missing
            ixgrid1=np.ix_(np.invert(fcstlead_mask),\
		np.full(domaindat['nlats'],True,dtype=bool),np.full(domaindat['nlons'],True,dtype=bool))
            ixgrid2=np.ix_(np.invert(file_fcstlead_mask),\
		np.full(domaindat['nlats'],True,dtype=bool),np.full(domaindat['nlons'],True,dtype=bool))
            var_dat[ixgrid1]=var[ixgrid2]
            var_mask[:,fcstlead_mask,:,:]=True

        #Reorder the precip dimensions if needed to [LAT,LON]
        elif centerdat['file_dimension_type']=='2D':
            order=(d.index(keys["latkey"]),d.index(keys["lonkey"]))
            var=np.transpose(var,order)
            if centerdat["latdir"]=="NtoS":
                var=var[::-1,:]
                var_dat=var

    else:
        if centerdat['file_dimension_type']=='4D':
            #Mask whole arrays if read failed
            var_mask=np.full((centerdat['nens'],centerdat['nfcst'],domaindat['nlats'],domaindat['nlons']),True,dtype=bool)
        elif centerdat['file_dimension_type']=='2D':
            var_mask=np.full((domaindat['nlats'],domaindat['nlons']),True,dtype=bool)
        elif centerdat['file_dimension_type']=='3D_ens':
            #Mask whole arrays if read failed
            var_mask=np.full((centerdat['nfcst'],domaindat['nlats'],domaindat['nlons']),True,dtype=bool)
        elif centerdat['file_dimension_type']=='3D_lead':
            #Mask whole arrays if read failed
            var_mask=np.full((centerdat['nens'],domaindat['nlats'],domaindat['nlons']),True,dtype=bool)

    #Create masked arrays for the variable
    var=np.ma.array(var_dat*centerdat['multiplier'],mask=var_mask)
    var=np.ma.masked_invalid(var)
    var=np.ma.masked_equal(var,centerdat["missingdata"])
    var=np.ma.masked_less(var,centerdat["mindata"])
    var=np.ma.masked_greater(var,centerdat["maxdata"])
    var[np.ma.array(var<0)&np.ma.array(var>=centerdat["mindata"])]=0
    if centerdat['file_dimension_type']=='4D':
        return {'var':var,'ens':ens_dat,'fcstlead':fcstlead_dat,'lat':lat_dat,'lon':lon_dat,'data_available':data_available,'dims':('ens','lead','lat','lon')}
    elif centerdat['file_dimension_type']=='3D_ens':
        return {'var':var,'ens':ens_dat,'lat':lat_dat,'lon':lon_dat,'data_available':data_available,'dims':('ens','lat','lon')}
    elif centerdat['file_dimension_type']=='3D_lead':
        return {'var':var,'fcstlead':fcstlead_dat,'lat':lat_dat,'lon':lon_dat,'data_available':data_available,'dims':('lead','lat','lon')}
    elif centerdat['file_dimension_type']=='2D':
        return {'var':var,'lat':lat_dat,'lon':lon_dat,'data_available':data_available}

def read_input_files(center,ingrid,idate=None,sdate=None,edate=None):
    centerdata=definitions.center_def(center)
    domaindata=definitions.grid_def(ingrid)
    indata={'centerdata':centerdata,'domaindata':domaindata,'date':idate}
    if (centerdata["type"] == 'forecast_onefile'): #This assumes latitude, longitude, lead time, and ensemble information in a single file
        filedata=definitions.input_filename_def(centerdata,ingrid,idate=idate) #list of data for all files that make up the forecast or observation
        indata['filedata']=filedata[0]
        if not (os.path.isfile(indata['filedata']['filename'])):
            data_available=False
            print "Can't find input file"
            vardata=None
        else:
            vardata=read_forecast_file(indata)

    elif (centerdata["type"] == 'forecast_manyfiles'): #This assumes lead time and/or ensemble members are in their own file
        filedata=definitions.input_filename_def(centerdata,ingrid,idate=idate) #list of data for all files that make up the forecast or observation
        nens=centerdata['nens']
        var=np.full((centerdata['nens'],centerdata['nfcst'],domaindata['nlats'],domaindata['nlons']),None,dtype=None)
        for filei,fn in enumerate(filedata): #Loop through files that make up this forecast
            print filei
            indata['filedata']=fn
            outdata=read_forecast_file(indata)
            if centerdata['file_dimension_type']=='3D_lead': #File data variable has 3 dimensions in it: Lat, Lon,Lead 
                var[fn['ens_i'],:,:,:]=outdata['var']
            elif centerdata['file_dimension_type']=='3D_ens': #File data variable has 3 dimensions in it: Lat, Lon,Ens 
                var[:,fn['lead_i'],:,:]=outdata['var']
            elif centerdata['file_dimension_type']=='2D': #File data variable has 2 dimensions in it: Lat and Lon
                var[fn['ens_i'],fn['lead_i'],:,:]=outdata['var']
        vardata=outdata
        vardata['var']=var
        vardata['ens']=range(centerdata['nens'])
        vardata['fcstlead']=centerdata['leads']
        vardata['dims']=('ens','lead','lat','lon')

    elif (centerdata["type"] == 'obs_onefile'):
        filedata=definitions.input_filename_def(centerdata,ingrid,sdate=sdate,edate=edate) #list of data for all files that make up the forecast or observation
        indata['filedata']=filedata[0]
        if not (os.path.isfile(indata['filedata']['filename'])):
            data_available=False
            print "Can't find input file"
            vardata=None
        else:
            vardata=read_obs_file(indata)

    elif (centerdata["type"] == 'obs_manyfiles'): #This assumes that there are multiple files to make one timestep
        filedata=definitions.input_filename_def(centerdata,ingrid,sdate=sdate,edate=edate) #list of data for all files that make up the forecast or observation
        var=np.ma.zeros((domaindata['nlats'],domaindata['nlons']))
        num2avg=0
        for fi,fd in enumerate(filedata):
            if not (os.path.isfile(fd['filename'])):
                    vardata=None
            else: 
                indata['filedata']=fd
                outdata=read_obs_file(indata)
                if centerdata['filedatedef'] in ['startaccum','endaccum']:
                    var=outdata['var']+var
                    num2avg=num2avg+1
                elif centerdata['filedatedef'] in ['midaccum']:
                    #if date of file is the middle of the accumulation period, we should
                    #equally average the first and last precipitation values instead of taking one or the other
                    ts2ind=len(filedata)-1
                    ts1ind=0
                    if fi in [ts1ind,ts2ind]:
                        var=outdata['var']/2.0+var
                        num2avg=num2avg+1/2.0
                    else:
                        var=outdata['var']+var
                        num2avg=num2avg+1
        if num2avg < ts2ind/2.0:
            #Only use data when more than half of timesteps are available, otherwise it will be missing
            vardata=None
        else:
            var=var/(1.0*num2avg)
            vardata=outdata
            vardata['var']=var

    return {'vardata':vardata,'config_info':indata}
