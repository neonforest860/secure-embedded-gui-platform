import os
import json
import logging
from typing import Dict, List, Optional
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette

from themes.theme_interface import ThemeInterface
from themes.default.light_theme import LightTheme
from themes.default.dark_theme import DarkTheme

class ThemeManager:
    """Manages theme loading, saving, and application"""
    def __init__(self, config_manager=None):
        self.config_manager = config_manager
        self.themes: Dict[str, ThemeInterface] = {}
        
        # Load built-in themes
        self.register_theme(LightTheme())
        self.register_theme(DarkTheme())
        
        # Load custom themes
        self.load_custom_themes()
        
        # Apply default theme
        if self.config_manager:
            default_theme = self.config_manager.get("appearance", "theme", "Light")
            self.apply_theme(default_theme)
    
    def register_theme(self, theme: ThemeInterface) -> None:
        """Register a theme"""
        self.themes[theme.name] = theme
        logging.info(f"Registered theme: {theme.name}")
    
    def load_custom_themes(self) -> None:
        """Load custom themes from user directory"""
        # Get custom themes directory
        if self.config_manager:
            themes_dir = self.config_manager.get("appearance", "themes_dir", None)
        else:
            themes_dir = None
            
        if not themes_dir:
            # Default to a themes directory in the user's home
            themes_dir = os.path.expanduser("~/.secure_gui_platform/themes")
        
        # Create directory if it doesn't exist
        themes_path = Path(themes_dir)
        if not themes_path.exists():
            themes_path.mkdir(parents=True, exist_ok=True)
            return  # No themes to load yet
        
        # Load themes from JSON files
        for theme_file in themes_path.glob("*.json"):
            try:
                with open(theme_file, 'r') as f:
                    theme_data = json.load(f)
                    theme = ThemeInterface.from_dict(theme_data)
                    self.register_theme(theme)
            except Exception as e:
                logging.error(f"Error loading theme from {theme_file}: {e}")
    
    def get_theme(self, name: str) -> Optional[ThemeInterface]:
        """Get a theme by name"""
        return self.themes.get(name)
    
    def get_all_themes(self) -> Dict[str, ThemeInterface]:
        """Get all registered themes"""
        return self.themes
    
    def get_theme_names(self) -> List[str]:
        """Get list of theme names"""
        return list(self.themes.keys())
    
    def apply_theme(self, theme_name: str) -> bool:
        """Apply a theme to the application"""
        theme = self.get_theme(theme_name)
        if not theme:
            logging.error(f"Theme not found: {theme_name}")
            return False
        
        # Apply stylesheet to application
        app = QApplication.instance()
        if app:
            app.setStyleSheet(theme.get_stylesheet())
            
            # Update color palette
            palette = app.palette()
            palette.setColor(QPalette.ColorRole.Window, theme.colors.background)
            palette.setColor(QPalette.ColorRole.WindowText, theme.colors.text)
            palette.setColor(QPalette.ColorRole.Button, theme.colors.secondary)
            palette.setColor(QPalette.ColorRole.ButtonText, theme.colors.text)
            palette.setColor(QPalette.ColorRole.Highlight, theme.colors.primary)
            app.setPalette(palette)
            
            # Save current theme if config manager is available
            if self.config_manager:
                self.config_manager.set("appearance", "theme", theme_name)
            
            logging.info(f"Applied theme: {theme_name}")
            return True
        
        logging.error("No QApplication instance found")
        return False
    
    def save_theme(self, theme: ThemeInterface) -> bool:
        """Save a theme to the themes directory"""
        # Get themes directory
        if self.config_manager:
            themes_dir = self.config_manager.get("appearance", "themes_dir", None)
        else:
            themes_dir = None
            
        if not themes_dir:
            # Default to a themes directory in the user's home
            themes_dir = os.path.expanduser("~/.secure_gui_platform/themes")
        
        # Create directory if it doesn't exist
        themes_path = Path(themes_dir)
        if not themes_path.exists():
            themes_path.mkdir(parents=True, exist_ok=True)
        
        # Save theme to JSON file
        try:
            theme_file = themes_path / f"{theme.name.lower().replace(' ', '_')}.json"
            with open(theme_file, 'w') as f:
                json.dump(theme.to_dict(), f, indent=4)
            
            # Register the theme
            self.register_theme(theme)
            
            logging.info(f"Saved theme to {theme_file}")
            return True
        except Exception as e:
            logging.error(f"Error saving theme: {e}")
            return False