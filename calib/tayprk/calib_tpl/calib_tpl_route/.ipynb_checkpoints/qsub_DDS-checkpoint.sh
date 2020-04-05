#!/bin/bash
#PBS -N REPLACE_CALIB_NAME
#PBS -A P48500028
#PBS -q premium
#PBS -l select=1:ncpus=3:mpiprocs=3
#PBS -l walltime=12:00:00
#PBS -M hongli@ucar.edu
#PBS -j oe

mkdir -p /glade/scratch/hongli/temp
export TMPDIR=/glade/scratch/hongli/temp
export MPI_SHEPHERD=true
# ./step2_run_summa_route.sh

python step0_define_mtp_bound.py
./Ostrich.exe

# save OstOutput0.txt after calib
ost_output=OstOutput0.txt
output_num=$(ls -l OstOutput* |wc -l)
if [ $output_num -gt 0 ]; then cp ${ost_output} OstOutput${output_num}.txt; fi
