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
    os.putenv("LOKI_ADDR", "http://3.69.26.31:3100/")
    downloadLogs()
