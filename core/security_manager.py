import os
import logging
import hashlib
import secrets
import datetime
from datetime import datetime
from typing import Optional, Callable, Dict, List

"""
Add the current_user attribute to the SecurityManager class
This fixes the AttributeError: 'SecurityManager' object has no attribute 'current_user'
"""

# Open core/security_manager.py and add these changes:

class SecurityManager:
    """
    Manages security aspects of the application
    """
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.authorized = False
        self.admin_mode = False
        self.current_user = "guest"  # Add this line to set a default user
        self._auth_callbacks: List[Callable[[bool], None]] = []
        
        # Security settings
        self.session_timeout = self.config_manager.get("security", "session_timeout", 1800)  # 30 minutes default
        
        # Add last_activity timestamp
        self.last_activity = datetime.now()
    
    def authenticate(self, password: str) -> bool:
        """Authenticate with admin password"""
        stored_hash = self.config_manager.get("security", "admin_password_hash", "")
        
        # If no password is set, this is first run
        if not stored_hash:
            result = self._set_initial_password(password)
            if result:
                self.current_user = "admin"  # Update current user on successful auth
                self.last_activity = datetime.now()  # Reset activity timer
            return result
        
        # Check password
        salt = stored_hash[:32]  # First 32 chars are the salt
        key = stored_hash[32:]   # Rest is the key
        new_key = self._hash_password(password, salt)
        
        if new_key == key:
            self.authorized = True
            self.current_user = "admin"  # Update current user on successful auth
            self.last_activity = datetime.now()  # Reset activity timer
            self._notify_auth_state()
            return True
        
        return False
    
    def logout(self) -> None:
        """Log out from admin mode"""
        self.authorized = False
        self.admin_mode = False
        self.current_user = "guest"  # Reset to guest on logout
        self._notify_auth_state()
    
    def check_session_timeout(self) -> bool:
        """Check if session has timed out"""
        if not self.authorized:
            return False
            
        # Check if session has timed out
        current_time = datetime.now()
        elapsed_seconds = (current_time - self.last_activity).total_seconds()
        
        if elapsed_seconds > self.session_timeout:
            return True
            
        return False
    
    def update_activity(self) -> None:
        """Update last activity timestamp"""
        self.last_activity = datetime.now()
    def register_auth_callback(self, callback: Callable[[bool], None]) -> None:
        """Register a callback to be called when auth state changes"""
        self._auth_callbacks.append(callback)
    
    # def authenticate(self, password: str) -> bool:
    #     """Authenticate with admin password"""
    #     stored_hash = self.config_manager.get("security", "admin_password_hash", "")
        
    #     # If no password is set, this is first run
    #     if not stored_hash:
    #         return self._set_initial_password(password)
        
    #     # Check password
    #     salt = stored_hash[:32]  # First 32 chars are the salt
    #     key = stored_hash[32:]   # Rest is the key
    #     new_key = self._hash_password(password, salt)
        
    #     if new_key == key:
    #         self.authorized = True
    #         self._notify_auth_state()
    #         return True
        
    #     return False
    
    def _set_initial_password(self, password: str) -> bool:
        """Set initial admin password"""
        salt = secrets.token_hex(16)
        key = self._hash_password(password, salt)
        password_hash = salt + key
        
        self.config_manager.set("security", "admin_password_hash", password_hash)
        self.authorized = True
        self._notify_auth_state()
        return True
    
    def _hash_password(self, password: str, salt: str) -> str:
        """Create secure hash of password"""
        return hashlib.pbkdf2_hmac(
            'sha256', 
            password.encode('utf-8'), 
            salt.encode('utf-8'), 
            100000  # Number of iterations
        ).hex()
    
    # def logout(self) -> None:
    #     """Log out from admin mode"""
    #     self.authorized = False
    #     self.admin_mode = False
    #     self._notify_auth_state()
    
    def enter_admin_mode(self) -> bool:
        """Enter admin mode if authenticated"""
        if self.authorized:
            self.admin_mode = True
            return True
        return False
    
    def exit_admin_mode(self) -> None:
        """Exit admin mode"""
        self.admin_mode = False
    
    def is_in_admin_mode(self) -> bool:
        """Check if in admin mode"""
        return self.admin_mode
    
    def _notify_auth_state(self) -> None:
        """Notify all registered callbacks of auth state change"""
        for callback in self._auth_callbacks:
            callback(self.authorized)
    
    def validate_plugin_integrity(self, plugin_path: str) -> bool:
        """Validate the integrity of a plugin"""
        # To be implemented with hash verification, signature checking, etc.
        return True