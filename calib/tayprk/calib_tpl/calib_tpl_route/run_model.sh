#!/bin/bash
set -e

python step1_replace_nc_param.py
./step2_run_summa_route.sh
python step3_diagnostics.py

exit 0
