#!/usr/bin/env python3

import os
from subprocess import run
from pathlib import Path

nodes = {
    0: 'me_south_1',
    1: 'ap_southeast_2',
    2: 'af_south_1',
    3: 'us_west_1',
    4: 'eu_central_1',
    5: 'sa_east_1'
}

def getContainerDir(downloadDir):
    num = 0
    for d in os.listdir(downloadDir):
        try:
            newNum = int(d)
            if newNum > num:
                num = newNum
        except e:
            print(f"{d} is not an int")
            print(e)

    return str(num+1)

def writeAnalysisConfig(logFiles):
    f = open('analysis/log_config.json', 'w')
    f.write('[')
    isFirst = True
    for logFile in logFiles:
        if not isFirst:
            f.write(', ')
        isFirst = False
        f.write('"%s"' % logFile)
    f.write(']')

def downloadLogs(downloadDir, sinceHours):
    Path(downloadDir).mkdir(exist_ok=True, parents=True)
    container = getContainerDir(downloadDir)
    outputDir = os.path.join(downloadDir, container)
    Path(outputDir).mkdir(exist_ok=True, parents=True)

    logFiles = []
    for i in nodes:
        logFile = "%s/%s.log" % (outputDir, nodes[i])
        cmd = """ logcli query --limit=987654321 --since=%dh --output=jsonl '{host="node%d"}' > %s """ % (
            sinceHours, i, logFile)
        print(cmd)
        run(cmd, shell=True)
        logFiles.append(logFile)

    writeAnalysisConfig(logFiles)

if __name__ == "__main__":
    defaultAddr = "http://3.69.26.31:3100/"
    if(os.getenv("LOKI_ADDR")==None):
        print('Setting LOKI_ADDR to default %s' % defaultAddr)
        os.putenv("LOKI_ADDR", defaultAddr)

    downloadLogs(
        os.getenv('DOWNLOAD_DIR', '/tmp/dht_lookup/logs'),
        os.getenv('SINCE', 4)
    )
