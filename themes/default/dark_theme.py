from PyQt6.QtGui import QColor
from themes.theme_interface import ThemeInterface

class DarkTheme(ThemeInterface):
    """Default dark theme"""
    def __init__(self):
        super().__init__("Dark", "Default dark theme")
        
        # Set colors
        self.colors.primary = QColor("#2196F3")
        self.colors.secondary = QColor("#757575")
        self.colors.background = QColor("#121212")
        self.colors.text = QColor("#FFFFFF")
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