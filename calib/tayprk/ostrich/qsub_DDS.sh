#!/bin/bash
#PBS -N DDS
#PBS -A P48500028
#PBS -q premium
#PBS -l select=1:ncpus=16
#PBS -l walltime=12:00:00
#PBS -m abe
#PBS -M hongli@ucar.edu
#PBS -o ./DDS.out
#PBS -e ./DDS.err
mkdir -p /glade/scratch/hongli/temp
export TMPDIR=/glade/scratch/hongli/temp
export MPI_SHEPHERD=true
python define_mtp_bound.py
./Ostrich.exe

### Run the executable
### setenv MPI_SHEPHERD true
### mpiexec dplace -s 1 OstrichGCC > DDSlog

