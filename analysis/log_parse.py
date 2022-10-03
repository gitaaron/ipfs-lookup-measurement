from models.model_logs_config import LogsConfig
from helpers import logs




if __name__ == '__main__':
    logs_config = LogsConfig('./log_config.json')
    logs.generate_parsed_log_files(logs.get_latest_log_region_files(logs_config))
