#!/bin/bash
set -e 

# user entry
# summaexec=/glade/u/home/andywood/proj/SHARP/models/summa/bin/summa.exe
summaexec=/glade/u/home/hongli/tools/summa/bin/summa.exe
routeexe=/glade/u/home/hongli/tools/mizuRoute/route/bin/route_runoff.develop.exe

ostrich=REPLACE_CALIB_DIR/
model=$ostrich/model
summa_output_3hr=output_output_timestep.nc
summa_output_24hr=output_day.nc #output_output_day.nc
summa_output_runoff=temp.nc

CASE=tayprk
Ngru=3
Nperjob=1 

sources=/glade/u/home/hongli/work/sharp/basins/sources
summa_ocontrol_file=outputControl.wb.txt
summa_ocontrol_3hr=$sources/outputControl.wb_3hr.txt
summa_ocontrol_24hr=$sources/outputControl.wb_24hr.txt
seg_file=$sources/step6_seg_$CASE.txt

# Step1. Run MPI summa
module load intel/18.0.5
cd $model/run/
cp $summa_ocontrol_24hr ../settings/$summa_ocontrol_file

# (1) MPI summa run
for gru in $(seq 1 $Ngru); do
    (${summaexec} -g $gru $Nperjob -r never -m fileManager.3hr.txt) &
done
wait

# # serially summa run
# ${summaexec} -r never -m fileManager.3hr.txt

# (2) concatenate GRU summa output
python $ostrich/concat.py

# Step2. Post-process summa daily putput
cd $model/output/gmet_huc12_3hr/

# (1) Add calender to time dimension of summa output
if [ -f $summa_output_runoff ]; then
   rm $summa_output_runoff
fi
ncatted -O -a calendar,time,o,c,'standard' -h $summa_output_24hr $summa_output_runoff

# (2) Overwrite fillvalue to all variables
ncatted -O -a _FillValue,,o,d,-999.0 -h $summa_output_runoff

# Step3. Mizuroute
# (1) create input for mizuRoute
# cd $model/route/input/
# if [ -e $summa_output_runoff ]; then rm $summa_output_runoff; fi
if [ -L $model/route/input/$summa_output_runoff ]; then rm $model/route/input/$summa_output_runoff; else echo 'not exist'; fi
ln -s $model/output/gmet_huc12_3hr/$summa_output_runoff $model/route/input/$summa_output_runoff

# (2) remove existing output
# cd $model/route/output/
for f in $model/route/output/*.nc; do
    if [ -e "$f" ]; then rm $f; fi
done

# (3) run mizuroute
module load gnu
cd $model/route/
${routeexe} setting/testCase_NHDPlus2_hru_runoff_mapping.control 

# (4) subset flow at gauge segment
cd $model/route/output/
seg_id=$(head -n 1 $seg_file)
ncrcat -O -d seg,$seg_id, -v time,reachID,IRFroutedRunoff -h test_*.nc all.nc

module load intel/18.0.5