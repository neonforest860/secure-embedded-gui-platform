import os
import time
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QDateEdit, QLineEdit, QGroupBox, QFormLayout, QFileDialog,
    QMessageBox, QCheckBox, QMenu, QSplitter, QTextEdit
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QSortFilterProxyModel, QRegularExpression
from PyQt6.QtGui import QColor, QAction , QFont

class LogEntry:
    """Simple class to represent a log entry"""
    def __init__(self, timestamp, level, source, message, details=None):
        self.timestamp = timestamp
        self.level = level
        self.source = source
        self.message = message
        self.details = details or ""
        
    @staticmethod
    def get_level_color(level):
        """Get color for log level"""
        if level == "DEBUG":
            return QColor(100, 100, 100)  # Dark gray
        elif level == "INFO":
            return QColor(0, 0, 0)  # Black
        elif level == "WARNING":
            return QColor(255, 165, 0)  # Orange
        elif level == "ERROR":
            return QColor(255, 0, 0)  # Red
        elif level == "CRITICAL":
            return QColor(128, 0, 0)  # Dark red
        return QColor(0, 0, 0)  # Default black

class LogFilterPanel(QWidget):
    """Panel for filtering log entries"""
    filterChanged = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the filter UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Time range group
        time_group = QGroupBox("Time Range")
        time_layout = QFormLayout(time_group)
        
        self.time_range = QComboBox()
        self.time_range.addItems([
            "All Time",
            "Last Hour",
            "Last 24 Hours",
            "Last 7 Days",
            "Last 30 Days",
            "Custom Range"
        ])
        self.time_range.currentTextChanged.connect(self.on_time_range_changed)
        time_layout.addRow("Period:", self.time_range)
        
        # Custom date range
        date_layout = QHBoxLayout()
        
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-7))
        self.start_date.setCalendarPopup(True)
        self.start_date.setEnabled(False)
        
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        self.end_date.setEnabled(False)
        
        date_layout.addWidget(QLabel("From:"))
        date_layout.addWidget(self.start_date)
        date_layout.addWidget(QLabel("To:"))
        date_layout.addWidget(self.end_date)
        
        time_layout.addRow("", date_layout)
        
        layout.addWidget(time_group)
        
        # Log level group
        level_group = QGroupBox("Log Level")
        level_layout = QVBoxLayout(level_group)
        
        self.show_debug = QCheckBox("Debug")
        self.show_debug.setChecked(True)
        self.show_debug.stateChanged.connect(self.on_filter_changed)
        
        self.show_info = QCheckBox("Info")
        self.show_info.setChecked(True)
        self.show_info.stateChanged.connect(self.on_filter_changed)
        
        self.show_warning = QCheckBox("Warning")
        self.show_warning.setChecked(True)
        self.show_warning.stateChanged.connect(self.on_filter_changed)
        
        self.show_error = QCheckBox("Error")
        self.show_error.setChecked(True)
        self.show_error.stateChanged.connect(self.on_filter_changed)
        
        self.show_critical = QCheckBox("Critical")
        self.show_critical.setChecked(True)
        self.show_critical.stateChanged.connect(self.on_filter_changed)
        
        level_layout.addWidget(self.show_debug)
        level_layout.addWidget(self.show_info)
        level_layout.addWidget(self.show_warning)
        level_layout.addWidget(self.show_error)
        level_layout.addWidget(self.show_critical)
        
        layout.addWidget(level_group)
        
        # Search group
        search_group = QGroupBox("Search")
        search_layout = QVBoxLayout(search_group)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search in logs...")
        self.search_input.textChanged.connect(self.on_filter_changed)
        
        search_layout.addWidget(self.search_input)
        
        layout.addWidget(search_group)
        
        # Actions group
        actions_group = QGroupBox("Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        self.export_button = QPushButton("Export Logs")
        self.export_button.clicked.connect(self.export_logs)
        
        self.clear_filters_button = QPushButton("Clear Filters")
        self.clear_filters_button.clicked.connect(self.clear_filters)
        
        actions_layout.addWidget(self.export_button)
        actions_layout.addWidget(self.clear_filters_button)
        
        layout.addWidget(actions_group)
        
        # Add spacer
        layout.addStretch(1)
    
    def on_time_range_changed(self, text):
        """Handle time range selection change"""
        custom_range = (text == "Custom Range")
        self.start_date.setEnabled(custom_range)
        self.end_date.setEnabled(custom_range)
        
        # Set default dates based on selection
        if not custom_range:
            today = QDate.currentDate()
            if text == "Last Hour":
                # We can't really set hours in QDateEdit easily, so just use today
                self.start_date.setDate(today)
                self.end_date.setDate(today)
            elif text == "Last 24 Hours":
                self.start_date.setDate(today.addDays(-1))
                self.end_date.setDate(today)
            elif text == "Last 7 Days":
                self.start_date.setDate(today.addDays(-7))
                self.end_date.setDate(today)
            elif text == "Last 30 Days":
                self.start_date.setDate(today.addDays(-30))
                self.end_date.setDate(today)
        
        self.on_filter_changed()
    
    def on_filter_changed(self):
        """Emit signal when any filter changes"""
        self.filterChanged.emit()
    
    def clear_filters(self):
        """Reset all filters to default values"""
        self.time_range.setCurrentText("All Time")
        self.show_debug.setChecked(True)
        self.show_info.setChecked(True)
        self.show_warning.setChecked(True)
        self.show_error.setChecked(True)
        self.show_critical.setChecked(True)
        self.search_input.clear()
    
    def get_filter_criteria(self):
        """Get the current filter criteria"""
        return {
            'time_range': self.time_range.currentText(),
            'start_date': self.start_date.date().toString(Qt.DateFormat.ISODate),
            'end_date': self.end_date.date().toString(Qt.DateFormat.ISODate),
            'show_debug': self.show_debug.isChecked(),
            'show_info': self.show_info.isChecked(),
            'show_warning': self.show_warning.isChecked(),
            'show_error': self.show_error.isChecked(),
            'show_critical': self.show_critical.isChecked(),
            'search_text': self.search_input.text()
        }
    
    def export_logs(self):
        """Export filtered logs to a file"""
        # This will be implemented by the parent widget
        pass

class LogPanel(QWidget):
    """Panel for viewing and filtering logs"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.log_entries = []  # Will be populated with LogEntry objects
        self.setup_ui()
        self.load_dummy_logs()  # For demonstration
    
    def setup_ui(self):
        """Set up the log panel UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("System Logs")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_logs)
        header_layout.addWidget(self.refresh_button)
        
        layout.addLayout(header_layout)
        
        # Create a splitter for filter panel and log view
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Filter panel
        self.filter_panel = LogFilterPanel()
        self.filter_panel.filterChanged.connect(self.apply_filters)
        self.filter_panel.export_button.clicked.connect(self.export_logs)
        
        # Log table
        log_container = QWidget()
        log_layout = QVBoxLayout(log_container)
        log_layout.setContentsMargins(0, 0, 0, 0)
        
        self.log_table = QTableWidget(0, 4)  # timestamp, level, source, message
        self.log_table.setHorizontalHeaderLabels(["Time", "Level", "Source", "Message"])
        self.log_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.log_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Time
        self.log_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Level
        self.log_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Source
        self.log_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.log_table.itemSelectionChanged.connect(self.on_log_selected)
        
        log_layout.addWidget(self.log_table, 1)  # 1 = stretch factor
        
        # Details pane
        self.details_pane = QTextEdit()
        self.details_pane.setReadOnly(True)
        self.details_pane.setMaximumHeight(100)
        log_layout.addWidget(self.details_pane)
        
        # Add panels to splitter
        splitter.addWidget(self.filter_panel)
        splitter.addWidget(log_container)
        
        # Set relative sizes (30% filter panel, 70% log view)
        splitter.setSizes([300, 700])
        
        layout.addWidget(splitter)
    
    def load_dummy_logs(self):
        """Load dummy log entries for demonstration"""
        # Create some dummy log entries
        now = datetime.now()
        
        self.log_entries = [
            LogEntry(
                now - timedelta(minutes=5), 
                "INFO", 
                "ApplicationStartup", 
                "Application started successfully",
                "User: admin\nVersion: 0.1.0\nPlatform: FreeBSD"
            ),
            LogEntry(
                now - timedelta(minutes=4, seconds=30), 
                "DEBUG", 
                "PluginManager", 
                "Discovered 3 plugins",
                "Plugins: Hello World, System Monitor, File Browser"
            ),
            LogEntry(
                now - timedelta(minutes=4), 
                "INFO", 
                "PluginManager", 
                "Loaded plugin: Hello World"
            ),
            LogEntry(
                now - timedelta(minutes=3, seconds=45), 
                "WARNING", 
                "SecurityManager", 
                "Failed login attempt",
                "Username: guest\nIP: 192.168.1.100\nAttempt: 1/3"
            ),
            LogEntry(
                now - timedelta(minutes=3), 
                "INFO", 
                "SecurityManager", 
                "User authenticated successfully",
                "Username: admin\nIP: 192.168.1.100"
            ),
            LogEntry(
                now - timedelta(minutes=2, seconds=30), 
                "ERROR", 
                "FileSystem", 
                "Failed to access restricted file",
                "Path: /etc/passwd\nUser: admin\nReason: Permission denied"
            ),
            LogEntry(
                now - timedelta(minutes=2), 
                "INFO", 
                "PluginManager", 
                "Loaded plugin: System Monitor"
            ),
            LogEntry(
                now - timedelta(minutes=1, seconds=30), 
                "CRITICAL", 
                "HardwareMonitor", 
                "Critical temperature detected",
                "Component: CPU\nTemperature: 95°C\nAction: Throttling"
            ),
            LogEntry(
                now - timedelta(minutes=1), 
                "WARNING", 
                "NetworkManager", 
                "Network connection unstable",
                "Interface: eth0\nPacket loss: 15%\nLatency: 250ms"
            ),
            LogEntry(
                now - timedelta(seconds=30), 
                "INFO", 
                "UserInterface", 
                "User opened System Monitor"
            )
        ]
        
        # Update the table
        self.update_log_table()
    
    def refresh_logs(self):
        """Refresh logs from the system"""
        # In a real implementation, this would read logs from the logging system
        # For now, we just update the table with the same data
        self.update_log_table()
    
    def update_log_table(self):
        """Update the log table with filtered entries"""
        self.log_table.setRowCount(0)  # Clear existing rows
        
        # Get filter criteria
        criteria = self.filter_panel.get_filter_criteria()
        
        # Process each log entry
        for entry in self.log_entries:
            # Check level filter
            if entry.level == "DEBUG" and not criteria['show_debug']:
                continue
            if entry.level == "INFO" and not criteria['show_info']:
                continue
            if entry.level == "WARNING" and not criteria['show_warning']:
                continue
            if entry.level == "ERROR" and not criteria['show_error']:
                continue
            if entry.level == "CRITICAL" and not criteria['show_critical']:
                continue
            
            # Check time filter
            entry_date = entry.timestamp.date().isoformat()
            if criteria['time_range'] != "All Time":
                if criteria['time_range'] == "Custom Range":
                    if entry_date < criteria['start_date'] or entry_date > criteria['end_date']:
                        continue
                elif criteria['time_range'] == "Last Hour":
                    if (datetime.now() - entry.timestamp).total_seconds() > 3600:
                        continue
                elif criteria['time_range'] == "Last 24 Hours":
                    if (datetime.now() - entry.timestamp).total_seconds() > 86400:
                        continue
                elif criteria['time_range'] == "Last 7 Days":
                    if (datetime.now() - entry.timestamp).total_seconds() > 604800:
                        continue
                elif criteria['time_range'] == "Last 30 Days":
                    if (datetime.now() - entry.timestamp).total_seconds() > 2592000:
                        continue
            
            # Check search text
            search_text = criteria['search_text'].lower()
            if search_text and not (
                search_text in entry.message.lower() or
                search_text in entry.source.lower() or
                (entry.details and search_text in entry.details.lower())
            ):
                continue
            
            # Entry passed all filters, add it to the table
            row = self.log_table.rowCount()
            self.log_table.insertRow(row)
            
            # Time
            time_item = QTableWidgetItem(entry.timestamp.strftime("%Y-%m-%d %H:%M:%S"))
            self.log_table.setItem(row, 0, time_item)
            
            # Level
            level_item = QTableWidgetItem(entry.level)
            level_item.setForeground(LogEntry.get_level_color(entry.level))
            level_item.setFont(QFont("Monospace", 9, QFont.Weight.Bold))
            self.log_table.setItem(row, 1, level_item)
            
            # Source
            source_item = QTableWidgetItem(entry.source)
            self.log_table.setItem(row, 2, source_item)
            
            # Message
            message_item = QTableWidgetItem(entry.message)
            self.log_table.setItem(row, 3, message_item)
            
            # Store the log entry index as item data for the first column
            time_item.setData(Qt.ItemDataRole.UserRole, self.log_entries.index(entry))
    
    def on_log_selected(self):
        """Handle log entry selection"""
        selected_items = self.log_table.selectedItems()
        if not selected_items:
            self.details_pane.clear()
            return
        
        # Get the first cell in the selected row
        first_cell = selected_items[0]
        row = first_cell.row()
        time_item = self.log_table.item(row, 0)
        
        # Get the log entry index from the item data
        entry_index = time_item.data(Qt.ItemDataRole.UserRole)
        entry = self.log_entries[entry_index]
        
        # Show details
        if entry.details:
            details_text = f"--- Details for log entry ---\n{entry.details}"
            self.details_pane.setText(details_text)
        else:
            self.details_pane.setText("No additional details available for this log entry.")
    
    def apply_filters(self):
        """Apply the current filters to the log table"""
        self.update_log_table()
    
    def export_logs(self):
        """Export filtered logs to a file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Logs",
            "",
            "Log Files (*.log);;CSV Files (*.csv);;Text Files (*.txt)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w') as f:
                # Write header
                if file_path.endswith('.csv'):
                    f.write("Timestamp,Level,Source,Message,Details\n")
                
                # Get visible rows
                visible_rows = []
                for row in range(self.log_table.rowCount()):
                    time_item = self.log_table.item(row, 0)
                    entry_index = time_item.data(Qt.ItemDataRole.UserRole)
                    visible_rows.append(self.log_entries[entry_index])
                
                # Write entries
                for entry in visible_rows:
                    timestamp_str = entry.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    if file_path.endswith('.csv'):
                        # CSV format
                        details = entry.details.replace('\n', ' ').replace(',', ';')
                        f.write(f'"{timestamp_str}","{entry.level}","{entry.source}","{entry.message}","{details}"\n')
                    else:
                        # Text or log format
                        f.write(f"[{timestamp_str}] {entry.level} [{entry.source}] {entry.message}\n")
                        if entry.details:
                            for line in entry.details.split('\n'):
                                f.write(f"    {line}\n")
            
            QMessageBox.information(self, "Export Successful", f"Logs exported to {file_path}")
        
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export logs: {str(e)}")