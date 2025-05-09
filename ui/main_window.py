from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QDialog, QLineEdit, QLabel, QFormLayout, QDialogButtonBox,
    QMessageBox, QApplication
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QCloseEvent

from ui.sidebar import Sidebar
from ui.content_area import ContentArea

class LoginDialog(QDialog):
    """Dialog for authentication"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Administrator Login")
        self.setModal(True)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the login dialog UI"""
        layout = QFormLayout(self)
        
        # Add password field
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("Password:", self.password)
        
        # Add buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
        
        # Set focus to password field
        self.password.setFocus()

class MainWindowUpdated(QMainWindow):
    """
    Main application window without decorations and with updated components
    """
    def __init__(self, config_manager=None, security_manager=None, 
                 theme_manager=None, plugin_manager=None, parent=None):
        super().__init__(parent)
        
        # Store managers
        self.config_manager = config_manager
        self.security_manager = security_manager
        self.theme_manager = theme_manager
        self.plugin_manager = plugin_manager
        
        # Set up UI
        self.setup_ui()
        
        # Start session timeout timer if enabled
        if self.security_manager and self.config_manager:
            timeout = self.config_manager.get("security", "session_timeout", 1800)  # 30 minutes default
            if timeout > 0:
                self.timeout_timer = QTimer(self)
                self.timeout_timer.timeout.connect(self.check_session_timeout)
                self.timeout_timer.start(60000)  # Check every minute
    
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
        sidebar_width = 250
        if self.config_manager:
            sidebar_width = self.config_manager.get("appearance", "sidebar_width", 250)
        self.sidebar.setFixedWidth(sidebar_width)
        
        # Connect sidebar auth button to show login dialog
        self.sidebar.auth_button.clicked.connect(self.show_auth_dialog)
        
        # Create content area with all managers
        self.content_area = ContentArea(
            config_manager=self.config_manager,
            security_manager=self.security_manager,
            theme_manager=self.theme_manager,
            plugin_manager=self.plugin_manager
        )
        
        # Connect sidebar section selection to content area
        self.sidebar.sectionSelected.connect(self.content_area.show_section)
        
        # Connect security manager auth callback to update UI
        if self.security_manager:
            self.security_manager.register_auth_callback(self.on_auth_state_changed)
        
        # Add widgets to layout
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.content_area)
    
    def show_auth_dialog(self):
        """Show authentication dialog or log out"""
        if self.security_manager.authorized:
            # Log out
            self.security_manager.logout()
        else:
            # Show login dialog
            dialog = LoginDialog(self)
            if dialog.exec():
                password = dialog.password.text()
                success = self.security_manager.authenticate(password)
                
                if not success:
                    QMessageBox.warning(self, "Authentication Failed", "Invalid password")
    
    def on_auth_state_changed(self, authorized):
        """Handle authentication state changes"""
        # Update content area
        self.content_area.update_authorization(authorized)
        
        # Reset session timeout timer
        if hasattr(self, 'timeout_timer') and authorized:
            self.timeout_timer.start()
    
    def check_session_timeout(self):
        """Check if session has timed out"""
        if self.security_manager and self.security_manager.authorized:
            # Check if session has timed out
            if self.security_manager.check_session_timeout():
                # Session timed out, show notification and log out
                QMessageBox.information(self, "Session Timeout", "Your session has timed out due to inactivity.")
                self.security_manager.logout()
    
    def closeEvent(self, event: QCloseEvent):
        """Handle close event"""
        if hasattr(self, 'timeout_timer'):
            self.timeout_timer.stop()
        
        # Always ignore close events (window cannot be closed)
        event.ignore()
    
    def keyPressEvent(self, event):
        """Handle key events"""
        # Intercept key combinations that might exit the application
        if event.key() in [Qt.Key.Key_F4, Qt.Key.Key_Q] and \
           event.modifiers() & Qt.KeyboardModifier.AltModifier:
            event.ignore()
            return
            
        # Exit application on Alt+Ctrl+Shift+X (secret admin key combo)
        if event.key() == Qt.Key.Key_X and \
           event.modifiers() & Qt.KeyboardModifier.AltModifier and \
           event.modifiers() & Qt.KeyboardModifier.ControlModifier and \
           event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            if self.security_manager and self.security_manager.authorized:
                reply = QMessageBox.question(
                    self,
                    "Exit Application",
                    "Are you sure you want to exit the application?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    QApplication.quit()
            return
            
        super().keyPressEvent(event)