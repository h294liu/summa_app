#!/bin/bash

set -e

echo "saving input files for the best solution found ..."

if [ ! -e best ] ; then
    mkdir best
fi

if [ ! -e out_archive ] ; then
	mkdir out_archive
fi

cp nc_multiplier.txt best/nc_multiplier.txt
cp model/settings/trialParams.model_huc12_3hr.v1.nc best/trialParams.model_huc12_3hr.v1.nc
cp model/route/output/all.nc best/all.nc
cp Diagnostics.txt best/Diagnostics.txt

cp Ost*.txt out_archive/

exit 0

