class HistoryManager:
    """Manages transcription history"""

    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.history = []
        self.load_history()

    def load_history(self):
        """Load history from configuration"""
        config = self.config_manager.load_config()
        self.history = config.get("history", [])

    def add_entry(self, text):
        """Add a new entry to history"""
        self.history.insert(0, text)  # Add at beginning
        self._save_history()

    def clear_history(self):
        """Clear all history"""
        self.history = []
        self._save_history()

    def _save_history(self):
        """Save history to configuration"""
        config = self.config_manager.load_config()
        config["history"] = self.history
        self.config_manager.save_config(config)
