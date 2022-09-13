#!/usr/bin/env python3

import os
from subprocess import run

num_nodes = 6


def downloadLogs():
    for i in range(0, num_nodes):
        cmd = """ logcli query --limit=987654321 --since=2000h --output=jsonl '{host="node%d"}' >%d.log """ % (
            i, i)
        run(cmd, shell=True)


if __name__ == "__main__":
    defaultAddr = "http://3.69.26.31:3100/"
    if(os.getenv("LOKI_ADDR")==None):
        print('Setting LOKI_ADDR to default %s' % defaultAddr)
        os.putenv("LOKI_ADDR", defaultAddr)
    downloadLogs()
