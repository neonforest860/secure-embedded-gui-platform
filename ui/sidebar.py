from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, 
    QStackedWidget, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

class SidebarButton(QPushButton):
    """Custom button for sidebar"""
    def __init__(self, text, icon=None, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        if icon:
            self.setIcon(QIcon(icon))
        
        # Apply styling
        self.setMinimumHeight(50)
        self.setFont(QFont("Roboto", 10))
        self.setStyleSheet("""
            QPushButton {
                border: none;
                text-align: left;
                padding: 10px;
                color: #ecf0f1;
                background-color: transparent;
            }
            QPushButton:checked {
                background-color: #34495e;
                border-left: 4px solid #3498db;
            }
            QPushButton:hover:!checked {
                background-color: #3e5771;
            }
        """)

class Sidebar(QWidget):
    """Sidebar for navigation and admin tools"""
    
    # Signal emitted when a section is selected
    sectionSelected = pyqtSignal(str)
    
    def __init__(self, security_manager, parent=None):
        super().__init__(parent)
        self.security_manager = security_manager
        self.setup_ui()
        
        # Register for auth state changes
        self.security_manager.register_auth_callback(self.update_admin_visibility)
    
    def setup_ui(self):
        """Set up the sidebar UI"""
        # Create main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Add header
        header = QLabel("Secure GUI Platform")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setMinimumHeight(60)
        header.setStyleSheet("""
            background-color: #1a2530;
            color: white;
            font-weight: bold;
            font-size: 14px;
        """)
        layout.addWidget(header)
        
        # Create scroll area for buttons
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("background-color: #2c3e50;")
        
        # Create container for buttons
        button_container = QWidget()
        self.button_layout = QVBoxLayout(button_container)
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.button_layout.setSpacing(1)
        self.button_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll_area.setWidget(button_container)
        layout.addWidget(scroll_area, 1)  # 1 = stretch factor
        
        # Add regular navigation buttons
        self.add_navigation_buttons()
        
        # Add admin section (hidden by default)
        self.admin_widget = QWidget()
        self.admin_layout = QVBoxLayout(self.admin_widget)
        self.admin_layout.setContentsMargins(0, 10, 0, 0)
        
        admin_header = QLabel("Admin Tools")
        admin_header.setStyleSheet("color: #bdc3c7; padding: 5px 10px;")
        self.admin_layout.addWidget(admin_header)
        
        # Add admin buttons
        self.add_admin_buttons()
        
        # Add admin widget to main layout (hidden initially)
        self.admin_widget.setVisible(False)
        layout.addWidget(self.admin_widget)
        
        # Add login/logout button at bottom
        self.auth_button = QPushButton("Login as Admin")
        self.auth_button.setMinimumHeight(40)
        self.auth_button.clicked.connect(self.toggle_auth)
        self.auth_button.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: #1a2530;
                color: white;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
        """)
        layout.addWidget(self.auth_button)
    
    def add_navigation_buttons(self):
        """Add main navigation buttons"""
        buttons = [
            ("Dashboard", self.select_dashboard),
            ("Map", self.select_map),
            ("Terminal", self.select_terminal),
            ("Plugins", self.select_plugins),
        ]
        
        self.nav_buttons = {}
        for text, callback in buttons:
            button = SidebarButton(text)
            button.clicked.connect(callback)
            self.button_layout.addWidget(button)
            self.nav_buttons[text.lower()] = button
        
        # Set first button checked by default
        self.nav_buttons["dashboard"].setChecked(True)
    
    def add_admin_buttons(self):
        """Add admin section buttons"""
        buttons = [
            ("Settings", self.select_settings),
            ("Users", self.select_users),
            ("System", self.select_system),
            ("Logs", self.select_logs),
        ]
        
        self.admin_buttons = {}
        for text, callback in buttons:
            button = SidebarButton(text)
            button.clicked.connect(callback)
            self.admin_layout.addWidget(button)
            self.admin_buttons[text.lower()] = button
    
    def select_dashboard(self):
        """Select dashboard section"""
        self.uncheck_other_buttons("dashboard")
        self.sectionSelected.emit("dashboard")
    
    def select_map(self):
        """Select map section"""
        self.uncheck_other_buttons("map")
        self.sectionSelected.emit("map")
    
    def select_terminal(self):
        """Select terminal section"""
        self.uncheck_other_buttons("terminal")
        self.sectionSelected.emit("terminal")
    
    def select_plugins(self):
        """Select plugins section"""
        self.uncheck_other_buttons("plugins")
        self.sectionSelected.emit("plugins")
    
    def select_settings(self):
        """Select settings section"""
        self.uncheck_other_buttons("settings", admin=True)
        self.sectionSelected.emit("settings")
    
    def select_users(self):
        """Select users section"""
        self.uncheck_other_buttons("users", admin=True)
        self.sectionSelected.emit("users")
    
    def select_system(self):
        """Select system section"""
        self.uncheck_other_buttons("system", admin=True)
        self.sectionSelected.emit("system")
    
    def select_logs(self):
        """Select logs section"""
        self.uncheck_other_buttons("logs", admin=True)
        self.sectionSelected.emit("logs")
    
    def uncheck_other_buttons(self, selected, admin=False):
        """Uncheck all buttons except the selected one"""
        # Uncheck nav buttons
        for key, button in self.nav_buttons.items():
            if key != selected or admin:
                button.setChecked(False)
                
        # Uncheck admin buttons
        for key, button in self.admin_buttons.items():
            if key != selected or not admin:
                button.setChecked(False)
    
    def toggle_auth(self):
        """Toggle authentication state"""
        if self.security_manager.authorized:
            self.security_manager.logout()
        else:
            # In a real implementation, show a password dialog here
            # For now, we'll just authenticate with a dummy password
            self.security_manager.authenticate("admin")
    
    def update_admin_visibility(self, authorized):
        """Update visibility of admin section based on auth state"""
        self.admin_widget.setVisible(authorized)
        
        if authorized:
            self.auth_button.setText("Logout")
        else:
            self.auth_button.setText("Login as Admin")
            # Ensure no admin section is selected when logging out
            for key in self.nav_buttons:
                if self.nav_buttons[key].isChecked():
                    self.sectionSelected.emit(key)
                    return
            # If no button is checked, default to dashboard
            self.select_dashboard()