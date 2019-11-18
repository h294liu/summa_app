#!/bin/bash
set -e

# This script is to subset MiuRoute for a case study
routeexec=/glade/u/home/hongli/tools/mizuRoute/route/bin/route_runoff.develop.exe

data_dir=/glade/u/home/hongli/data/mizuRoute/
route_folder=upco_route
ndhplus_file=nhdplus2_conus_river_network.nc
subset_tmp=NHDPlus2_hru_runoff_mapping.control.subset_tmp
run_tmp=NHDPlus2_hru_runoff_mapping.control.run_tmp

model=/glade/u/home/hongli/work/sharp/basins/riogrd/model
route_dir=route
subset_file=testCase_NHDPlus2_hru_runoff_mapping.control.subset
run_file=testCase_NHDPlus2_hru_runoff_mapping.control

RouteLine_file=RioGrandeRiver_RouteLink__plusHRUs.nc
COMID=17906875 #obtained by viewing the usgs_gauge_conus.shp and Flowline_UCOplus.shp.

# Step1. subset RouteLink
# link MizuRoute exe
cd $model
if [ -d $route_dir ]; then rm -r $route_dir; fi
cp -r $data_dir/$route_folder $route_dir
cd $route_dir
ln -sfn $routeexec .

# link entire ndhplus file
cd ancillary_data/
ln -sfn $data_dir/$ndhplus_file .

# create subset control file
cd ../setting/
cp $data_dir/$subset_tmp ./$subset_file
sed -i "s/RouteLinkXXX.nc/${RouteLine_file}/g" $subset_file
sed -i "s/outletXXX/${COMID}/g" $subset_file

# dry-run subset
cd ../
${routeexec} setting/${subset_file}

# Step2. create run control file
# create run control file
cd setting/
cp $data_dir/$run_tmp ./$run_file
sed -i "s/RouteLinkXXX.nc/${RouteLine_file}/g" $run_file
sed -i "s/outletXXX/${COMID}/g" $run_file

