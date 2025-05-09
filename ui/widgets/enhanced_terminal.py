from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QLineEdit,
    QHBoxLayout, QLabel, QCompleter, QSplitter,
    QTreeWidget, QTreeWidgetItem, QMenu, QPushButton,
    QDialog, QDialogButtonBox, QFormLayout, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QStringListModel, QTimer
from PyQt6.QtGui import QTextCursor, QFont, QColor, QTextCharFormat, QAction

from utils.secure_shell import SecureShell

class CommandHistoryDialog(QDialog):
    """Dialog for browsing and selecting from command history"""
    
    commandSelected = pyqtSignal(str)
    
    def __init__(self, command_history, parent=None):
        super().__init__(parent)
        self.command_history = command_history
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the dialog UI"""
        self.setWindowTitle("Command History")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        layout = QVBoxLayout(self)
        
        # Command history tree
        self.history_tree = QTreeWidget()
        self.history_tree.setHeaderLabels(["#", "Command"])
        self.history_tree.setColumnWidth(0, 50)
        self.history_tree.setAlternatingRowColors(True)
        self.history_tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        # Populate tree
        for i, cmd in enumerate(self.command_history, 1):
            item = QTreeWidgetItem([str(i), cmd])
            self.history_tree.addTopLevelItem(item)
        
        layout.addWidget(self.history_tree)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.on_accepted)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
    
    def on_item_double_clicked(self, item, column):
        """Handle item double click"""
        self.emit_selected_command()
        self.accept()
    
    def on_accepted(self):
        """Handle OK button"""
        self.emit_selected_command()
        self.accept()
    
    def emit_selected_command(self):
        """Emit the selected command"""
        selected_items = self.history_tree.selectedItems()
        if selected_items:
            command = selected_items[0].text(1)
            self.commandSelected.emit(command)

class EnhancedTerminal(QWidget):
    """
    An enhanced secure terminal widget with improved features
    """
    # Signal emitted when a command is executed
    commandExecuted = pyqtSignal(str, str)  # command, result
    
    def __init__(self, config_manager=None, security_manager=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.security_manager = security_manager
        
        # Create secure shell
        self.secure_shell = SecureShell(config_manager, security_manager)
        
        self.setup_ui()
        
        # Set up auto-completion
        self.update_completer()
        
        # Display welcome message
        self.display_welcome()
    
    def setup_ui(self):
        """Set up the terminal UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
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
        splitter.addWidget(self.output_display)
        
        # Help sidebar (hidden by default)
        self.help_sidebar = QTreeWidget()
        self.help_sidebar.setHeaderLabels(["Command", "Description"])
        self.help_sidebar.setColumnWidth(0, 100)
        self.help_sidebar.itemClicked.connect(self.on_help_item_clicked)
        self.help_sidebar.setVisible(False)  # Hidden by default
        splitter.addWidget(self.help_sidebar)
        
        # Set splitter sizes (output display gets more space)
        splitter.setSizes([700, 300])
        
        layout.addWidget(splitter, 1)  # 1 = stretch factor
        
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
        
        # Command buttons
        self.history_button = QPushButton("History")
        self.history_button.setFixedWidth(60)
        self.history_button.clicked.connect(self.show_history_dialog)
        
        self.help_button = QPushButton("Help")
        self.help_button.setFixedWidth(60)
        self.help_button.setCheckable(True)
        self.help_button.clicked.connect(self.toggle_help_sidebar)
        
        input_layout.addWidget(self.prompt_label)
        input_layout.addWidget(self.command_input)
        input_layout.addWidget(self.history_button)
        input_layout.addWidget(self.help_button)
        
        layout.addLayout(input_layout)
        
        # Set up context menu for output display
        self.output_display.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.output_display.customContextMenuRequested.connect(self.show_context_menu)
        
        # Populate help sidebar
        self.update_help_sidebar()
    
    def update_help_sidebar(self):
        """Update the help sidebar with available commands"""
        self.help_sidebar.clear()
        
        # Group commands by category
        categories = {
            "General": ["help", "echo", "version", "info", "clear", "history"],
            "File System": ["ls", "pwd", "cd", "cat"],
            "System Info": ["date", "uptime", "ps", "df", "free"],
            "Administration": ["log", "plugin", "config", "exit", "logout", "shutdown", "restart"]
        }
        
        for category, cmds in categories.items():
            category_item = QTreeWidgetItem([category, ""])
            self.help_sidebar.addTopLevelItem(category_item)
            
            for cmd in cmds:
                if cmd in self.secure_shell.command_help:
                    help_text = self.secure_shell.command_help[cmd]
                    cmd_item = QTreeWidgetItem([cmd, help_text])
                    category_item.addChild(cmd_item)
            
            category_item.setExpanded(True)
    
    def update_completer(self):
        """Update the command completer with available commands"""
        commands = sorted(self.secure_shell.commands.keys())
        self.completer = QCompleter(commands)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.command_input.setCompleter(self.completer)
    
    def display_welcome(self):
        """Display welcome message"""
        welcome_message = """
Secure GUI Platform Terminal
===========================
Type 'help' for a list of available commands.
Press the 'Help' button to view the command reference sidebar.
"""
        self.append_output(welcome_message, "system")
    
    def execute_command(self):
        """Execute the current command"""
        command = self.command_input.text().strip()
        if not command:
            return
        
        # Display command in output with user style
        self.append_output(f"$ {command}", "user")
        
        # Execute command
        result = self.secure_shell.execute(command)
        
        # Handle special results
        if result == "<clear>":
            self.output_display.clear()
        elif result == "<exit>":
            # Just minimize or hide terminal in a real implementation
            self.append_output("Terminal mode exited", "system")
        elif result == "<shutdown>":
            # In a real implementation, this would trigger system shutdown
            self.append_output("System shutdown initiated", "warning")
        elif result == "<restart>":
            # In a real implementation, this would trigger system restart
            self.append_output("System restart initiated", "warning")
        elif result:
            # Display regular result
            self.append_output(result, "result")
        
        # Emit signal
        self.commandExecuted.emit(command, result if result else "")
        
        # Clear input
        self.command_input.clear()
    
    def append_output(self, text, style="normal"):
        """Append text to output display with styling"""
        if not text:
            return
            
        # Create text format based on style
        format = QTextCharFormat()
        
        if style == "user":
            format.setForeground(QColor("#4CAF50"))  # Green
            format.setFontWeight(QFont.Weight.Bold)
        elif style == "result":
            format.setForeground(QColor("#F0F0F0"))  # White
        elif style == "error":
            format.setForeground(QColor("#F44336"))  # Red
        elif style == "warning":
            format.setForeground(QColor("#FFC107"))  # Yellow/Orange
        elif style == "system":
            format.setForeground(QColor("#2196F3"))  # Blue
        
        # Insert text with format
        cursor = self.output_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(text + "\n", format)
        
        # Scroll to bottom
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.output_display.setTextCursor(cursor)
    
    def keyPressEvent(self, event):
        """Handle key events for terminal"""
        # Focus on command input when typing
        if not self.command_input.hasFocus() and event.text().isalnum():
            self.command_input.setFocus()
            self.command_input.setText(event.text())
            self.command_input.setCursorPosition(len(event.text()))
            return
        
        # History navigation is handled in the command input
        if self.command_input.hasFocus():
            # Up arrow for previous command
            if event.key() == Qt.Key.Key_Up:
                self.navigate_history(direction=-1)
                return
            
            # Down arrow for next command
            elif event.key() == Qt.Key.Key_Down:
                self.navigate_history(direction=1)
                return
        
        # Pass other keys to parent
        super().keyPressEvent(event)
    
    def navigate_history(self, direction):
        """Navigate through command history"""
        history = self.secure_shell.command_history
        if not history:
            return
        
        # Get current command
        current_cmd = self.command_input.text()
        
        # Try to find current command in history
        try:
            current_index = history.index(current_cmd)
        except ValueError:
            current_index = len(history) if direction < 0 else -1
        
        # Calculate new index
        new_index = current_index + direction
        
        # Bounds checking
        if 0 <= new_index < len(history):
            self.command_input.setText(history[new_index])
        elif new_index < 0:
            self.command_input.clear()
    
    def show_history_dialog(self):
        """Show command history dialog"""
        dialog = CommandHistoryDialog(self.secure_shell.command_history, self)
        dialog.commandSelected.connect(self.command_input.setText)
        dialog.exec()
    
    def toggle_help_sidebar(self, checked):
        """Toggle the help sidebar visibility"""
        self.help_sidebar.setVisible(checked)
    
    def on_help_item_clicked(self, item, column):
        """Handle help item click"""
        # If it's a command (has a parent), copy it to command input
        if item.parent():
            command = item.text(0)
            self.command_input.setText(command)
            self.command_input.setFocus()
    
    def show_context_menu(self, pos):
        """Show context menu for output display"""
        menu = QMenu(self)
        
        copy_action = QAction("Copy", self)
        copy_action.triggered.connect(self.output_display.copy)
        menu.addAction(copy_action)
        
        select_all_action = QAction("Select All", self)
        select_all_action.triggered.connect(self.output_display.selectAll)
        menu.addAction(select_all_action)
        
        menu.addSeparator()
        
        clear_action = QAction("Clear Terminal", self)
        clear_action.triggered.connect(self.output_display.clear)
        menu.addAction(clear_action)
        
        # Show context menu at cursor position
        menu.exec(self.output_display.mapToGlobal(pos))