#!/bin/bash
set -e

root_dir=/glade/u/home/hongli/work/sharp/basins/tayprk
ofolder=step6_save_calib_results
if [ ! -d $root_dir/analysis/$ofolder ]; then mkdir $root_dir/analysis/$ofolder; fi

trial_folder_names=(calib_var10_trial1 calib_var10_trial2 calib_var10_trial3 calib_var10_trial4 calib_var10_trial5 calib_var10_trial6 \
calib_route_trial1 calib_route_trial2 calib_route_trial3 calib_route_trial4 calib_route_trial5 calib_route_trial6)
job_nums=(2 2 2 2 2 2 2 2 2 2 2 2)

len=${#trial_folder_names[@]}

for i in $(seq 0 $(($len-1))); do
    trial_folder_name=${trial_folder_names[$i]}
    job_num=${job_nums[$i]}
    calib_dir=$root_dir/calib/${trial_folder_name}
    echo $trial_folder_name
    
    # output folder
    otrial_folder=${trial_folder_name}
    otrial_dir=$root_dir/analysis/$ofolder/$otrial_folder
    if [ ! -d $otrial_dir ]; then mkdir -p $otrial_dir; fi                

    # save OstOutput.txt from calibration                       
    for job_id in $(seq 1 ${job_num}); do 
        ostfile=OstOutput${job_id}.txt
        cp -rP $calib_dir/$ostfile $otrial_dir/$ostfile
    done
    
    # save best results 
    cp -rP $calib_dir/best $otrial_dir/

done