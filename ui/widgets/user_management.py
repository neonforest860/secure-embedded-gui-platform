from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QDialog, QFormLayout, QLineEdit, QComboBox, QMessageBox,
    QCheckBox, QDialogButtonBox, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon

class UserDialog(QDialog):
    """Dialog for adding or editing a user"""
    def __init__(self, parent=None, edit_mode=False, user_data=None):
        super().__init__(parent)
        self.edit_mode = edit_mode
        self.user_data = user_data or {}
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the dialog UI"""
        self.setWindowTitle("Add User" if not self.edit_mode else "Edit User")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Basic information
        basic_group = QGroupBox("User Information")
        form_layout = QFormLayout(basic_group)
        
        self.username = QLineEdit()
        if self.edit_mode:
            self.username.setText(self.user_data.get("username", ""))
            self.username.setReadOnly(True)  # Can't change username in edit mode
        form_layout.addRow("Username:", self.username)
        
        self.full_name = QLineEdit()
        self.full_name.setText(self.user_data.get("full_name", ""))
        form_layout.addRow("Full Name:", self.full_name)
        
        self.email = QLineEdit()
        self.email.setText(self.user_data.get("email", ""))
        form_layout.addRow("Email:", self.email)
        
        self.role = QComboBox()
        self.role.addItems(["User", "Administrator"])
        if self.edit_mode and self.user_data.get("role"):
            self.role.setCurrentText(self.user_data.get("role"))
        form_layout.addRow("Role:", self.role)
        
        layout.addWidget(basic_group)
        
        # Password section
        pass_group = QGroupBox("Password" if not self.edit_mode else "Change Password")
        pass_layout = QFormLayout(pass_group)
        
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        pass_layout.addRow("Password:", self.password)
        
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        pass_layout.addRow("Confirm Password:", self.confirm_password)
        
        if self.edit_mode:
            # In edit mode, password is optional
            self.password.setPlaceholderText("Leave blank to keep unchanged")
            self.confirm_password.setPlaceholderText("Leave blank to keep unchanged")
        
        layout.addWidget(pass_group)
        
        # Permissions section
        perm_group = QGroupBox("Permissions")
        perm_layout = QVBoxLayout(perm_group)
        
        self.can_use_terminal = QCheckBox("Can use terminal")
        self.can_use_terminal.setChecked(self.user_data.get("can_use_terminal", False))
        perm_layout.addWidget(self.can_use_terminal)
        
        self.can_manage_plugins = QCheckBox("Can manage plugins")
        self.can_manage_plugins.setChecked(self.user_data.get("can_manage_plugins", False))
        perm_layout.addWidget(self.can_manage_plugins)
        
        self.can_access_files = QCheckBox("Can access file system")
        self.can_access_files.setChecked(self.user_data.get("can_access_files", False))
        perm_layout.addWidget(self.can_access_files)
        
        self.can_access_network = QCheckBox("Can access network")
        self.can_access_network.setChecked(self.user_data.get("can_access_network", False))
        perm_layout.addWidget(self.can_access_network)
        
        layout.addWidget(perm_group)
        
        # Account status
        status_group = QGroupBox("Account Status")
        status_layout = QVBoxLayout(status_group)
        
        self.is_active = QCheckBox("Account is active")
        self.is_active.setChecked(self.user_data.get("is_active", True))
        status_layout.addWidget(self.is_active)
        
        self.require_password_change = QCheckBox("Require password change at next login")
        self.require_password_change.setChecked(self.user_data.get("require_password_change", True))
        status_layout.addWidget(self.require_password_change)
        
        layout.addWidget(status_group)
        
        # Buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.validate)
        self.button_box.rejected.connect(self.reject)
        
        layout.addWidget(self.button_box)
    
    def validate(self):
        """Validate the input before accepting"""
        # Check for required fields
        if not self.username.text():
            QMessageBox.warning(self, "Validation Error", "Username is required")
            return
        
        if not self.edit_mode and not self.password.text():
            QMessageBox.warning(self, "Validation Error", "Password is required for new users")
            return
        
        # Check password match if provided
        if self.password.text() or self.confirm_password.text():
            if self.password.text() != self.confirm_password.text():
                QMessageBox.warning(self, "Validation Error", "Passwords do not match")
                return
        
        # All validations passed, accept the dialog
        self.accept()
    
    def get_user_data(self):
        """Get the user data from the dialog"""
        user_data = {
            "username": self.username.text(),
            "full_name": self.full_name.text(),
            "email": self.email.text(),
            "role": self.role.currentText(),
            "can_use_terminal": self.can_use_terminal.isChecked(),
            "can_manage_plugins": self.can_manage_plugins.isChecked(),
            "can_access_files": self.can_access_files.isChecked(),
            "can_access_network": self.can_access_network.isChecked(),
            "is_active": self.is_active.isChecked(),
            "require_password_change": self.require_password_change.isChecked()
        }
        
        # Add password only if provided
        if self.password.text():
            user_data["password"] = self.password.text()
        
        return user_data

class UserManagementPanel(QWidget):
    """
    Panel for managing users and their permissions
    """
    userChanged = pyqtSignal(dict)  # Signal emitted when a user is added, edited, or deleted
    
    def __init__(self, security_manager, parent=None):
        super().__init__(parent)
        self.security_manager = security_manager
        self.users = []  # Will be populated from security manager
        self.setup_ui()
        self.load_users()
    
    def setup_ui(self):
        """Set up the user management UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("User Management")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title)
        
        self.add_user_button = QPushButton("Add User")
        self.add_user_button.clicked.connect(self.add_user)
        header_layout.addWidget(self.add_user_button)
        
        layout.addLayout(header_layout)
        
        # User table
        self.user_table = QTableWidget(0, 6)  # Start with 0 rows, 6 columns
        self.user_table.setHorizontalHeaderLabels([
            "Username", "Full Name", "Role", "Status", "Last Login", "Actions"
        ])
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.user_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.user_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.user_table)
        
        # Filter and search (can be expanded later)
        filter_layout = QHBoxLayout()
        
        self.show_inactive = QCheckBox("Show Inactive Users")
        self.show_inactive.setChecked(False)
        self.show_inactive.stateChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.show_inactive)
        
        self.filter_role = QComboBox()
        self.filter_role.addItems(["All Roles", "User", "Administrator"])
        self.filter_role.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(QLabel("Role:"))
        filter_layout.addWidget(self.filter_role)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search users...")
        self.search_input.textChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.search_input)
        
        layout.addLayout(filter_layout)
    
    def load_users(self):
        """Load users from the security manager"""
        # In a real implementation, this would load from the security manager
        # For now, we'll add some dummy users
        self.users = [
            {
                "username": "admin",
                "full_name": "Administrator",
                "email": "admin@example.com",
                "role": "Administrator",
                "is_active": True,
                "can_use_terminal": True,
                "can_manage_plugins": True,
                "can_access_files": True,
                "can_access_network": True,
                "last_login": "2025-05-08 09:15",
                "require_password_change": False
            },
            {
                "username": "user1",
                "full_name": "Regular User",
                "email": "user@example.com",
                "role": "User",
                "is_active": True,
                "can_use_terminal": True,
                "can_manage_plugins": False,
                "can_access_files": False,
                "can_access_network": False,
                "last_login": "2025-05-07 14:30",
                "require_password_change": False
            },
            {
                "username": "guest",
                "full_name": "Guest Account",
                "email": "guest@example.com",
                "role": "User",
                "is_active": False,
                "can_use_terminal": False,
                "can_manage_plugins": False,
                "can_access_files": False,
                "can_access_network": False,
                "last_login": "Never",
                "require_password_change": True
            }
        ]
        
        self.update_user_table()
    
    def update_user_table(self):
        """Update the user table with current users"""
        self.user_table.setRowCount(0)  # Clear existing rows
        
        for user in self.users:
            # Skip inactive users if filter is set
            if not self.show_inactive.isChecked() and not user["is_active"]:
                continue
            
            # Skip users that don't match role filter
            if self.filter_role.currentText() != "All Roles" and user["role"] != self.filter_role.currentText():
                continue
            
            # Skip users that don't match search text
            search_text = self.search_input.text().lower()
            if search_text and not (
                search_text in user["username"].lower() or
                search_text in user["full_name"].lower() or
                search_text in user["email"].lower()
            ):
                continue
            
            # Add the user to the table
            row = self.user_table.rowCount()
            self.user_table.insertRow(row)
            
            # Username
            self.user_table.setItem(row, 0, QTableWidgetItem(user["username"]))
            
            # Full Name
            self.user_table.setItem(row, 1, QTableWidgetItem(user["full_name"]))
            
            # Role
            self.user_table.setItem(row, 2, QTableWidgetItem(user["role"]))
            
            # Status
            status = "Active" if user["is_active"] else "Inactive"
            status_item = QTableWidgetItem(status)
            status_item.setForeground(Qt.GlobalColor.darkGreen if user["is_active"] else Qt.GlobalColor.darkRed)
            self.user_table.setItem(row, 3, status_item)
            
            # Last Login
            self.user_table.setItem(row, 4, QTableWidgetItem(user["last_login"]))
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            
            edit_button = QPushButton("Edit")
            edit_button.setProperty("username", user["username"])
            edit_button.clicked.connect(lambda checked, u=user["username"]: self.edit_user(u))
            
            delete_button = QPushButton("Delete")
            delete_button.setProperty("username", user["username"])
            delete_button.clicked.connect(lambda checked, u=user["username"]: self.delete_user(u))
            
            actions_layout.addWidget(edit_button)
            actions_layout.addWidget(delete_button)
            
            self.user_table.setCellWidget(row, 5, actions_widget)
    
    def apply_filters(self):
        """Apply filters to the user table"""
        self.update_user_table()
    
    def add_user(self):
        """Add a new user"""
        dialog = UserDialog(self)
        if dialog.exec():
            user_data = dialog.get_user_data()
            
            # Check if username already exists
            if any(u["username"] == user_data["username"] for u in self.users):
                QMessageBox.warning(self, "Error", f"Username '{user_data['username']}' already exists")
                return
            
            # Add to users list
            self.users.append(user_data)
            
            # Update UI
            self.update_user_table()
            
            # Emit signal
            self.userChanged.emit(user_data)
            
            QMessageBox.information(self, "Success", f"User '{user_data['username']}' added successfully")
    
    def edit_user(self, username):
        """Edit an existing user"""
        # Find the user
        user = next((u for u in self.users if u["username"] == username), None)
        if not user:
            QMessageBox.warning(self, "Error", f"User '{username}' not found")
            return
        
        dialog = UserDialog(self, edit_mode=True, user_data=user)
        if dialog.exec():
            updated_data = dialog.get_user_data()
            
            # Update user data
            for i, u in enumerate(self.users):
                if u["username"] == username:
                    self.users[i].update(updated_data)
                    break
            
            # Update UI
            self.update_user_table()
            
            # Emit signal
            self.userChanged.emit(updated_data)
            
            QMessageBox.information(self, "Success", f"User '{username}' updated successfully")
    
    def delete_user(self, username):
        """Delete a user"""
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete user '{username}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Find and remove the user
        for i, user in enumerate(self.users):
            if user["username"] == username:
                deleted_user = self.users.pop(i)
                
                # Update UI
                self.update_user_table()
                
                # Emit signal
                self.userChanged.emit({"username": username, "action": "delete"})
                
                QMessageBox.information(self, "Success", f"User '{username}' deleted successfully")
                return
        
        QMessageBox.warning(self, "Error", f"User '{username}' not found")