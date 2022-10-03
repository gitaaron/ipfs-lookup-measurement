import json
import os

class LogsConfig:
    latest_dir_name: str
    root_dir_path: str
    def __init__(self, path_to_json_config):
        config = json.load(open(path_to_json_config, 'rb'))
        self.latest_dir_name = config['latest_dir_name']
        self.root_dir_path = config['root_dir_path']

    @property
    def latest_log_dir(self):
        return os.path.join(self.root_dir_path, self.latest_dir_name)
