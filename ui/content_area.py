from PyQt6.QtWidgets import QWidget, QStackedWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt

from ui.widgets.enhanced_terminal import EnhancedTerminal
from ui.widgets.map_widget import MapWidget
from ui.widgets.system_monitor import SystemMonitorPanel
from ui.widgets.log_panel import LogPanel
from ui.widgets.settings_panel import SettingsPanel
from ui.widgets.user_management import UserManagementPanel
from ui.widgets.plugin_manager_widget import PluginManagerWidget

class ContentArea(QStackedWidget):
    """
    Main content area that displays different sections based on sidebar selection
    """
    def __init__(self, config_manager=None, security_manager=None, theme_manager=None, plugin_manager=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.security_manager = security_manager
        self.theme_manager = theme_manager
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
        self.sections["settings"] = self.create_settings_section()
        
        # Users section
        self.sections["users"] = self.create_users_section()
        
        # System section
        self.sections["system"] = self.create_system_section()
        
        # Logs section
        self.sections["logs"] = self.create_logs_section()
        
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
        
        # Add system monitor for dashboard view
        system_monitor = SystemMonitorPanel()
        layout.addWidget(system_monitor)
        
        return widget
    
    def create_map_section(self):
        """Create the map section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create map widget
        map_widget = MapWidget()
        layout.addWidget(map_widget)
        
        return widget
    
    def create_terminal_section(self):
        """Create the terminal section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create enhanced terminal
        terminal = EnhancedTerminal(
            config_manager=self.config_manager,
            security_manager=self.security_manager
        )
        layout.addWidget(terminal)
        
        return widget
    
    def create_plugins_section(self):
        """Create the plugins section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Create plugin manager widget if plugin manager is available
        if self.plugin_manager:
            plugin_manager_widget = PluginManagerWidget(self.plugin_manager)
            layout.addWidget(plugin_manager_widget)
        else:
            # Placeholder if plugin manager is not available
            title = QLabel("Plugins")
            title.setStyleSheet("font-size: 24px; font-weight: bold;")
            layout.addWidget(title)
            
            description = QLabel("Plugin manager not available")
            description.setStyleSheet("font-size: 16px; color: #7f8c8d;")
            layout.addWidget(description)
        
        return widget
    
    def create_settings_section(self):
        """Create the settings section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Check if user is authorized
        if self.security_manager and not self.security_manager.authorized:
            # Unauthorized view
            title = QLabel("Settings")
            title.setStyleSheet("font-size: 24px; font-weight: bold;")
            layout.addWidget(title)
            
            description = QLabel("Administrative access required")
            description.setStyleSheet("font-size: 16px; color: #e74c3c;")
            layout.addWidget(description)
        else:
            # Create settings panel
            settings_panel = SettingsPanel(
                config_manager=self.config_manager,
                theme_manager=self.theme_manager
            )
            layout.addWidget(settings_panel)
        
        return widget
    
    def create_users_section(self):
        """Create the users section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Check if user is authorized
        if self.security_manager and not self.security_manager.authorized:
            # Unauthorized view
            title = QLabel("User Management")
            title.setStyleSheet("font-size: 24px; font-weight: bold;")
            layout.addWidget(title)
            
            description = QLabel("Administrative access required")
            description.setStyleSheet("font-size: 16px; color: #e74c3c;")
            layout.addWidget(description)
        else:
            # Create user management panel
            user_panel = UserManagementPanel(self.security_manager)
            layout.addWidget(user_panel)
        
        return widget
    
    def create_system_section(self):
        """Create the system section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Check if user is authorized
        if self.security_manager and not self.security_manager.authorized:
            # Unauthorized view
            title = QLabel("System")
            title.setStyleSheet("font-size: 24px; font-weight: bold;")
            layout.addWidget(title)
            
            description = QLabel("Administrative access required")
            description.setStyleSheet("font-size: 16px; color: #e74c3c;")
            layout.addWidget(description)
        else:
            # Create system monitor panel
            system_monitor = SystemMonitorPanel()
            layout.addWidget(system_monitor)
        
        return widget
    
    def create_logs_section(self):
        """Create the logs section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Check if user is authorized
        if self.security_manager and not self.security_manager.authorized:
            # Unauthorized view
            title = QLabel("Logs")
            title.setStyleSheet("font-size: 24px; font-weight: bold;")
            layout.addWidget(title)
            
            description = QLabel("Administrative access required")
            description.setStyleSheet("font-size: 16px; color: #e74c3c;")
            layout.addWidget(description)
        else:
            # Create log panel
            log_panel = LogPanel()
            layout.addWidget(log_panel)
        
        return widget
    
    def show_section(self, section_name):
        """Switch to the specified section"""
        if section_name in self.sections:
            self.setCurrentWidget(self.sections[section_name])
            
            # If section requires admin access, check authorization
            if section_name in ["settings", "users", "system", "logs"]:
                self.refresh_admin_section(section_name)
    
    def refresh_admin_section(self, section_name):
        """Refresh an admin section based on authorization status"""
        # Check if user is authorized
        is_authorized = self.security_manager and self.security_manager.authorized
        
        # Get current widget
        current_widget = self.sections[section_name]
        
        # Check if widget needs to be recreated
        is_admin_widget = isinstance(current_widget.layout().itemAt(0).widget(), (
            SettingsPanel, UserManagementPanel, SystemMonitorPanel, LogPanel
        ))
        
        if is_authorized and not is_admin_widget:
            # Recreate section with proper admin widget
            old_widget = self.sections[section_name]
            index = self.indexOf(old_widget)
            
            if section_name == "settings":
                new_widget = self.create_settings_section()
            elif section_name == "users":
                new_widget = self.create_users_section()
            elif section_name == "system":
                new_widget = self.create_system_section()
            elif section_name == "logs":
                new_widget = self.create_logs_section()
            
            # Update sections dictionary
            self.sections[section_name] = new_widget
            
            # Replace in the stacked widget
            self.removeWidget(old_widget)
            self.insertWidget(index, new_widget)
            self.setCurrentWidget(new_widget)
        
        elif not is_authorized and is_admin_widget:
            # Recreate section with unauthorized message
            old_widget = self.sections[section_name]
            index = self.indexOf(old_widget)
            
            if section_name == "settings":
                new_widget = self.create_settings_section()
            elif section_name == "users":
                new_widget = self.create_users_section()
            elif section_name == "system":
                new_widget = self.create_system_section()
            elif section_name == "logs":
                new_widget = self.create_logs_section()
            
            # Update sections dictionary
            self.sections[section_name] = new_widget
            
            # Replace in the stacked widget
            self.removeWidget(old_widget)
            self.insertWidget(index, new_widget)
            self.setCurrentWidget(new_widget)
    
    def update_authorization(self, authorized):
        """Update all admin sections when authorization state changes"""
        # Refresh all admin sections
        for section in ["settings", "users", "system", "logs"]:
            self.refresh_admin_section(section)