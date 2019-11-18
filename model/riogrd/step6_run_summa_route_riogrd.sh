#!/bin/bash
set -e 

# user entry
summaexec=/glade/u/home/andywood/proj/SHARP/models/new/summa/bin/summa.exe
routeexe=/glade/u/home/hongli/tools/mizuRoute/route/bin/route_runoff.develop.exe

model=/glade/u/home/hongli/work/sharp/basins/riogrd/model
summa_output_3hr=output_output_timestep.nc
summa_output_24hr=output_output_day.nc
summa_output_runoff=temp.nc

scripts=/glade/u/home/hongli/work/sharp/basins/scripts
summa_ocontrol_file=outputControl.wb.txt
summa_ocontrol_3hr=$scripts/outputControl.wb_3hr.txt
summa_ocontrol_24hr=$scripts/outputControl.wb_24hr.txt
seg_file=$scripts/step3_seg_riogrd.txt

cd $model

# Step1. Run summa
module load intel/18.0.5
cd run/
# check if 3hr output exists (in order to add hruId to daily output)
if [ ! -f output/gmet_huc12_3hr/$summa_output_3hr ]
then
    cp $summa_ocontrol_3hr ../settings/$summa_ocontrol_file
    ${summaexec} -r never -m fileManager.3hr.txt 
fi
cp $summa_ocontrol_24hr ../settings/$summa_ocontrol_file
${summaexec} -r never -m fileManager.3hr.txt 
cd ..

# Step2. Post-process summa daily putput
cd output/gmet_huc12_3hr/

# (1) Copy hruId from 3hr output to daily output
ncks -A -v hruId -h $summa_output_3hr $summa_output_24hr

# (2) Add calender to time dimension of summa output
if [ -f $summa_output_runoff ]; then
   rm $summa_output_runoff
fi
ncatted -a calendar,time,a,c,'standard' -h $summa_output_24hr $summa_output_runoff

# (3) Add fillvalue to all variables
ncatted -a _FillValue,,a,d,-999.0 -h $summa_output_runoff
cd ../../

# Step3. Mizuroute
cd route/
# (1) create input for mizuRoute
cd input/
if [ -e $summa_output_runoff ]; then rm $summa_output_runoff; fi
ln -s ../../output/gmet_huc12_3hr/$summa_output_runoff .
cd ../

# (2) remove existing output
cd output/
for f in ./*.nc; do
    if [ -e "$f" ]; then rm $f; fi
done
cd ../

# (3) run mizuroute
module load gnu
${routeexe} setting/testCase_NHDPlus2_hru_runoff_mapping.control 

# (4) subset flow at gauge segment
cd output/
seg_id=$(head -n 1 $seg_file)
ncrcat -O -d seg,$seg_id, -v time,reachID,IRFroutedRunoff -h test_20*.nc all.nc
cd ../../

module load intel/18.0.5

