from typing import Dict, Any
from dataclasses import dataclass
from PyQt6.QtGui import QColor

@dataclass
class ThemeColors:
    """Colors defined in a theme"""
    primary: QColor
    secondary: QColor
    background: QColor
    text: QColor
    accent: QColor
    warning: QColor
    error: QColor
    success: QColor

class ThemeInterface:
    """Base class for all themes"""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.colors = ThemeColors(
            primary=QColor("#1976D2"),
            secondary=QColor("#424242"),
            background=QColor("#FFFFFF"),
            text=QColor("#212121"),
            accent=QColor("#FF4081"),
            warning=QColor("#FFC107"),
            error=QColor("#F44336"),
            success=QColor("#4CAF50")
        )
        self.fonts = {
            "default": "Roboto",
            "monospace": "Roboto Mono",
            "header": "Roboto Condensed"
        }
        self.metrics = {
            "padding": 8,
            "margin": 16,
            "border_radius": 4
        }
    
    def get_stylesheet(self) -> str:
        """Generate QSS stylesheet from theme properties"""
        # Basic application-wide styles
        stylesheet = f"""
            QWidget {{
                background-color: {self.colors.background.name()};
                color: {self.colors.text.name()};
                font-family: {self.fonts['default']};
            }}
            
            QLabel {{
                background: transparent;
            }}
            
            QPushButton {{
                background-color: {self.colors.secondary.name()};
                color: white;
                border: none;
                padding: {self.metrics['padding']}px;
                border-radius: {self.metrics['border_radius']}px;
            }}
            
            QPushButton:hover {{
                background-color: {self.colors.primary.name()};
            }}
            
            QLineEdit, QTextEdit, QPlainTextEdit {{
                border: 1px solid {self.colors.secondary.name()};
                border-radius: {self.metrics['border_radius']}px;
                padding: 6px;
                background-color: white;
                color: {self.colors.text.name()};
            }}
            
            QComboBox {{
                border: 1px solid {self.colors.secondary.name()};
                border-radius: {self.metrics['border_radius']}px;
                padding: 6px;
                background-color: white;
            }}
            
            QTabWidget::pane {{
                border: 1px solid {self.colors.secondary.name()};
                border-radius: {self.metrics['border_radius']}px;
            }}
            
            QTabBar::tab {{
                background-color: {self.colors.background.name()};
                padding: 8px 16px;
                margin-right: 2px;
            }}
            
            QTabBar::tab:selected {{
                background-color: {self.colors.primary.name()};
                color: white;
            }}
            
            QScrollBar:vertical {{
                border: none;
                background: {self.colors.background.name()};
                width: 10px;
                margin: 0px;
            }}
            
            QScrollBar::handle:vertical {{
                background: {self.colors.secondary.name()};
                min-height: 20px;
                border-radius: 5px;
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
                height: 0px;
            }}
        """
        return stylesheet
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert theme to serializable dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "colors": {
                "primary": self.colors.primary.name(),
                "secondary": self.colors.secondary.name(),
                "background": self.colors.background.name(),
                "text": self.colors.text.name(),
                "accent": self.colors.accent.name(),
                "warning": self.colors.warning.name(),
                "error": self.colors.error.name(),
                "success": self.colors.success.name()
            },
            "fonts": self.fonts,
            "metrics": self.metrics
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ThemeInterface':
        """Create theme from dictionary"""
        theme = cls(data["name"], data["description"])
        
        # Set colors
        theme.colors.primary = QColor(data["colors"]["primary"])
        theme.colors.secondary = QColor(data["colors"]["secondary"])
        theme.colors.background = QColor(data["colors"]["background"])
        theme.colors.text = QColor(data["colors"]["text"])
        theme.colors.accent = QColor(data["colors"]["accent"])
        theme.colors.warning = QColor(data["colors"]["warning"])
        theme.colors.error = QColor(data["colors"]["error"])
        theme.colors.success = QColor(data["colors"]["success"])
        
        # Set fonts
        theme.fonts = data["fonts"]
        
        # Set metrics
        theme.metrics = data["metrics"]
        
        return theme