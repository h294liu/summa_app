#!/bin/bash
set -e

# make a job list to run 52 parallel summa
# Note: Make sure there is / in end of routeoutdir

# user entry
summaexec=/glade/u/home/andywood/proj/SHARP/models/new/summa/bin/summa.exe
jobfile=joblist.run_summa.txt
Nhru=52
Nperjob=1

if [ -e $jobfile ]; then rm $jobfile; fi

for hru_id in $(seq 1 $Nhru); do
    echo $summaexec -g $hru_id $Nperjob -r never -m fileManager.3hr.txt  >> $jobfile
done

exit 0
