#!/bin/bash
set -e

# This script is to create and submit mulctiple calibrations
template_folder='tayprk_calib_template'

cd ..
for paral_id in $(seq 3 10); do
    echo paral_${paral_id}
    folder_name=tayprk_calib_${paral_id}
    
    # create folder
    if [ -e ${folder_name} ]; then
        rm -rf ${folder_name}
    fi
    
    cp -r ${template_folder} ./${folder_name}
    
    cd ${folder_name}
    rm -rf route/mizuRoute #save space
    rm -rf route/mizuRoute_bkup #save space
    qsub qsub_DDS.sh
    sleep 1
    cd ../
    
done
cd scripts_hongli
