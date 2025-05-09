#!/usr/bin/env python3
import sys
import logging
from PyQt6.QtWidgets import QApplication

from core.config_manager import ConfigManager
from ui.main_window import MainWindow

def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('secure_gui_platform.log')
        ]
    )

def main():
    """Application entry point"""
    # Set up logging
    setup_logging()
    logging.info("Starting Secure GUI Platform")
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Secure GUI Platform")
    app.setApplicationVersion("0.1.0")
    
    # Configure application behavior
    app.setQuitOnLastWindowClosed(False)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Enter event loop
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())