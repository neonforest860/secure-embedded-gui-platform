from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow

class SecureWindowManager:
    """
    Manages window creation with secure settings
    """
    @staticmethod
    def create_secure_window(window_class):
        """
        Factory method to create a window with security settings
        """
        window = window_class()
        
        # Apply security settings
        window.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        
        # Disable system menu to prevent Alt+F4 and other shortcuts
        window.setWindowFlag(Qt.WindowType.WindowSystemMenuHint, False)
        
        return window