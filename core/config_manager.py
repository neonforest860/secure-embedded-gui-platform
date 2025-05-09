import json
import os
import logging
from typing import Any, Dict, Optional
from pathlib import Path

class ConfigManager:
    """
    Manages application configuration with secure storage
    """
    def __init__(self, config_dir: Optional[str] = None):
        # Use provided config directory or default to user's home directory
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            self.config_dir = Path.home() / ".secure_gui_platform"
        
        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True, parents=True)
        
        # Path to main config file
        self.config_file = self.config_dir / "config.json"
        
        # Initialize config dictionary
        self.config: Dict[str, Dict[str, Any]] = {}
        
        # Load config or create default
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file or create default"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                logging.info(f"Configuration loaded from {self.config_file}")
            except (json.JSONDecodeError, IOError) as e:
                logging.error(f"Error loading configuration: {e}")
                self._create_default_config()
        else:
            self._create_default_config()
    
    def _create_default_config(self) -> None:
        """Create default configuration"""
        self.config = {
            "general": {
                "development_mode": False,
                "log_level": "INFO",
            },
            "appearance": {
                "theme": "default",
                "font_size": 12,
            },
            "security": {
                "plugin_verification": True,
                "admin_password_hash": "",  # Will be set during first run
                "session_timeout": 1800,  # 30 minutes
            },
            "plugins": {
                "enabled": [],
                "auto_update": False,
            }
        }
        self._save_config()
        logging.info("Created default configuration")
    
    def _save_config(self) -> None:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            logging.info(f"Configuration saved to {self.config_file}")
        except IOError as e:
            logging.error(f"Error saving configuration: {e}")
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        if section in self.config and key in self.config[section]:
            return self.config[section][key]
        return default
    
    def set(self, section: str, key: str, value: Any) -> None:
        """Set a configuration value"""
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section][key] = value
        self._save_config()
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get an entire configuration section"""
        return self.config.get(section, {})
    
    def set_section(self, section: str, values: Dict[str, Any]) -> None:
        """Set an entire configuration section"""
        self.config[section] = values
        self._save_config()