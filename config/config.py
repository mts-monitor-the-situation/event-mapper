import pyyaml


class Config:
    """
    Configuration class to load and validate application settings.

    Example usage:
    ```
        config = Config("config.yaml")
        google_maps_api_key = config.get("google_maps_api_key")
    ```
    """

    def __init__(self, config_file):
        self.config_file = config_file
        self.config_data = self.load_config()
        self.validate()

    def load_config(self):
        try:
            with open(self.config_file, "r") as file:
                return pyyaml.safe_load(file) or {}
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {self.config_file}")
        except Exception as e:
            raise ValueError(f"Error loading config file {self.config_file}: {e}")

    def validate(self):
        required_keys = ["google_maps_api_key", "mongodb_connection_string", "redis_connection_string"]
        for key in required_keys:
            if key not in self.config_data:
                raise ValueError(f"Missing required config key: {key}")

    def get(self, key, default=None):
        return self.config_data.get(key, default)
