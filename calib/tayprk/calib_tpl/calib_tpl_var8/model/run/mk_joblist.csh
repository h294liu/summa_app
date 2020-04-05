#!/bin/csh
# A. Wood, 2018
# make a job list to run 36
# set for multiple years and months

set nHru = 3995   # specific to each domain
set nCores = 72   # specific to cluster (mult of 36 on cheyenne)
set jobsPerCore = `echo $nHru $nCores | awk '{printf("%d",$1/$2+1)}' `
set jobList = joblist.run_summa.3hr.txt
echo jobs per core = $jobsPerCore

echo -n > $jobList
set N = 0
while ($N < $nCores)
  set N1 = `echo $N | awk '{print $1*'$jobsPerCore'+1}' `
  set N2 = `echo $N1 $jobsPerCore $nHru | awk '{if(($1+$2)>$3){print $3-$1+1}else{print $2}}' `
  echo ./summa.dev.exe -g $N1 $N2 -r never -m fileManager.3hr.txt >> $jobList
  @ N ++
end
