import sys, getopt
from models.model_logs_config import LogsConfig
from helpers import logs

def main(argv):
    bucket_mode = ''

    try:
        opts, args = getopt.getopt(argv, "hb:", ["buckets="])
    except getopt.GetoptError:
        print('log_parse.py -b ALL|LATEST')
        sys.exit(2)

    for opt, arg in opts:
        print(opt)
        if opt in ("-b", "--buckets"):
            print(arg)
            bucket_mode = arg


    if bucket_mode == 'ALL':
        logs_config = LogsConfig('./log_config.json')
        logs.generate_all_parsed_log_files_since_beginning(logs_config)
    elif bucket_mode == 'LATEST':
        logs_config = LogsConfig('./log_config.json')
        logs.generate_latest_parsed_log_files(logs_config)
    else:
        print('log_parse.py -b ALL|LATEST')
        sys.exit(2)


if __name__ == '__main__':
    main(sys.argv[1:])
