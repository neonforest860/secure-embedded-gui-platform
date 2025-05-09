import os
import platform
import psutil
import time
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QGroupBox, QFormLayout, QProgressBar,
    QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QColor

class SystemInfoCollector(QThread):
    """Thread for collecting system information"""
    info_collected = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = False
    
    def run(self):
        """Run the thread"""
        self.running = True
        while self.running:
            # Collect system information
            info = {
                'cpu_percent': psutil.cpu_percent(interval=0.1),
                'memory': psutil.virtual_memory(),
                'disk': psutil.disk_usage('/'),
                'network': psutil.net_io_counters(),
                'processes': []
            }
            
            # Get process information
            for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_percent', 'cpu_percent']):
                try:
                    pinfo = proc.info
                    pinfo['cpu_percent'] = proc.cpu_percent(interval=0)
                    info['processes'].append(pinfo)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            # Sort processes by memory usage
            info['processes'] = sorted(
                info['processes'], 
                key=lambda x: x['memory_percent'],
                reverse=True
            )[:20]  # Top 20 processes
            
            # Emit signal with collected information
            self.info_collected.emit(info)
            
            # Sleep for a bit
            time.sleep(2)
    
    def stop(self):
        """Stop the thread"""
        self.running = False
        self.wait()

class SystemMonitorPanel(QWidget):
    """
    Panel for monitoring system resources and processes
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
        # Start collector thread
        self.collector = SystemInfoCollector()
        self.collector.info_collected.connect(self.update_system_info)
        self.collector.start()
    
    def setup_ui(self):
        """Set up the system monitor UI"""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Overview tab
        overview_tab = QWidget()
        overview_layout = QVBoxLayout(overview_tab)
        
        # System information
        system_group = QGroupBox("System Information")
        system_layout = QFormLayout(system_group)
        
        self.os_label = QLabel()
        system_layout.addRow("Operating System:", self.os_label)
        
        self.hostname_label = QLabel()
        system_layout.addRow("Hostname:", self.hostname_label)
        
        self.cpu_label = QLabel()
        system_layout.addRow("CPU:", self.cpu_label)
        
        self.memory_label = QLabel()
        system_layout.addRow("Memory:", self.memory_label)
        
        self.uptime_label = QLabel()
        system_layout.addRow("Uptime:", self.uptime_label)
        
        overview_layout.addWidget(system_group)
        
        # Resource usage
        resource_group = QGroupBox("Resource Usage")
        resource_layout = QVBoxLayout(resource_group)
        
        # CPU usage
        cpu_layout = QHBoxLayout()
        cpu_layout.addWidget(QLabel("CPU Usage:"))
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)
        cpu_layout.addWidget(self.cpu_bar)
        resource_layout.addLayout(cpu_layout)
        
        # Memory usage
        mem_layout = QHBoxLayout()
        mem_layout.addWidget(QLabel("Memory Usage:"))
        self.mem_bar = QProgressBar()
        self.mem_bar.setRange(0, 100)
        mem_layout.addWidget(self.mem_bar)
        resource_layout.addLayout(mem_layout)
        
        # Disk usage
        disk_layout = QHBoxLayout()
        disk_layout.addWidget(QLabel("Disk Usage:"))
        self.disk_bar = QProgressBar()
        self.disk_bar.setRange(0, 100)
        disk_layout.addWidget(self.disk_bar)
        resource_layout.addLayout(disk_layout)
        
        overview_layout.addWidget(resource_group)
        
        # Network information
        network_group = QGroupBox("Network Information")
        network_layout = QFormLayout(network_group)
        
        self.ip_label = QLabel()
        network_layout.addRow("IP Address:", self.ip_label)
        
        self.network_sent_label = QLabel()
        network_layout.addRow("Data Sent:", self.network_sent_label)
        
        self.network_recv_label = QLabel()
        network_layout.addRow("Data Received:", self.network_recv_label)
        
        overview_layout.addWidget(network_group)
        
        # Add overview tab
        self.tabs.addTab(overview_tab, "Overview")
        
        # Processes tab
        processes_tab = QWidget()
        processes_layout = QVBoxLayout(processes_tab)
        
        # Process table
        self.process_table = QTableWidget(0, 5)
        self.process_table.setHorizontalHeaderLabels([
            "PID", "Name", "User", "CPU %", "Memory %"
        ])
        self.process_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        processes_layout.addWidget(self.process_table)
        
        # Add processes tab
        self.tabs.addTab(processes_tab, "Processes")
        
        # Add tabs to layout
        layout.addWidget(self.tabs)
        
        # Load initial system information
        self.load_static_system_info()
    
    def load_static_system_info(self):
        """Load static system information that doesn't change frequently"""
        # OS information
        os_info = f"{platform.system()} {platform.release()} {platform.machine()}"
        self.os_label.setText(os_info)
        
        # Hostname
        self.hostname_label.setText(platform.node())
        
        # CPU information
        cpu_info = f"{psutil.cpu_count(logical=False)} cores, {psutil.cpu_count()} threads"
        self.cpu_label.setText(cpu_info)
        
        # Memory information
        memory = psutil.virtual_memory()
        memory_total = self.format_bytes(memory.total)
        self.memory_label.setText(memory_total)
        
        # IP address (simple implementation - might need improvement for multiple interfaces)
        try:
            import socket
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            self.ip_label.setText(ip)
        except:
            self.ip_label.setText("Unknown")
    
    def update_system_info(self, info):
        """Update system information with data from collector thread"""
        # Update CPU usage
        self.cpu_bar.setValue(int(info['cpu_percent']))
        cpu_color = self.get_usage_color(info['cpu_percent'])
        self.set_progress_bar_color(self.cpu_bar, cpu_color)
        
        # Update memory usage
        memory = info['memory']
        memory_percent = memory.percent
        self.mem_bar.setValue(int(memory_percent))
        mem_color = self.get_usage_color(memory_percent)
        self.set_progress_bar_color(self.mem_bar, mem_color)
        
        # Update disk usage
        disk = info['disk']
        disk_percent = disk.percent
        self.disk_bar.setValue(int(disk_percent))
        disk_color = self.get_usage_color(disk_percent)
        self.set_progress_bar_color(self.disk_bar, disk_color)
        
        # Update uptime
        boot_time = psutil.boot_time()
        uptime = time.time() - boot_time
        uptime_str = self.format_uptime(uptime)
        self.uptime_label.setText(uptime_str)
        
        # Update network information
        network = info['network']
        self.network_sent_label.setText(self.format_bytes(network.bytes_sent))
        self.network_recv_label.setText(self.format_bytes(network.bytes_recv))
        
        # Update process table
        self.update_process_table(info['processes'])
    
    def update_process_table(self, processes):
        """Update the process table with current processes"""
        # Set the number of rows
        self.process_table.setRowCount(len(processes))
        
        # Populate the table
        for row, proc in enumerate(processes):
            # PID
            self.process_table.setItem(row, 0, QTableWidgetItem(str(proc['pid'])))
            
            # Name
            self.process_table.setItem(row, 1, QTableWidgetItem(proc['name']))
            
            # User
            self.process_table.setItem(row, 2, QTableWidgetItem(proc['username']))
            
            # CPU %
            cpu_item = QTableWidgetItem(f"{proc['cpu_percent']:.1f}%")
            if proc['cpu_percent'] > 50:
                cpu_item.setForeground(QColor(255, 0, 0))  # Red
            elif proc['cpu_percent'] > 20:
                cpu_item.setForeground(QColor(255, 165, 0))  # Orange
            self.process_table.setItem(row, 3, cpu_item)
            
            # Memory %
            mem_item = QTableWidgetItem(f"{proc['memory_percent']:.1f}%")
            if proc['memory_percent'] > 10:
                mem_item.setForeground(QColor(255, 0, 0))  # Red
            elif proc['memory_percent'] > 5:
                mem_item.setForeground(QColor(255, 165, 0))  # Orange
            self.process_table.setItem(row, 4, mem_item)
    
    def format_bytes(self, bytes):
        """Format bytes into a human-readable string"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes < 1024:
                return f"{bytes:.2f} {unit}"
            bytes /= 1024
        return f"{bytes:.2f} PB"
    
    def format_uptime(self, seconds):
        """Format uptime into a human-readable string"""
        days, remainder = divmod(int(seconds), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{days} days, {hours} hours, {minutes} minutes"
        elif hours > 0:
            return f"{hours} hours, {minutes} minutes"
        else:
            return f"{minutes} minutes, {seconds} seconds"
    
    def get_usage_color(self, percent):
        """Get color based on usage percentage"""
        if percent < 60:
            return QColor(0, 200, 0)  # Green
        elif percent < 80:
            return QColor(255, 165, 0)  # Orange
        else:
            return QColor(255, 0, 0)  # Red
    
    def set_progress_bar_color(self, progress_bar, color):
        """Set progress bar color using stylesheet"""
        progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid grey;
                border-radius: 2px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {color.name()};
            }}
        """)
    
    def closeEvent(self, event):
        """Stop the collector thread when the widget is closed"""
        self.collector.stop()
        super().closeEvent(event)