#!/bin/bash
set -e

# extract noncontigous hru/gru summa model from a larger domain 
# by using Hongli modified Bart subset python script

# source directories for settings, forcings and run files
root=/glade/u/home/hongli/work/sharp/basins

SETTINGS0=$root/upco_huc12/settings/ 
FORCINGS0=$root/upco_huc12/forcings/gmet_huc12_3hr_summa/
RUN0=$root/upco_huc12/run/

CASE=riogrd
MODEL=model
setfolder=settings
forcefolder=forcings/gmet_huc12_3hr_summa
outputfolder=output/gmet_huc12_3hr

fmfile=fileManager.3hr.txt
replace_str1=UPCO
replace_str2=/glade/u/home/andywood/proj/SHARP/wreg/upco_huc12 

subset_py=$root/scripts/nc_subset_by_id.py
subset_gru_py=$root/scripts/nc_subset_by_gruid.py
huc_id_file=$root/scripts/step1_huc_id_riogrd.txt

# step 1. make folders
echo 'step 1. make folders'
cd $root
if [ ! -d $CASE ]; then mkdir $CASE; fi
cd $CASE

if [ ! -d $MODEL ]; then mkdir $MODEL; fi
cd $MODEL
modelpth=$PWD

if [ ! -d $setfolder ]; then mkdir $setfolder; fi
cd $setfolder

# clean existing files
for file in gru.nc hru.nc gru_subset.nc hru_subset.nc
do
  if [ -f "$file" ]; then rm $file; fi
done

# step 2. Attribute nc
echo 'step 2. attribute nc'
# (1) gru dim variables
# extract gru dim variables
ncks -h -v gruId $SETTINGS0/attributes.UPCO_huc12.nc gru.nc
# change nc dim from gru to hru
ncrename -h -O -d gru,hru gru.nc
# subset by hruId
python $subset_gru_py gru.nc $huc_id_file gru_subset.nc
# change nc dim back to hru
ncrename -h -O -d hru,gru gru_subset.nc

# (2) hru dim variables
# extract hru dim variables
ncks -h -x -v gruId $SETTINGS0/attributes.UPCO_huc12.nc hru.nc
# subset by hruId
python $subset_py hru.nc $huc_id_file hru_subset.nc

# (3) merge gru and hru dim variables
ncks -h -A -v gruId gru_subset.nc hru_subset.nc
cp hru_subset.nc attributes.${MODEL}_huc12.nc

# (4) delete useless nc files
for file in gru.nc hru.nc gru_subset.nc hru_subset.nc
do
  if [ -f "$file" ]; then rm $file; fi
done

# step 3. Parameter nc
echo 'step 3. parameter nc'
# (1) gru dim variables
echo '(1) gru dim variables'
# extract gru dim variables
ncks -h -v basin__aquiferBaseflowExp,basin__aquiferHydCond,basin__aquiferScaleFactor,routingGammaScale,routingGammaShape $SETTINGS0/trialParams.UPCO_huc12_3hr.v1.nc gru.nc
# add gruId variable from attribute.nc to gru.nc (in order to subset by gruId)
ncks -A -v gruId $SETTINGS0/attributes.UPCO_huc12.nc gru.nc
# change nc dim from gru to hru
ncrename -h -O -d gru,hru gru.nc
# subset by hruId
python $subset_gru_py gru.nc $huc_id_file gru_subset.nc
# change nc dim back to hru
ncrename -h -O -d hru,gru gru_subset.nc

# (2) hru dim variables
echo '(2) hru dim variables'
# extract hru dim variables
ncks -h -x -v basin__aquiferBaseflowExp,basin__aquiferHydCond,basin__aquiferScaleFactor,routingGammaScale,routingGammaShape $SETTINGS0/trialParams.UPCO_huc12_3hr.v1.nc hru.nc
# subset by hruId
python $subset_py hru.nc $huc_id_file hru_subset.nc

# (3) merge gru and hru dim variables
echo '(3) merge gru and hru dim variables'
ncks -h -A -v basin__aquiferBaseflowExp,basin__aquiferHydCond,basin__aquiferScaleFactor,routingGammaScale,routingGammaShape gru_subset.nc hru_subset.nc
cp hru_subset.nc trialParams.${MODEL}_huc12_3hr.v1.nc

# (4) delete useless nc files
echo '(4) delete useless nc files'
for file in gru.nc hru.nc gru_subset.nc hru_subset.nc
do
  if [ -f "$file" ]; then rm $file; fi
done

# step 4. Cold state nc
echo 'step 4. cold state nc'
python $subset_py $SETTINGS0/coldState.UPCO_huc12_3hr.v1.nc $huc_id_file ./coldState.${MODEL}_huc12_3hr.v1.nc

# step 5. Other txt
echo 'step 5. other text'
cp $SETTINGS0/fileManager*.txt $SETTINGS0/outputControl*.txt $SETTINGS0/localParams*.txt \
   $SETTINGS0/basinParams*.txt $SETTINGS0/modelDecisions*.txt $SETTINGS0/forcingFileList*.txt $SETTINGS0/*.TBL* ./

# step 6. revise fileManager.txt
echo 'step 6. revise fileManager.txt'
sed -i "s/${replace_str1}/${MODEL}/g" $fmfile
sed -i "s+${replace_str2}+${modelpth}+g" $fmfile
cd ../

# step 7: make new forcings and output directories
echo 'step 7. make new forcings and output directories'
mkdir -p $forcefolder
mkdir -p $outputfolder

# extract forcings files
echo 'step 8. extract forcing files'
cd $forcefolder
for F in $FORCINGS0/*.nc; do
  echo extracting from ${F##*/} #$F
  python $subset_py $F $huc_id_file ${F##*/}
  #ncatted -O -a units,time,o,c,'hours since 2000-01-01 00:00:00.0' -h ${F##*/}

done
cd ../../

# copy run directory and edit contents as needed to reset paths
cp -R $RUN0 ./run
