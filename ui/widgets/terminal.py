from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QLineEdit,
    QHBoxLayout, QLabel, QCompleter
)
from PyQt6.QtCore import Qt, pyqtSignal, QStringListModel
from PyQt6.QtGui import QTextCursor, QFont

class SecureTerminal(QWidget):
    """
    A secure terminal widget with limited command capabilities
    """
    # Signal emitted when a command is executed
    commandExecuted = pyqtSignal(str, str)  # command, result
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
        # Command history
        self.command_history = []
        self.history_index = 0
        
        # Available commands
        self.available_commands = [
            "help", "clear", "echo", "version", "info", "list",
            "exit", "logout", "shutdown", "restart"
        ]
        
        # Set up completer
        self.completer = QCompleter(self.available_commands)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.command_input.setCompleter(self.completer)
        
        # Command handlers
        self.command_handlers = {
            "help": self.cmd_help,
            "clear": self.cmd_clear,
            "echo": self.cmd_echo,
            "version": self.cmd_version,
            "info": self.cmd_info,
            "list": self.cmd_list,
            "exit": self.cmd_exit,
            "logout": self.cmd_logout,
            "shutdown": self.cmd_shutdown,
            "restart": self.cmd_restart
        }
        
        # Display welcome message
        self.display_welcome()
    
    def setup_ui(self):
        """Set up the terminal UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Output display
        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)
        self.output_display.setFont(QFont("Roboto Mono", 10))
        self.output_display.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #F0F0F0;
                border: none;
            }
        """)
        layout.addWidget(self.output_display)
        
        # Command input area
        input_layout = QHBoxLayout()
        
        self.prompt_label = QLabel("$")
        self.prompt_label.setFixedWidth(15)
        self.prompt_label.setFont(QFont("Roboto Mono", 10))
        self.prompt_label.setStyleSheet("color: #4CAF50;")
        
        self.command_input = QLineEdit()
        self.command_input.setFont(QFont("Roboto Mono", 10))
        self.command_input.setStyleSheet("""
            QLineEdit {
                background-color: #2A2A2A;
                color: #F0F0F0;
                border: none;
                padding: 5px;
            }
        """)
        self.command_input.returnPressed.connect(self.execute_command)
        
        input_layout.addWidget(self.prompt_label)
        input_layout.addWidget(self.command_input)
        
        layout.addLayout(input_layout)
    
    def display_welcome(self):
        """Display welcome message"""
        welcome_message = """
Secure GUI Platform Terminal
===========================
Type 'help' for a list of available commands.
"""
        self.output_display.setPlainText(welcome_message)
    
    def execute_command(self):
        """Execute the current command"""
        command = self.command_input.text().strip()
        if not command:
            return
        
        # Add to history
        self.command_history.append(command)
        self.history_index = len(self.command_history)
        
        # Display command in output
        self.output_display.append(f"$ {command}")
        
        # Parse command and args
        parts = command.split()
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Execute command
        if cmd in self.command_handlers:
            result = self.command_handlers[cmd](*args)
            if result:
                self.output_display.append(result)
            
            # Emit signal
            self.commandExecuted.emit(cmd, result if result else "")
        else:
            self.output_display.append(f"Command not found: {cmd}")
        
        # Clear input and add a blank line in output
        self.command_input.clear()
        self.output_display.append("")
        
        # Scroll to bottom
        cursor = self.output_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.output_display.setTextCursor(cursor)
    
    def cmd_help(self, *args):
        """Display help information"""
        help_text = """
Available commands:
------------------
help        - Display this help information
clear       - Clear the terminal screen
echo [text] - Display text
version     - Display system version
info        - Display system information
list        - List available resources
exit        - Exit terminal mode
logout      - Log out current user
shutdown    - Shut down the system (requires confirmation)
restart     - Restart the system (requires confirmation)
"""
        return help_text
    
    def cmd_clear(self, *args):
        """Clear the terminal output"""
        self.output_display.clear()
        return None
    
    def cmd_echo(self, *args):
        """Echo the provided text"""
        return " ".join(args)
    
    def cmd_version(self, *args):
        """Display version information"""
        return "Secure GUI Platform v0.1.0"
    
    def cmd_info(self, *args):
        """Display system information"""
        return """
System Information:
------------------
Platform: Secure GUI Platform
Version: 0.1.0
OS: FreeBSD / Linux
Python: 3.10+
Qt: 6.x
"""
    
    def cmd_list(self, *args):
        """List available resources"""
        return """
Available Resources:
------------------
Plugins: Use 'list plugins' for details
Users: Use 'list users' for details (requires admin)
Logs: Use 'list logs' for details (requires admin)
"""
    
    def cmd_exit(self, *args):
        """Exit terminal mode (placeholder)"""
        return "Terminal mode exited"
    
    def cmd_logout(self, *args):
        """Log out current user (placeholder)"""
        return "User logged out"
    
    def cmd_shutdown(self, *args):
        """Shut down the system (placeholder)"""
        return "Shutdown command requires confirmation and admin privileges"
    
    def cmd_restart(self, *args):
        """Restart the system (placeholder)"""
        return "Restart command requires confirmation and admin privileges"
    
    def keyPressEvent(self, event):
        """Handle key events for terminal"""
        # Up arrow for previous command
        if event.key() == Qt.Key.Key_Up and self.command_history:
            if self.history_index > 0:
                self.history_index -= 1
                self.command_input.setText(self.command_history[self.history_index])
        
        # Down arrow for next command
        elif event.key() == Qt.Key.Key_Down and self.command_history:
            if self.history_index < len(self.command_history) - 1:
                self.history_index += 1
                self.command_input.setText(self.command_history[self.history_index])
            else:
                self.history_index = len(self.command_history)
                self.command_input.clear()
        
        # Tab for auto-completion is handled by QCompleter
        
        # Pass other keys to parent
        else:
            super().keyPressEvent(event)