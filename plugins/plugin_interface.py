from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from PyQt6.QtWidgets import QWidget

class PluginInterface(ABC):
    """
    Base interface that all plugins must implement
    """
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the plugin"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Return the plugin name"""
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        """Return the plugin version"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Return plugin description"""
        pass
    
    @abstractmethod
    def get_widget(self) -> QWidget:
        """Return the main plugin widget"""
        pass
    
    @abstractmethod
    def shutdown(self) -> bool:
        """Clean up resources"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """Return plugin capabilities"""
        pass