#!/usr/bin/env
set -e
echo "start download_logs..."
sh download_logs.sh
cd analysis
echo "parse log..."
python log_parse.py
echo "plot_all..."
python plot_all.py
cd ../share
echo "create_build..."
python create_build.py
echo "share_to_ipfs..."
sh add_to_ipfs.sh
