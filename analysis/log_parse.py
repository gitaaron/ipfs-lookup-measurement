import sys, getopt
from logs import parse
from logs.model_logs_config import LogsConfig


def execute(logs_config: LogsConfig, bucket_mode: str):
    if bucket_mode == 'ALL':
        parse.all(logs_config)
    elif bucket_mode == 'LATEST':
        parse.latest(logs_config)
    else:
        print('log_parse.py -b ALL|LATEST')
        sys.exit(2)



def main(argv):
    bucket_mode = ''

    try:
        opts, args = getopt.getopt(argv, "hb:", ["buckets="])
    except getopt.GetoptError:
        print('log_parse.py -b ALL|LATEST')
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-b", "--buckets"):
            bucket_mode = arg

    logs_config = LogsConfig('./log_config.json')

    execute(logs_config, bucket_mode)


if __name__ == '__main__':
    main(sys.argv[1:])
