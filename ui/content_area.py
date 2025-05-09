from PyQt6.QtWidgets import QWidget, QStackedWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt

from ui.widgets.terminal import SecureTerminal
# We'll import the PluginManagerWidget when needed to avoid circular imports

class ContentArea(QStackedWidget):
    """
    Main content area that displays different sections
    """
    def __init__(self, plugin_manager=None, parent=None):
        super().__init__(parent)
        self.plugin_manager = plugin_manager
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the initial UI"""
        # Create sections dictionary
        self.sections = {}
        
        # Dashboard section
        self.sections["dashboard"] = self.create_dashboard_section()
        
        # Map section
        self.sections["map"] = self.create_map_section()
        
        # Terminal section
        self.sections["terminal"] = self.create_terminal_section()
        
        # Plugins section
        self.sections["plugins"] = self.create_plugins_section()
        
        # Settings section
        self.sections["settings"] = self.create_admin_section("Settings", "System configuration")
        
        # Users section
        self.sections["users"] = self.create_admin_section("Users", "User management")
        
        # System section
        self.sections["system"] = self.create_admin_section("System", "System information and controls")
        
        # Logs section
        self.sections["logs"] = self.create_admin_section("Logs", "System logs and audit trails")
        
        # Add all sections to the stacked widget
        for widget in self.sections.values():
            self.addWidget(widget)
    
    def create_dashboard_section(self):
        """Create the dashboard section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        description = QLabel("Main system overview")
        description.setStyleSheet("font-size: 16px; color: #7f8c8d;")
        layout.addWidget(description)
        
        # Add dashboard widgets here
        
        # Add spacer
        layout.addStretch(1)
        
        return widget
    
    def create_map_section(self):
        """Create the map section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        title = QLabel("Map")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        description = QLabel("Interactive map interface")
        description.setStyleSheet("font-size: 16px; color: #7f8c8d;")
        layout.addWidget(description)
        
        # Add map placeholder
        map_placeholder = QFrame()
        map_placeholder.setFrameShape(QFrame.Shape.StyledPanel)
        map_placeholder.setStyleSheet("background-color: #ecf0f1; min-height: 300px;")
        layout.addWidget(map_placeholder)
        
        # Add spacer
        layout.addStretch(1)
        
        return widget
    
    def create_terminal_section(self):
        """Create the terminal section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        title = QLabel("Terminal")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        description = QLabel("Secure command shell")
        description.setStyleSheet("font-size: 16px; color: #7f8c8d;")
        layout.addWidget(description)
        
        # Add terminal widget
        terminal = SecureTerminal()
        layout.addWidget(terminal)
        
        return widget
    
    def create_plugins_section(self):
        """Create the plugins section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        title = QLabel("Plugins")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        description = QLabel("Plugin management")
        description.setStyleSheet("font-size: 16px; color: #7f8c8d;")
        layout.addWidget(description)
        
        # We'll add the plugin manager widget when a plugin manager is available
        if self.plugin_manager:
            from ui.widgets.plugin_manager_widget import PluginManagerWidget
            plugin_manager_widget = PluginManagerWidget(self.plugin_manager)
            layout.addWidget(plugin_manager_widget)
        else:
            placeholder = QLabel("Plugin manager not available")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(placeholder)
        
        return widget
    
    def create_admin_section(self, title_text, description_text):
        """Create an admin section with title and description"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        title = QLabel(title_text)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        description = QLabel(description_text)
        description.setStyleSheet("font-size: 16px; color: #7f8c8d;")
        layout.addWidget(description)
        
        # Add admin restricted notice
        admin_notice = QLabel("This section requires administrator privileges")
        admin_notice.setStyleSheet("color: #e74c3c; font-weight: bold; margin-top: 20px;")
        admin_notice.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(admin_notice)
        
        # Add spacer
        layout.addStretch(1)
        
        return widget
    
    def show_section(self, section_name):
        """Switch to the specified section"""
        if section_name in self.sections:
            self.setCurrentWidget(self.sections[section_name])
    
    def set_plugin_manager(self, plugin_manager):
        """Set or update the plugin manager"""
        self.plugin_manager = plugin_manager
        
        # Recreate plugins section with the manager
        old_plugins_section = self.sections["plugins"]
        index = self.indexOf(old_plugins_section)
        
        # Create new section
        new_plugins_section = self.create_plugins_section()
        self.sections["plugins"] = new_plugins_section
        
        # Replace in the stacked widget
        if index != -1:
            self.removeWidget(old_plugins_section)
            self.insertWidget(index, new_plugins_section)