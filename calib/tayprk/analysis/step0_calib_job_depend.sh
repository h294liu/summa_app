#!/bin/bash
set -e

# This script is to create and submit mulctiple calibrations
type=calib
CASE=tayprk
root_dir=/glade/u/home/hongli/work/sharp/basins/$CASE

templates=(calib_tpl_var10 calib_tpl_route)
calib_trial_nums=(6 6) 
job_num_per_trials=(2 2)
job_file=qsub_DDS.sh

len=${#templates[@]}

for i in $(seq 0 $(($len-1))); do
    template=${templates[$i]}
    calib_trial_num=${calib_trial_nums[$i]}
    job_num_per_trial=${job_num_per_trials[$i]}
    template_dir=$root_dir/${type}_tpl/${template}

    for paral_id in $(seq 4 ${calib_trial_num}); do
        trial_name=${template/_tpl/}_trial${paral_id}
        calib_dir=$root_dir/${type}/$trial_name
        calib_job=${trial_name/trial/trl}
        echo ${trial_name}

        # (1) create folder
        if [ -e ${calib_dir} ]; then
            rm -rf ${calib_dir}
        fi
        cp -rP ${template_dir} ${calib_dir}

        # (2) remove unecessary folders
       # rm -rf ${calib_dir}/model/route/river_network #save space
       # ln -s ${template_dir}/model/route/river_network ${calib_dir}/model/route/river_network

        rm -rf ${calib_dir}/model/forcings/gmet_huc12_3hr_summa #save space
        ln -s ${template_dir}/model/forcings/gmet_huc12_3hr_summa ${calib_dir}/model/forcings/gmet_huc12_3hr_summa

        # (3) replace calib directory in several files
        cd $calib_dir
        for file in concat.py step0_define_mtp_bound.py step1_replace_nc_param.py step2_run_summa_route.sh step3_diagnostics.py model/settings/fileManager.3hr.txt; do
            sed -i "s~REPLACE_CALIB_DIR~${calib_dir}~g" $calib_dir/$file    
        done
        sed -i "s~REPLACE_CALIB_NAME~${calib_job}~g" $calib_dir/$job_file 

        # (5) submit job
        one=$(qsub $job_file)
        echo $one 
        for id in $(seq 2 ${job_num_per_trial}); do 
            next=$(qsub -W depend=afterany:$one $job_file)
            one=$next
        done
        sleep 3
        cd $root_dir
    done
done
