#!/usr/bin/env python3
import sys
import logging
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QDir

from core.config_manager import ConfigManager
from core.security_manager import SecurityManager
from themes.theme_manager import ThemeManager
from plugins.plugin_manager import PluginManager
from ui.main_window import MainWindowUpdated

def setup_logging(config_manager=None):
    """Set up logging configuration"""
    # Set log level based on configuration
    log_level = logging.INFO
    if config_manager:
        level_name = config_manager.get("general", "log_level", "INFO")
        log_level = getattr(logging, level_name, logging.INFO)
    
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    # Set up logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(os.path.join(logs_dir, 'secure_gui_platform.log'))
        ]
    )

def main():
    """Application entry point"""
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Secure GUI Platform")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("Your Organization")
    
    # Create managers
    config_manager = ConfigManager()
    
    # Set up logging after config is available
    setup_logging(config_manager)
    logging.info("Starting Secure GUI Platform")
    
    # Create other managers
    security_manager = SecurityManager(config_manager)
    theme_manager = ThemeManager(config_manager)
    plugin_manager = PluginManager(config_manager, security_manager)
    
    # Apply theme
    theme_name = config_manager.get("appearance", "theme", "Light")
    theme_manager.apply_theme(theme_name)
    
    # Load plugins
    if config_manager.get("plugins", "auto_load", True):
        logging.info("Auto-loading enabled plugins")
        plugin_manager.load_enabled_plugins()
    
    # Create and show main window
    window = MainWindowUpdated(
        config_manager=config_manager,
        security_manager=security_manager,
        theme_manager=theme_manager,
        plugin_manager=plugin_manager
    )
    window.show()
    
    # Configure application behavior
    app.setQuitOnLastWindowClosed(False)
    
    # Enter event loop
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())