import numpy as np
import pdb

def write_csv(fn,p_all,cid,startdate,enddate,idate,accstr,center):
        #This output is only for catchments (not grids)
	#fn: output file name
        #p_all: precipitation data: shape (#ens,#cid)
	#Data for one particular lead and averaging period
        #startdate - start of target period
        #enddate - end of target period
        #idate - initialization date (if multi-model, of most recent forecast)
	#cid, catchment id
	outfile=open(fn,'w')
        mystr='polyid,rainfall,rainfallmin,rainfallmax,initializationDate,'+\
              'PeriodStart,PeriodEnd,SimilarDate,timeAverageLength\n'
        mystr= outfile.write(mystr)
        for ci,thiscid in enumerate(cid):
            if center in ['trmm','jaxa','merge']:
                pcpmean=p_all[ci]
                pcpmin=p_all[ci]
                pcpmax=p_all[ci]
            elif center in ['egrr','kwbc','cwao','lfpw','sbsj','rjtd','babj','ecmf',\
                    'CFSv2','CMC1','CMC2','GFDL','GFDLFLOR1','GFDLFLOR2','CCSM4','multimodel']:
        	ens=np.ma.sort(p_all[:,ci])
                ens=ens[np.ma.getmaskarray(ens)==False]
                nens=len(ens)
                val=np.ceil(nens/10.0)
                pcpmean=np.median(ens)
                pcpmax=ens[-1-int(val)+1]
                pcpmin=ens[int(val)-1]
            outfile.write("%4d,%7.4f,%7.4f,%7.4f,%10s,%10s,%10s,%10s,%6s\n" % \
                (thiscid,pcpmean,pcpmin,pcpmax,\
                idate.strftime('%Y%m%d%H'),startdate.strftime('%Y%m%d%H'),\
                enddate.strftime('%Y%m%d%H'),'N/A',accstr))
        outfile.close()
