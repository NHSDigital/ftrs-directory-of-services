import os
import yaml

class Config:
    def __init__(self):
        """Load YAML configuration file."""
        config_file = os.path.join(os.path.dirname(__file__), "config.yaml")

        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Configuration file not found: {config_file}")

        with open(config_file, "r") as file:
            self.config = yaml.safe_load(file)

        # Ensure 'environments' key exists
        env = self.config.get("environment")
        if not env or env not in self.config.get("environments", {}):
            raise ValueError(f"Invalid environment: {env}")

        self.env_config = self.config["environments"][env]

    def get(self, key):
        """Get a configuration value for the selected environment."""
        return self.env_config.get(key, None)

# Create a global config instance
config = Config()
