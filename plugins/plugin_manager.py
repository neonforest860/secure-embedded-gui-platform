import os
import sys
import importlib.util
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

from plugins.plugin_interface import PluginInterface

class PluginManager:
    """
    Manages plugin discovery, loading, and lifecycle
    """
    def __init__(self, config_manager, security_manager):
        self.config_manager = config_manager
        self.security_manager = security_manager
        self.plugins: Dict[str, PluginInterface] = {}
        self.plugin_dirs: List[Path] = []
        
        # Add default plugin directories
        self._add_plugin_directory(Path(__file__).parent / "built_in")
        
        # Add user plugin directory from config
        user_plugin_dir = self.config_manager.get("plugins", "user_plugin_dir", None)
        if user_plugin_dir:
            self._add_plugin_directory(Path(user_plugin_dir))
    
    def _add_plugin_directory(self, directory: Path) -> None:
        """Add a directory to search for plugins"""
        if directory.exists() and directory.is_dir():
            self.plugin_dirs.append(directory)
            logging.info(f"Added plugin directory: {directory}")
        else:
            logging.warning(f"Plugin directory does not exist: {directory}")
    
    def discover_plugins(self) -> List[str]:
        """
        Discover available plugins in all plugin directories
        Returns a list of plugin module paths
        """
        discovered_plugins: List[str] = []
        
        for plugin_dir in self.plugin_dirs:
            for item in plugin_dir.glob("*"):
                # Skip if not a directory or doesn't have __init__.py
                if not item.is_dir() or not (item / "__init__.py").exists():
                    continue
                
                # Check if it has a plugin.py file
                plugin_file = item / "plugin.py"
                if plugin_file.exists():
                    module_path = f"{item.parent.name}.{item.name}.plugin"
                    discovered_plugins.append(module_path)
                    logging.info(f"Discovered plugin: {module_path}")
        
        return discovered_plugins
    
    def load_plugin(self, module_path: str) -> Optional[PluginInterface]:
        """
        Load a plugin from its module path
        Returns the plugin instance or None if loading failed
        """
        try:
            # Import the module
            module = importlib.import_module(module_path)
            
            # Find the plugin class (a subclass of PluginInterface)
            plugin_class = None
            for name in dir(module):
                obj = getattr(module, name)
                if (isinstance(obj, type) and 
                    issubclass(obj, PluginInterface) and 
                    obj is not PluginInterface):
                    plugin_class = obj
                    break
            
            if not plugin_class:
                logging.error(f"No PluginInterface implementation found in {module_path}")
                return None
            
            # Create an instance
            plugin = plugin_class()
            
            # Initialize the plugin
            if not plugin.initialize():
                logging.error(f"Failed to initialize plugin: {module_path}")
                return None
            
            # Store the plugin
            plugin_name = plugin.get_name()
            self.plugins[plugin_name] = plugin
            logging.info(f"Loaded plugin: {plugin_name} ({plugin.get_version()})")
            
            return plugin
        
        except Exception as e:
            logging.error(f"Error loading plugin {module_path}: {e}")
            return None
    
    def load_enabled_plugins(self) -> Dict[str, PluginInterface]:
        """
        Load all enabled plugins
        Returns a dictionary of loaded plugins
        """
        enabled_plugins = self.config_manager.get("plugins", "enabled", [])
        
        # Discover all available plugins
        available_plugins = self.discover_plugins()
        
        # Load each enabled plugin
        for module_path in available_plugins:
            plugin_name = module_path.split(".")[-2]  # Extract name from path
            if plugin_name in enabled_plugins:
                self.load_plugin(module_path)
        
        return self.plugins
    
    def get_plugin(self, name: str) -> Optional[PluginInterface]:
        """Get a loaded plugin by name"""
        return self.plugins.get(name)
    
    def get_all_plugins(self) -> Dict[str, PluginInterface]:
        """Get all loaded plugins"""
        return self.plugins
    
    def enable_plugin(self, name: str) -> bool:
        """Enable a plugin"""
        enabled_plugins = self.config_manager.get("plugins", "enabled", [])
        if name not in enabled_plugins:
            enabled_plugins.append(name)
            self.config_manager.set("plugins", "enabled", enabled_plugins)
            return True
        return False
    
    def disable_plugin(self, name: str) -> bool:
        """Disable a plugin"""
        enabled_plugins = self.config_manager.get("plugins", "enabled", [])
        if name in enabled_plugins:
            enabled_plugins.remove(name)
            self.config_manager.set("plugins", "enabled", enabled_plugins)
            
            # Unload the plugin if it's loaded
            if name in self.plugins:
                self.unload_plugin(name)
            
            return True
        return False
    
    def unload_plugin(self, name: str) -> bool:
        """Unload a plugin"""
        if name in self.plugins:
            plugin = self.plugins[name]
            if plugin.shutdown():
                del self.plugins[name]
                logging.info(f"Unloaded plugin: {name}")
                return True
            else:
                logging.error(f"Failed to properly shutdown plugin: {name}")
                return False
        return False
    
    def unload_all_plugins(self) -> None:
        """Unload all plugins"""
        for name in list(self.plugins.keys()):
            self.unload_plugin(name)