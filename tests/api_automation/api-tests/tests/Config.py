import os
import yaml

class Config:
    def __init__(self):
        # Fix the path: Ensure it points to the correct location
        config_file = os.path.join(os.path.dirname(__file__), "Config.yaml")

        # Load the YAML configuration
        with open(config_file, "r") as file:
            self.config = yaml.safe_load(file)

    def get(self, key):
        return self.config.get(key, None)

config = Config()
