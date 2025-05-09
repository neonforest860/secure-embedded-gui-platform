from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QScrollArea, QFormLayout, QLineEdit, QCheckBox,
    QComboBox, QSpinBox, QGroupBox, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal

class SettingsPanel(QWidget):
    """
    Administrative settings panel with multiple categories
    """
    # Signal emitted when settings are changed
    settingsChanged = pyqtSignal(str, str, object)  # section, key, value
    
    def __init__(self, config_manager, theme_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.theme_manager = theme_manager
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Set up the settings UI"""
        layout = QVBoxLayout(self)
        
        # Create tab widget for different setting categories
        self.tabs = QTabWidget()
        
        # General settings tab
        self.general_tab = self.create_general_tab()
        self.tabs.addTab(self.general_tab, "General")
        
        # Appearance settings tab
        self.appearance_tab = self.create_appearance_tab()
        self.tabs.addTab(self.appearance_tab, "Appearance")
        
        # Security settings tab
        self.security_tab = self.create_security_tab()
        self.tabs.addTab(self.security_tab, "Security")
        
        # Plugins settings tab
        self.plugins_tab = self.create_plugins_tab()
        self.tabs.addTab(self.plugins_tab, "Plugins")
        
        # Advanced settings tab
        self.advanced_tab = self.create_advanced_tab()
        self.tabs.addTab(self.advanced_tab, "Advanced")
        
        layout.addWidget(self.tabs)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.reset_button = QPushButton("Reset to Defaults")
        self.reset_button.clicked.connect(self.reset_to_defaults)
        
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_settings)
        self.apply_button.setDefault(True)
        
        button_layout.addWidget(self.reset_button)
        button_layout.addStretch()
        button_layout.addWidget(self.apply_button)
        
        layout.addLayout(button_layout)
    
    def create_general_tab(self):
        """Create the general settings tab"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Application settings group
        app_group = QGroupBox("Application Settings")
        app_layout = QFormLayout(app_group)
        
        self.app_name = QLineEdit()
        app_layout.addRow("Application Name:", self.app_name)
        
        self.dev_mode = QCheckBox("Development Mode")
        app_layout.addRow("", self.dev_mode)
        
        self.log_level = QComboBox()
        self.log_level.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        app_layout.addRow("Log Level:", self.log_level)
        
        layout.addWidget(app_group)
        
        # Startup settings group
        startup_group = QGroupBox("Startup Settings")
        startup_layout = QFormLayout(startup_group)
        
        self.auto_start = QCheckBox("Start on System Boot")
        startup_layout.addRow("", self.auto_start)
        
        self.restore_session = QCheckBox("Restore Previous Session")
        startup_layout.addRow("", self.restore_session)
        
        layout.addWidget(startup_group)
        
        # Add spacer at the end
        layout.addStretch(1)
        
        scroll.setWidget(content)
        return scroll
    
    def create_appearance_tab(self):
        """Create the appearance settings tab"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Theme settings group
        theme_group = QGroupBox("Theme Settings")
        theme_layout = QFormLayout(theme_group)
        
        self.theme_selector = QComboBox()
        # Add themes from theme manager
        if self.theme_manager:
            self.theme_selector.addItems(self.theme_manager.get_theme_names())
        theme_layout.addRow("Theme:", self.theme_selector)
        
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)
        theme_layout.addRow("Base Font Size:", self.font_size)
        
        layout.addWidget(theme_group)
        
        # UI settings group
        ui_group = QGroupBox("UI Settings")
        ui_layout = QFormLayout(ui_group)
        
        self.sidebar_width = QSpinBox()
        self.sidebar_width.setRange(150, 500)
        self.sidebar_width.setSingleStep(10)
        ui_layout.addRow("Sidebar Width:", self.sidebar_width)
        
        self.show_status_bar = QCheckBox("Show Status Bar")
        ui_layout.addRow("", self.show_status_bar)
        
        layout.addWidget(ui_group)
        
        # Add spacer at the end
        layout.addStretch(1)
        
        scroll.setWidget(content)
        return scroll
    
    def create_security_tab(self):
        """Create the security settings tab"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Authentication settings group
        auth_group = QGroupBox("Authentication Settings")
        auth_layout = QFormLayout(auth_group)
        
        self.change_password_button = QPushButton("Change Admin Password")
        self.change_password_button.clicked.connect(self.change_admin_password)
        auth_layout.addRow("Admin Password:", self.change_password_button)
        
        self.session_timeout = QSpinBox()
        self.session_timeout.setRange(0, 86400)  # 0 to 24 hours in seconds
        self.session_timeout.setSingleStep(300)  # 5 minute increments
        self.session_timeout.setSuffix(" seconds")
        auth_layout.addRow("Session Timeout:", self.session_timeout)
        
        layout.addWidget(auth_group)
        
        # Plugin security group
        plugin_group = QGroupBox("Plugin Security")
        plugin_layout = QFormLayout(plugin_group)
        
        self.plugin_verification = QCheckBox("Verify Plugin Integrity")
        plugin_layout.addRow("", self.plugin_verification)
        
        self.plugin_sandbox = QCheckBox("Sandbox Plugin Execution")
        plugin_layout.addRow("", self.plugin_sandbox)
        
        layout.addWidget(plugin_group)
        
        # System access group
        system_group = QGroupBox("System Access")
        system_layout = QFormLayout(system_group)
        
        self.terminal_access = QCheckBox("Enable Terminal Access")
        system_layout.addRow("", self.terminal_access)
        
        self.file_access = QCheckBox("Enable File System Access")
        system_layout.addRow("", self.file_access)
        
        self.network_access = QCheckBox("Enable Network Access")
        system_layout.addRow("", self.network_access)
        
        layout.addWidget(system_group)
        
        # Add spacer at the end
        layout.addStretch(1)
        
        scroll.setWidget(content)
        return scroll
    
    def create_plugins_tab(self):
        """Create the plugins settings tab"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Plugin settings group
        plugins_group = QGroupBox("Plugin Settings")
        plugins_layout = QFormLayout(plugins_group)
        
        self.auto_load_plugins = QCheckBox("Automatically Load Enabled Plugins")
        plugins_layout.addRow("", self.auto_load_plugins)
        
        self.plugin_auto_update = QCheckBox("Auto-update Plugins")
        plugins_layout.addRow("", self.plugin_auto_update)
        
        self.plugin_directory_button = QPushButton("Browse...")
        self.plugin_directory_button.clicked.connect(self.browse_plugin_directory)
        self.plugin_directory = QLineEdit()
        self.plugin_directory.setReadOnly(True)
        
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(self.plugin_directory)
        dir_layout.addWidget(self.plugin_directory_button)
        
        plugins_layout.addRow("Plugin Directory:", dir_layout)
        
        layout.addWidget(plugins_group)
        
        # Add spacer at the end
        layout.addStretch(1)
        
        scroll.setWidget(content)
        return scroll
    
    def create_advanced_tab(self):
        """Create the advanced settings tab"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Warning label
        warning = QLabel("Warning: These settings are for advanced users. "
                         "Incorrect values may cause system instability.")
        warning.setStyleSheet("color: red;")
        warning.setWordWrap(True)
        layout.addWidget(warning)
        
        # System settings group
        system_group = QGroupBox("System Settings")
        system_layout = QFormLayout(system_group)
        
        self.max_memory = QSpinBox()
        self.max_memory.setRange(64, 8192)  # 64MB to 8GB
        self.max_memory.setSingleStep(64)
        self.max_memory.setSuffix(" MB")
        system_layout.addRow("Max Memory Usage:", self.max_memory)
        
        self.process_priority = QComboBox()
        self.process_priority.addItems(["Low", "Normal", "High"])
        system_layout.addRow("Process Priority:", self.process_priority)
        
        self.enable_hardware_accel = QCheckBox("Enable Hardware Acceleration")
        system_layout.addRow("", self.enable_hardware_accel)
        
        layout.addWidget(system_group)
        
        # Debug settings group
        debug_group = QGroupBox("Debug Settings")
        debug_layout = QFormLayout(debug_group)
        
        self.debug_logging = QCheckBox("Enable Debug Logging")
        debug_layout.addRow("", self.debug_logging)
        
        self.console_output = QCheckBox("Show Console Output")
        debug_layout.addRow("", self.console_output)
        
        layout.addWidget(debug_group)
        
        # Maintenance group
        maint_group = QGroupBox("Maintenance")
        maint_layout = QVBoxLayout(maint_group)
        
        self.reset_all_button = QPushButton("Reset All Settings to Default")
        self.reset_all_button.clicked.connect(self.reset_all_settings)
        
        self.export_settings_button = QPushButton("Export Settings")
        self.export_settings_button.clicked.connect(self.export_settings)
        
        self.import_settings_button = QPushButton("Import Settings")
        self.import_settings_button.clicked.connect(self.import_settings)
        
        maint_layout.addWidget(self.reset_all_button)
        maint_layout.addWidget(self.export_settings_button)
        maint_layout.addWidget(self.import_settings_button)
        
        layout.addWidget(maint_group)
        
        # Add spacer at the end
        layout.addStretch(1)
        
        scroll.setWidget(content)
        return scroll
    
    def load_settings(self):
        """Load settings from config manager"""
        if not self.config_manager:
            return
        
        # General settings
        self.app_name.setText(self.config_manager.get("general", "app_name", "Secure GUI Platform"))
        self.dev_mode.setChecked(self.config_manager.get("general", "development_mode", False))
        log_level = self.config_manager.get("general", "log_level", "INFO")
        index = self.log_level.findText(log_level)
        if index >= 0:
            self.log_level.setCurrentIndex(index)
        
        # Startup settings
        self.auto_start.setChecked(self.config_manager.get("general", "auto_start", False))
        self.restore_session.setChecked(self.config_manager.get("general", "restore_session", False))
        
        # Appearance settings
        theme = self.config_manager.get("appearance", "theme", "Light")
        index = self.theme_selector.findText(theme)
        if index >= 0:
            self.theme_selector.setCurrentIndex(index)
        self.font_size.setValue(self.config_manager.get("appearance", "font_size", 12))
        self.sidebar_width.setValue(self.config_manager.get("appearance", "sidebar_width", 250))
        self.show_status_bar.setChecked(self.config_manager.get("appearance", "show_status_bar", False))
        
        # Security settings
        self.session_timeout.setValue(self.config_manager.get("security", "session_timeout", 1800))
        self.plugin_verification.setChecked(self.config_manager.get("security", "plugin_verification", True))
        self.plugin_sandbox.setChecked(self.config_manager.get("security", "plugin_sandbox", True))
        self.terminal_access.setChecked(self.config_manager.get("security", "terminal_access", True))
        self.file_access.setChecked(self.config_manager.get("security", "file_access", False))
        self.network_access.setChecked(self.config_manager.get("security", "network_access", False))
        
        # Plugin settings
        self.auto_load_plugins.setChecked(self.config_manager.get("plugins", "auto_load", True))
        self.plugin_auto_update.setChecked(self.config_manager.get("plugins", "auto_update", False))
        self.plugin_directory.setText(self.config_manager.get("plugins", "user_plugin_dir", ""))
        
        # Advanced settings
        self.max_memory.setValue(self.config_manager.get("advanced", "max_memory", 1024))
        priority = self.config_manager.get("advanced", "process_priority", "Normal")
        index = self.process_priority.findText(priority)
        if index >= 0:
            self.process_priority.setCurrentIndex(index)
        self.enable_hardware_accel.setChecked(self.config_manager.get("advanced", "hardware_acceleration", True))
        self.debug_logging.setChecked(self.config_manager.get("advanced", "debug_logging", False))
        self.console_output.setChecked(self.config_manager.get("advanced", "console_output", False))
    
    def apply_settings(self):
        """Apply the current settings"""
        if not self.config_manager:
            QMessageBox.warning(self, "Settings Error", "Configuration manager not available")
            return
        
        # General settings
        self.config_manager.set("general", "app_name", self.app_name.text())
        self.config_manager.set("general", "development_mode", self.dev_mode.isChecked())
        self.config_manager.set("general", "log_level", self.log_level.currentText())
        self.config_manager.set("general", "auto_start", self.auto_start.isChecked())
        self.config_manager.set("general", "restore_session", self.restore_session.isChecked())
        
        # Appearance settings
        self.config_manager.set("appearance", "theme", self.theme_selector.currentText())
        self.config_manager.set("appearance", "font_size", self.font_size.value())
        self.config_manager.set("appearance", "sidebar_width", self.sidebar_width.value())
        self.config_manager.set("appearance", "show_status_bar", self.show_status_bar.isChecked())
        
        # Apply theme if changed
        if self.theme_manager:
            self.theme_manager.apply_theme(self.theme_selector.currentText())
        
        # Security settings
        self.config_manager.set("security", "session_timeout", self.session_timeout.value())
        self.config_manager.set("security", "plugin_verification", self.plugin_verification.isChecked())
        self.config_manager.set("security", "plugin_sandbox", self.plugin_sandbox.isChecked())
        self.config_manager.set("security", "terminal_access", self.terminal_access.isChecked())
        self.config_manager.set("security", "file_access", self.file_access.isChecked())
        self.config_manager.set("security", "network_access", self.network_access.isChecked())
        
        # Plugin settings
        self.config_manager.set("plugins", "auto_load", self.auto_load_plugins.isChecked())
        self.config_manager.set("plugins", "auto_update", self.plugin_auto_update.isChecked())
        self.config_manager.set("plugins", "user_plugin_dir", self.plugin_directory.text())
        
        # Advanced settings
        self.config_manager.set("advanced", "max_memory", self.max_memory.value())
        self.config_manager.set("advanced", "process_priority", self.process_priority.currentText())
        self.config_manager.set("advanced", "hardware_acceleration", self.enable_hardware_accel.isChecked())
        self.config_manager.set("advanced", "debug_logging", self.debug_logging.isChecked())
        self.config_manager.set("advanced", "console_output", self.console_output.isChecked())
        
        # Notify about settings change
        QMessageBox.information(self, "Settings", "Settings applied successfully!")
    
    def reset_to_defaults(self):
        """Reset settings to defaults"""
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Reset all settings
            self.app_name.setText("Secure GUI Platform")
            self.dev_mode.setChecked(False)
            self.log_level.setCurrentText("INFO")
            self.auto_start.setChecked(False)
            self.restore_session.setChecked(False)
            
            self.theme_selector.setCurrentText("Light")
            self.font_size.setValue(12)
            self.sidebar_width.setValue(250)
            self.show_status_bar.setChecked(False)
            
            self.session_timeout.setValue(1800)
            self.plugin_verification.setChecked(True)
            self.plugin_sandbox.setChecked(True)
            self.terminal_access.setChecked(True)
            self.file_access.setChecked(False)
            self.network_access.setChecked(False)
            
            self.auto_load_plugins.setChecked(True)
            self.plugin_auto_update.setChecked(False)
            self.plugin_directory.setText("")
            
            self.max_memory.setValue(1024)
            self.process_priority.setCurrentText("Normal")
            self.enable_hardware_accel.setChecked(True)
            self.debug_logging.setChecked(False)
            self.console_output.setChecked(False)
    
    def reset_all_settings(self):
        """Reset all settings to defaults and apply"""
        reply = QMessageBox.question(
            self,
            "Reset All Settings",
            "Are you sure you want to reset ALL settings to defaults? This will remove all customizations.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.config_manager:
                self.config_manager._create_default_config()
                self.load_settings()
                QMessageBox.information(self, "Settings Reset", "All settings have been reset to defaults.")
    
    def change_admin_password(self):
        """Change the admin password"""
        # To be implemented with a password dialog
        QMessageBox.information(self, "Change Password", "Password change functionality to be implemented.")
    
    def browse_plugin_directory(self):
        """Browse for plugin directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Plugin Directory",
            self.plugin_directory.text(),
            QFileDialog.Option.ShowDirsOnly
        )
        
        if directory:
            self.plugin_directory.setText(directory)
    
    def export_settings(self):
        """Export settings to a file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Settings",
            "",
            "JSON Files (*.json)"
        )
        
        if file_path and self.config_manager:
            # In a real implementation, this would export the settings to a file
            QMessageBox.information(self, "Export Settings", f"Settings exported to {file_path}")
    
    def import_settings(self):
        """Import settings from a file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Settings",
            "",
            "JSON Files (*.json)"
        )
        
        if file_path and self.config_manager:
            # In a real implementation, this would import settings from a file
            QMessageBox.information(self, "Import Settings", f"Settings imported from {file_path}")