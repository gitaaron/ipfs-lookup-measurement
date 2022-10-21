#!/usr/bin/env
set -e
echo "start download_logs..."
sh download_logs.sh
cd analysis
echo "parse log..."
SKIP_ERROR=TRUE python log_parse.py -b LATEST
echo "plot_all..."
python plot_all.py
cd ../share
echo "create_and_share_build..."
python create_and_share_build.py
