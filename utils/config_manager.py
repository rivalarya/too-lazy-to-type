import json
import os

CONFIG_FILE = os.path.join(os.getcwd(), "config.json")


class ConfigManager:
    """Manages application configuration and persistence"""

    def __init__(self, config_file=CONFIG_FILE):
        self.config_file = config_file
        self.default_config = {
            "api_key": "",
            "record_hotkey": "ctrl+shift",
            "record_mode": "hold",
            "history": [],
            "stt_model": "gpt-4o-mini-transcribe"
        }

    def load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as file:
                return json.load(file)
        return self.default_config.copy()

    def save_config(self, config):
        """Save configuration to file"""
        with open(self.config_file, "w") as file:
            json.dump(config, file, indent=4)


# Initialize config file if it doesn't exist
if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "w") as file:
        json.dump(ConfigManager().default_config, file, indent=4)
