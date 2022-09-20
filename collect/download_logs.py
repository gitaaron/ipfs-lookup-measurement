#!/usr/bin/env python3

import os
from subprocess import run
from pathlib import Path
import json

nodes = {
    0: 'me_south_1',
    1: 'ap_southeast_2',
    2: 'af_south_1',
    3: 'us_west_1',
    4: 'eu_central_1',
    5: 'sa_east_1'
}

def getContainerDir(download_dir):
    num = 0
    for d in os.listdir(download_dir):
        try:
            newNum = int(d)
            if newNum > num:
                num = newNum
        except e:
            print(f"{d} is not an int")
            print(e)

    return str(num+1)

def writeAnalysisConfig(root_dir_path, latest_dir_name):
    f = open('analysis/log_config.json', 'w')
    f.write(json.dumps({'root_dir_path':root_dir_path, 'latest_dir_name':latest_dir_name}))
    f.close()

def downloadLogs(download_dir, sinceHours):
    Path(download_dir).mkdir(exist_ok=True, parents=True)
    container = getContainerDir(download_dir)
    output_dir = os.path.join(download_dir, container)
    Path(output_dir).mkdir(exist_ok=True, parents=True)

    for i in nodes:
        logFile = "%s/%s.log" % (output_dir, nodes[i])
        cmd = """ logcli query --limit=987654321 --since=%dh --output=jsonl '{host="node%d"}' > %s """ % (
            sinceHours, i, logFile)
        print(cmd)
        #run(cmd, shell=True)

    writeAnalysisConfig(download_dir, container)

if __name__ == "__main__":
    defaultAddr = "http://3.69.26.31:3100/"
    if(os.getenv("LOKI_ADDR")==None):
        print('Setting LOKI_ADDR to default %s' % defaultAddr)
        os.putenv("LOKI_ADDR", defaultAddr)

    downloadLogs(
        os.getenv('DOWNLOAD_DIR', '/tmp/dht_lookup/logs'),
        os.getenv('SINCE', 4)
    )
