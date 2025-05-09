from typing import Dict, Any
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt

from plugins.plugin_interface import PluginInterface

class HelloWorldWidget(QWidget):
    """Widget for the Hello World plugin"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set up UI
        layout = QVBoxLayout(self)
        
        title = QLabel("Hello World Plugin")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        description = QLabel("A simple example plugin for the Secure GUI Platform")
        description.setStyleSheet("font-size: 16px; color: #7f8c8d;")
        layout.addWidget(description)
        
        # Add a button that does something
        self.hello_button = QPushButton("Say Hello")
        self.hello_button.clicked.connect(self.say_hello)
        layout.addWidget(self.hello_button)
        
        # Add a label to display the greeting
        self.greeting_label = QLabel("")
        self.greeting_label.setStyleSheet("font-size: 18px; color: #2980b9;")
        layout.addWidget(self.greeting_label)
        
        # Add a spacer
        layout.addStretch(1)
    
    def say_hello(self):
        """Show a greeting when the button is clicked"""
        self.greeting_label.setText("Hello, Secure GUI Platform User!")

class HelloWorldPlugin(PluginInterface):
    """
    A simple example plugin that displays a greeting
    """
    def initialize(self) -> bool:
        """Initialize the plugin"""
        self.widget = HelloWorldWidget()
        return True
    
    def get_name(self) -> str:
        """Return the plugin name"""
        return "Hello World"
    
    def get_version(self) -> str:
        """Return the plugin version"""
        return "1.0.0"
    
    def get_description(self) -> str:
        """Return plugin description"""
        return "A simple example plugin for the Secure GUI Platform"
    
    def get_widget(self) -> QWidget:
        """Return the main plugin widget"""
        return self.widget
    
    def shutdown(self) -> bool:
        """Clean up resources"""
        return True
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return plugin capabilities"""
        return {
            "has_settings": False,
            "has_permissions": False,
            "required_api_version": "1.0.0",
            "supported_platform": ["freebsd", "linux"],
            "category": "example"
        }