from jobqueue_cli.storage import JSONStorage


class ConfigManager:
    def __init__(self, storage: JSONStorage):
        self.storage = storage
    
    def set_config(self, key: str, value: str):
        """Set a configuration value"""
        config = self.storage.load_config()
        
        # Try to convert value to appropriate type
        try:
            if value.lower() in ['true', 'false']:
                value = value.lower() == 'true'
            elif value.isdigit():
                value = int(value)
            elif value.replace('.', '').isdigit():
                value = float(value)
        except (ValueError, AttributeError):
            pass
        
        config[key] = value
        self.storage.save_config(config)
    
    def get_config(self, key: str, default=None):
        """Get a configuration value"""
        config = self.storage.load_config()
        return config.get(key, default)
    
    def get_all_config(self) -> dict:
        """Get all configuration values"""
        return self.storage.load_config()