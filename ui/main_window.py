from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt

from ui.sidebar import Sidebar
from ui.content_area import ContentArea
from core.security_manager import SecurityManager
from core.config_manager import ConfigManager

class MainWindow(QMainWindow):
    """
    Main application window without decorations
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Get instances of managers
        self.config_manager = ConfigManager()
        self.security_manager = SecurityManager(self.config_manager)
        
        # Set up UI
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the main window UI"""
        # Remove window decorations
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        
        # Prevent Alt+F4 and other system shortcuts
        self.setWindowFlag(Qt.WindowType.WindowSystemMenuHint, False)
        
        # Set fullscreen mode
        self.showFullScreen()
        
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Create main layout
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create sidebar
        self.sidebar = Sidebar(self.security_manager)
        self.sidebar.setFixedWidth(250)
        from plugins.plugin_manager import PluginManager
        self.plugin_manager = PluginManager(self.config_manager, self.security_manager)
        
        # Create content area with plugin manager
        self.content_area = ContentArea(self.plugin_manager)
        
        # Connect sidebar section selection to content area
        self.sidebar.sectionSelected.connect(self.content_area.show_section)
        
        
        # Create content area
        self.content_area = ContentArea()
        
        # Connect sidebar section selection to content area
        self.sidebar.sectionSelected.connect(self.content_area.show_section)
        
        # Add widgets to layout
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.content_area)
    
    def closeEvent(self, event):
        # Prevent standard window closing
        event.ignore()
        
    def keyPressEvent(self, event):
        # Intercept key combinations that might exit the application
        if event.key() in [Qt.Key.Key_F4, Qt.Key.Key_Q] and \
           event.modifiers() & Qt.KeyboardModifier.AltModifier:
            event.ignore()
            return
        super().keyPressEvent(event)