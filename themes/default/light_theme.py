from PyQt6.QtGui import QColor
from themes.theme_interface import ThemeInterface

class LightTheme(ThemeInterface):
    """Default light theme"""
    def __init__(self):
        super().__init__("Light", "Default light theme")
        
        # Set colors
        self.colors.primary = QColor("#1976D2")
        self.colors.secondary = QColor("#424242")
        self.colors.background = QColor("#FFFFFF")
        self.colors.text = QColor("#212121")
        self.colors.accent = QColor("#FF4081")
        self.colors.warning = QColor("#FFC107")
        self.colors.error = QColor("#F44336")
        self.colors.success = QColor("#4CAF50")
        
        # Set fonts
        self.fonts = {
            "default": "Roboto",
            "monospace": "Roboto Mono",
            "header": "Roboto Condensed"
        }
        
        # Set metrics
        self.metrics = {
            "padding": 8,
            "margin": 16,
            "border_radius": 4
        }