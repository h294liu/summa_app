import matplotlib as mpl
mpl.use('Agg')
from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.pyplot as plt
#import pdb
import definitions
import grid_utils
from datetime import datetime
from datetime import timedelta
from descartes import PolygonPatch
import shapefile as shp

def basic_map_gridplot(data,lat,lon,fn,clevs=None,mycmap=None,countries=False,shapefile=None):
    fig=plt.figure()
    m=Basemap(projection='cyl',llcrnrlat=lat[0],urcrnrlat=lat[-1],\
            llcrnrlon=lon[0],urcrnrlon=lon[-1],resolution='c')
    m.drawcoastlines(linewidth=2)
    if shapefile is not None:
        try:
            m.readshapefile(shapefile,'catch_boundaries')
        except:
            # pdb.set_trace() AW
            print('unable to read shapefile with basemap')
    if countries is True:
        m.drawcountries(linewidth=2)
    x,y=m(lon,lat)
    xx,yy=np.meshgrid(x,y)
    if clevs is None:
        cs=m.contourf(xx,yy,data,extend='both')
    else:
        cs=m.contourf(xx,yy,data,clevs,extend='both')
    cbar=m.colorbar(cs,location='bottom',pad='5%')
    plt.savefig(fn)
    plt.close()

#def catchment_plot(data, datacid, shpname, joinid_index, fn, maxcolorval):
def catchment_plot(data, datacid, shpname, joinid_index, fn):
    #make a plot with 10 color gradations and a colorbar to go with it
    base=plt.cm.get_cmap('jet')
    color_list=base(np.linspace(0,1,10))
    jet10=base.from_list('jet10',color_list,10)
    plt.rcParams.update({'font.size': 6})
    #cmap=jet
    #ncar=plt.get_cmap('gist_ncar')
    #define 10 colors in the list
    #cmaplist=[jet(0),jet(25),jet(50),jet(75),jet(100),jet(125),jet(150),jet(175),jet(250),ncar(195)]
    #cmap=cmap.from_list('Custom cmap',cmaplist,10)
    #cmap=plt.cm.jet

    fig=plt.figure(figsize=(6,8))
    ax=fig.add_axes([.15,.3,.8,.7])
    #ax=fig.add_subplot(221)

    #maxcolorval=np.max(data)/10  # top of color bar
    datamax   = float(np.max(data))
    datamin   = float(np.min(data))
    datarange = datamax-datamin
    ncolorcat = 10    # use 10 for now (assumed in settings below

    # refmt data
    data=np.squeeze(data)

    # read shapefile
    polys=shp.Reader(shpname)

    # loop through polygons and plot each 'patch'
    i=0
    for r1,r2 in zip(polys.shapeRecords(),polys.records()):
#	if i<100:
	if i>=0:
                print("plotting", i)
		#shpcid=int(float(r2[joinid_index]))  # handle different var types for matching indices
		shpcid=r2[joinid_index]
		val=data[datacid==shpcid]
		if np.invert(np.isnan(val)):
			poly=r1.shape.__geo_interface__

                        f=(val-datamin)/datarange  # transform value into an index between 0 & 1

			if f[0] < 0:
			    patch=PolygonPatch(poly,fc='w',ec=None,alpha=0.8,hatch='//')
			if 0 <= f[0]:
                            # patch=PolygonPatch(poly,fc=jet10(f[0]),ec=jet10(f[0]),alpha=0.8)
			    patch=PolygonPatch(poly,fc=jet10(f[0]),ec='b',alpha=0.8,linewidth=0.05)
			ax.add_patch(patch)
	i=i+1
    ax.axis('scaled')
    # pdb.set_trace() AW

    # plot colorbar
    #fig2=plt.figure()

    m=np.zeros((1,10))
    for i in range(0,10):
        m[0,i]=(i)/10.0
    #xtickvals=[k*mymax for k in [0,.1,.2,.3,.4,.5,.6,.7,.8,.9,1]]
    xtickvals=[k*datarange+datamin for k in [0,.1,.2,.3,.4,.5,.6,.7,.8,.9,1]]
    xtickvals=(np.round(np.array(xtickvals)))


    ax2=fig.add_axes([.15,.15,.75,0.03])

#    ax2.imshow(m, cmap=jet10,interpolation='nearest',vmin=0,vmax=1,aspect=1)
    ax2.imshow(m, cmap=jet10,interpolation='nearest',vmin=0,vmax=1)
    ax2.set_yticks(np.arange(0))
    ax2.set_xticks(np.linspace(-0.5,9.5,11))
    ax2.set_xticklabels(xtickvals)
 
    plt.savefig(fn,dpi=200)
    plt.close()

    fn2=fn.split('.')[0]+'cbar.png'
    #plt.savefig(fn.split('.')[0]+'_cbar.png',dpi=200)
    #plt.close()
    #fig2=plt.figure()
    #ax.axis('scaled')
    #ax2=fig2.add_axes([0.1,0.1,.8,0.2])
    #m=np.zeros((1,10))
    #for i in range(0,10):
    #    m[0,i]=(i)/10.0
    #xtickvals=[k*mymax for k in [0,.1,.2,.3,.4,.5,.6,.7,.8,.9,1]]
    #ax2.imshow(m,cmap=jet10,interpolation='nearest',vmin=0,vmax=1,aspect=1)
    #ax2.set_yticks(np.arange(0))
    #ax2.set_xticks(np.linspace(-0.5,9.5,11))
    #ax2.set_xticklabels(xtickvals)
    #plt.savefig('cbar.png',dpi=200)
    #plt.close()


