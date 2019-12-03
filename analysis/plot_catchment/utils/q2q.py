import random
import numpy as N
import pdb
import time

def climperc_fast(valdum,climdum,randombnd=True):
    value = valdum
    clim = climdum
    NVAL = len(value)

    percent = N.empty(NVAL, dtype=float)
    percent[:] = N.nan

    # make sure climate data are sorted and real
    if clim.ndim > 1:
        clim = clim.flatten()
    clim = N.sort(clim)
    clim = clim.astype(float)
    clim = clim[~N.isnan(clim)]

    NCLIM = len(clim)
    lbnds=N.searchsorted(clim,value,side='left')
    hbnds=N.searchsorted(clim,value,side='right')
    mids=N.array([random.choice(N.arange(l,h+1,1)) for l,h in zip(lbnds,hbnds)])
    percent=(mids+1.0)/(NCLIM+1.0)
    return percent

def climperc(valdum,climdum,randombnd=True):
    value = valdum
    clim = climdum
    NVAL = len(value)

    percent = N.empty(NVAL, dtype=float)
    percent[:] = N.nan

    # make sure climate data are sorted and real
    if clim.ndim > 1:
        clim = clim.flatten()
    clim = N.sort(clim)
    clim = clim.astype(float)
    clim = clim[~N.isnan(clim)]

    NCLIM = len(clim)

    for i_v in range(NVAL):
        t=time.time()
        if N.isnan(value[i_v]):
            percent[i_v]=N.nan

        # check to see if percentile is possible
        elif value[i_v] < clim[0]:
#            print('WARNING: passed value below clim. obs')
            if randombnd:
                percent[i_v]= random.random()/(NCLIM+1.)
#                print('-- randomly-drawing lowest percentile')
#                print('  randomly selecting lowest %: '+str(percent[i_v]))
            else:
                percent[i_v]=1./(NCLIM+1.)
#                print('-- % set to lowest-possible clim val: '+str(percent[i_v]))
        else:
            if value[i_v] > clim[NCLIM-1]:
#                print('WARNING: passed value above clim. obs')
                if randombnd:
                    percent[i_v]=NCLIM/(NCLIM+1.)+random.random()/(NCLIM+1.)
#                    print('  randomly selecting highest %: '+str(percent[i_v]))
                else:
                    percent[i_v] = NCLIM/(NCLIM+1.)
#                    print('-- % set to highest-possible clim val: '+str(percent[i_v]))
            else:
                # first, determine bounding climate values
                # note: assuming climate values sorted in setting bounds
                lbnd = N.nan
                hbnd = N.nan
                lbnd=N.where(clim<=value[i_v])[0][-1]
                hbnd=N.where(clim>=value[i_v])[0][0]
                #These are the lines that take so much time
                #for i_clim in range(NCLIM):
                #    if clim[i_clim] <= value[i_v]:
                #        lbnd = i_clim
                #for i_clim in range(NCLIM-1,-1,-1):
                #    if clim[i_clim] >= value[i_v]:
                #        hbnd=i_clim
                #pdb.set_trace()
                # now accounting for multiple climate realizations w/ same value
                    # or if value[i_v] exactly equals climate value (i.e. lbnd=hbnd)
                    # by randomly sampling the interval
		if lbnd >= hbnd:
                    dum = lbnd
                    lbnd = hbnd
                    hbnd = dum
                    percent[i_v] = ((hbnd+1.)/(NCLIM+1.) - (lbnd+1.)/(NCLIM+1.))*random.random() + \
                    (lbnd+1.)/(NCLIM+1.)
                else:
                    pfrac = ( value[i_v] - clim[lbnd] ) / ( clim[hbnd] - clim[lbnd] )
                    percent[i_v] = (lbnd+1.)/(NCLIM+1.)+pfrac*((hbnd+1.)/(NCLIM+1.) - (lbnd+1.)/(NCLIM+1.))
    return(percent)

def climquan(climdum,percdum):
    clim = climdum
    percent = percdum
    NQUAN = len(percent)

    quan = N.empty(NQUAN,dtype = float)
    quan[:] = N.nan

    # make sure climate data is flattended, sorted and real
    clim = N.sort(clim)
    clim = clim.astype(float)
    clim = clim[~N.isnan(clim)]
    NCLIM = len(clim)

    for i_q in range(NQUAN):
        # Check to see if percentile is possible
        if N.isnan(percent[i_q]):
            quan[i_q]=N.nan
        elif percent[i_q]<1./(NCLIM+1):
#            print('WARNING: quant discret. below what can be specif by # of clim. obs')
#            print('  setting quantile to lowest clim. % & val: '+ str((1./(NCLIM+1.),clim[0])))
            quan[i_q] = clim[0]
        else:
            if percent[i_q] > NCLIM/(NCLIM+1.):
#                print('WARNING: quant discret. above what can be specif by # of clim. obs')
#                print('  setting quantile to largest clim. % & val: '+ str((NCLIM/(NCLIM+1.),clim[NCLIM-1])))
                quan[i_q] = clim[NCLIM-1]
            elif percent[i_q] == NCLIM/(NCLIM+1):
                quan[i_q] = clim[NCLIM-1]
            else:
                #linear interpolate
                iql = int(percent[i_q]*(NCLIM+1.))
                iqh = iql + 1
                # linearly interpolate to get quantile (unless upper-lower bnds are equal)
                pfrac = ( percent[i_q] - (iql/(NCLIM+1.)) ) / ( (iqh/(NCLIM+1.)) - (iql/(NCLIM+1.)) )
                quan[i_q] = clim[iql-1] + pfrac*(clim[iqh-1] - clim[iql-1])

    return(quan)



#;****************************************************************
#; q2q.py
#;
#; This function does a quantile-to-quantile mapping using the functions
#;   climperc.py and climquan.py. Note that if any of the values are
#;   below(above) any of the "climatological" values passed (i.e. what
#;   is possible given the climate data size), then resetting to
#;   lower(upper) bound
#;
#; program created Jan 11, 2008
#;*****************************************************************

def q2q(modldum,modlclimdum,obsclimdum):
    modldat = modldum      
    modlclimdat = modlclimdum
    obsclimdat = obsclimdum
    ts=time.time()
    modlperc = climperc_fast(modldat,modlclimdat)
    tf=time.time()
    obsdat = climquan(obsclimdat,modlperc)
    return(obsdat)
