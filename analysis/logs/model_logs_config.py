import json, os

class LogsConfig:
    latest_dir_name: str
    root_dir_path: str
    def __init__(self, path_to_json_config):
        config = json.load(open(path_to_json_config, 'rb'))
        self.latest_dir_name = config['latest_dir_name']
        self.root_dir_path = config['root_dir_path']

    @property
    def all_dir_paths(self) -> list[str]:
        return [os.path.join(self.root_dir_path, dir_name) for dir_name in os.listdir(self.root_dir_path)]

    @property
    def latest_dir_path(self) -> str:
        return os.path.join(self.root_dir_path, self.latest_dir_name)