def catchment_plot_2sided(data,datacid,shpname,joinid_index,fn,maxcolorval):
    #make a plot with 10 color gradations and a colorbar to go with it
    base=plt.cm.get_cmap('seismic')
    color_list=base(np.linspace(0,1,21))
    seis21=base.from_list('seis21',color_list,21)
    #cmap=jet
    #ncar=plt.get_cmap('gist_ncar')
    #define 10 colors in the list
    #cmaplist=[jet(0),jet(25),jet(50),jet(75),jet(100),jet(125),jet(150),jet(175),jet(250),ncar(195)]
    #cmap=cmap.from_list('Custom cmap',cmaplist,10)
    fig=plt.figure()
    ax=fig.add_axes([0,0,1,1])
    #ax=fig.add_subplot(221)
    data=np.squeeze(data)
    #cmap=plt.cm.jet
    polys=shp.Reader(shpname)
    mymax=float(maxcolorval)
    for r1,r2 in zip(polys.shapeRecords(),polys.records()):
	shpcid=int(float(r2[joinid_index]))
        val=data[datacid==shpcid]
        poly=r1.shape.__geo_interface__
        f=val/mymax
        patch=PolygonPatch(poly,fc=seis21(f[0]),ec=seis21(f[0]),alpha=0.8)
        ax.add_patch(patch)
    ax.axis('scaled')
    plt.savefig(fn,dpi=200)
    plt.close()
#Plot colorbar
    fig2=plt.figure()
    ax2=fig2.add_axes([0.1,0.1,.8,0.2])
    m=np.zeros((1,10))
    for i in range(0,10):
        m[0,i]=(i)/10.0
    xtickvals=[k*mymax for k in [0,.1,.2,.3,.4,.5,.6,.7,.8,.9,1]]
    ax2.imshow(m,cmap=jet10,interpolation='nearest',vmin=0,vmax=1,aspect=1)
    ax2.set_yticks(np.arange(0))
    ax2.set_xticks(np.linspace(-0.5,9.5,11))
    ax2.set_xticklabels(xtickvals)
    plt.savefig(fn+'_cbar.png',dpi=200)
    plt.close()

def make_forecast_ts_plot(fn,data,forecast_list,idate,h,center):
    nt=len(forecast_list)
    pmedian=np.ma.zeros(nt)
    pmax=np.ma.zeros(nt)
    pmin=np.ma.zeros(nt)
    for i in range(nt):
        fdat=tuple(forecast_list[i])
        f=definitions.forecast_def_old(idate,fdat,h)
        ens=np.ma.squeeze(data[:,i])
        pmedian[i]=np.ma.mean(ens) #Change back to median
        pmax[i]=np.ma.max(ens)
        pmin[i]=np.ma.min(ens)
    fig,ax = plt.subplots()
    dts=np.arange(len(pmedian))
    ax.plot(dts,pmedian,color='red',linewidth=3.)
    ax.fill_between(dts,pmin,pmax,where=pmin<pmax,facecolor='grey',interpolate=True)
    xaxislabels=[definitions.forecast_def_old(idate,tuple(fdat),h)['sdate'].strftime('%m/%d')+\
            ' to '+definitions.forecast_def_old(idate,tuple(fdat),h)['edate'].strftime('%m/%d')\
            for fdat in forecast_list]
    ax.xaxis.set_ticklabels(xaxislabels,rotation=90)
    ax.set_title('Forecast '+center)
    ax.set_ylabel('Rainfall mm/day')
    if np.ma.max(pmax)<10:
        ax.set_ylim([0,10])
    else:
        ax.set_ylim([0,np.ma.max(pmax)])
    plt.tight_layout()
    plt.savefig(fn)
    plt.close()

def make_forecast_ts_txt(fn,data,datelist,catchname,\
        earliestdate=datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)):
    outfile=open(fn,'w')
    #outfile.write('%15s %15s\n' % ('Catchment Name: ', str(catchname)))
    #outfile.write('%9s, %7s,%4s,%7s\n' % ('Startdate','Median','Min','Max'))
    for ens,sd in zip(np.rollaxis(data,1),datelist):
        if sd>=earliestdate:
            nens=np.sum(np.invert(np.ma.getmaskarray(ens)))
            if nens>5:
                ens=ens[np.ma.getmaskarray(ens)==False]
                val=np.ceil(nens/10.0)
                pmedian=np.ma.median(ens)
                ens=np.sort(ens)
                pmax=ens[-1-int(val)+1]
                pmin=ens[int(val)-1]
                outfile.write('%10s,%7.4f,%7.4f,%7.4f\n' % (sd.strftime('%m-%d-%Y'),pmedian,pmin,pmax))
    outfile.close()

def make_obs_ts_txt(fn,climfn,data,startdates,catchname,numdays=15):
    outfile=open(fn,'w')
    #outfile.write('%15s %15s\n' % ('Catchment Name: ', str(catchname)))
    #outfile.write('%9s, %7s,%4s,%7s\n' % ('Startdate','Median','Min','Max'))
    outpcp=np.load(climfn)['outpcp']
    refdates=[datetime(2000,1,1)+timedelta(days=d) for d in range(366)]
    startdates2=np.array([ grid_utils.matlabdn2datetime(d) for d in startdates])
    for pcp,sd in zip(np.squeeze(data),startdates2):
        if sd>=datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)-timedelta(days=numdays):
            if type(pcp) is np.float32:
                pmedian=pcp
                #10th percentile
                pmin=outpcp[np.array([r==sd.replace(year=2000) for r in refdates]),0]
                #90th percentile
                pmax=outpcp[np.array([r==sd.replace(year=2000) for r in refdates]),2]
                outfile.write('%10s,%7.4f,%7.4f,%7.4f\n' % (sd.strftime('%m-%d-%Y'),pmedian,pmin,pmax))
    outfile.close()
