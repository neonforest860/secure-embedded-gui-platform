from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QStackedWidget, QCheckBox,
    QLineEdit, QTextEdit, QGroupBox, QFormLayout, QMessageBox,
    QDialog, QDialogButtonBox, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QFont

class PluginListItem(QListWidgetItem):
    """List item for a plugin"""
    def __init__(self, name, version, description, enabled=False):
        super().__init__(name)
        self.name = name
        self.version = version
        self.description = description
        self.enabled = enabled
        
        # Set tooltip with description
        self.setToolTip(description)
        
        # Set checkbox state
        self.setCheckState(Qt.CheckState.Checked if enabled else Qt.CheckState.Unchecked)

class PluginDetailsWidget(QWidget):
    """Widget to display plugin details"""
    
    enableChanged = pyqtSignal(str, bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.current_plugin = ""
    
    def setup_ui(self):
        """Set up the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        self.name_label = QLabel("Plugin Name")
        self.name_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.name_label)
        
        # Version
        version_layout = QHBoxLayout()
        version_layout.addWidget(QLabel("Version:"))
        self.version_label = QLabel("1.0.0")
        version_layout.addWidget(self.version_label)
        version_layout.addStretch(1)
        layout.addLayout(version_layout)
        
        # Description
        description_group = QGroupBox("Description")
        description_layout = QVBoxLayout(description_group)
        self.description_label = QLabel("Plugin description goes here.")
        self.description_label.setWordWrap(True)
        description_layout.addWidget(self.description_label)
        layout.addWidget(description_group)
        
        # Enable/Disable
        self.enable_checkbox = QCheckBox("Enabled")
        self.enable_checkbox.toggled.connect(self.on_enable_toggled)
        layout.addWidget(self.enable_checkbox)
        
        # Settings (placeholder)
        settings_group = QGroupBox("Settings")
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.addWidget(QLabel("No settings available for this plugin."))
        layout.addWidget(settings_group)
        
        # Spacer
        layout.addStretch(1)
    
    def set_plugin(self, name, version, description, enabled):
        """Set the plugin details"""
        self.current_plugin = name
        self.name_label.setText(name)
        self.version_label.setText(version)
        self.description_label.setText(description)
        
        # Block signals to prevent triggering the toggled event
        self.enable_checkbox.blockSignals(True)
        self.enable_checkbox.setChecked(enabled)
        self.enable_checkbox.blockSignals(False)
    
    def on_enable_toggled(self, checked):
        """Handle enable/disable toggle"""
        self.enableChanged.emit(self.current_plugin, checked)

class PluginManagerWidget(QWidget):
    """Widget for managing plugins"""
    def __init__(self, plugin_manager, parent=None):
        super().__init__(parent)
        self.plugin_manager = plugin_manager
        self.setup_ui()
        self.load_plugins()
    
    def setup_ui(self):
        """Set up the UI"""
        layout = QHBoxLayout(self)
        
        # Left panel - Plugin list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search plugins...")
        self.search_input.textChanged.connect(self.filter_plugins)
        left_layout.addWidget(self.search_input)
        
        self.plugin_list = QListWidget()
        self.plugin_list.itemClicked.connect(self.on_plugin_selected)
        left_layout.addWidget(self.plugin_list)
        
        button_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_plugins)
        button_layout.addWidget(self.refresh_button)
        
        self.import_button = QPushButton("Import")
        self.import_button.clicked.connect(self.import_plugin)
        button_layout.addWidget(self.import_button)
        
        left_layout.addLayout(button_layout)
        
        # Right panel - Plugin details
        self.details_widget = PluginDetailsWidget()
        self.details_widget.enableChanged.connect(self.on_plugin_enable_changed)
        
        # Add panels to main layout
        layout.addWidget(left_panel, 1)  # 1 = stretch factor
        layout.addWidget(self.details_widget, 2)  # 2 = stretch factor
    
    def load_plugins(self):
        """Load and display available plugins"""
        self.plugin_list.clear()
        
        # Get enabled plugins
        enabled_plugins = self.plugin_manager.config_manager.get("plugins", "enabled", [])
        
        # Discover available plugins
        available_plugins = self.plugin_manager.discover_plugins()
        
        # Create items for each plugin
        for module_path in available_plugins:
            # Extract plugin name from path
            plugin_name = module_path.split(".")[-2]
            
            # For a real implementation, we'd need to load plugin metadata without fully loading the plugin
            # For now, we'll create items with placeholder info
            version = "1.0.0"
            description = f"Description for {plugin_name} plugin"
            enabled = plugin_name in enabled_plugins
            
            item = PluginListItem(plugin_name, version, description, enabled)
            self.plugin_list.addItem(item)
        
        # Load already loaded plugins
        for name, plugin in self.plugin_manager.get_all_plugins().items():
            # Skip if already added
            if self.find_item_by_name(name):
                continue
                
            version = plugin.get_version()
            description = plugin.get_description()
            enabled = True  # If it's loaded, it's enabled
            
            item = PluginListItem(name, version, description, enabled)
            self.plugin_list.addItem(item)
    
    def find_item_by_name(self, name):
        """Find a list item by plugin name"""
        for i in range(self.plugin_list.count()):
            item = self.plugin_list.item(i)
            if item.name == name:
                return item
        return None
    
    def filter_plugins(self, text):
        """Filter plugins by name"""
        text = text.lower()
        for i in range(self.plugin_list.count()):
            item = self.plugin_list.item(i)
            if text in item.name.lower() or text in item.description.lower():
                item.setHidden(False)
            else:
                item.setHidden(True)
    
    def on_plugin_selected(self, item):
        """Handle plugin selection"""
        self.details_widget.set_plugin(
            item.name,
            item.version,
            item.description,
            item.enabled
        )
    
    def on_plugin_enable_changed(self, name, enabled):
        """Handle plugin enable/disable"""
        if enabled:
            success = self.plugin_manager.enable_plugin(name)
            # After enabling, try to load the plugin
            if success:
                # Find plugin module path
                module_path = None
                for path in self.plugin_manager.discover_plugins():
                    if path.split(".")[-2] == name:
                        module_path = path
                        break
                
                if module_path:
                    self.plugin_manager.load_plugin(module_path)
        else:
            success = self.plugin_manager.disable_plugin(name)
        
        # Update list item
        item = self.find_item_by_name(name)
        if item:
            item.enabled = enabled
            item.setCheckState(
                Qt.CheckState.Checked if enabled else Qt.CheckState.Unchecked
            )
        
        # Show result
        if not success:
            QMessageBox.warning(
                self,
                "Plugin Operation Failed",
                f"Failed to {'enable' if enabled else 'disable'} plugin: {name}"
            )
    
    def import_plugin(self):
        """Import a plugin from a file or directory"""
        # Show file dialog to select a plugin directory or zip file
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        dialog.setWindowTitle("Select Plugin Directory")
        
        if dialog.exec():
            selected_dirs = dialog.selectedFiles()
            if selected_dirs:
                plugin_dir = selected_dirs[0]
                
                # In a real implementation, we would copy the plugin to the plugins directory
                # and register it with the plugin manager
                QMessageBox.information(
                    self,
                    "Plugin Import",
                    f"Plugin import from {plugin_dir} would be implemented here."
                )
                
                # Refresh the plugin list
                self.load_plugins()