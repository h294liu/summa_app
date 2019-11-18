#!/bin/bash
set -e

cd model
python step0_replace_nc_param.py
./step1_run_summa_route.sh
python step2_calcualte_diagnostics.py

exit 0
