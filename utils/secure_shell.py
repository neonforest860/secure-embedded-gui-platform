import os
import time
import re
import logging
import subprocess
import shlex
from typing import List, Dict, Callable, Optional, Tuple, Any
from datetime import datetime

class CommandSandbox:
    """
    Sandbox for executing commands with security restrictions
    """
    def __init__(self, working_dir=None):
        self.working_dir = working_dir or os.path.expanduser("~")
        self.environment = self._create_restricted_env()
    
    def _create_restricted_env(self) -> Dict[str, str]:
        """Create a restricted environment for command execution"""
        # Start with a minimal environment
        env = {
            "PATH": "/usr/local/bin:/usr/bin:/bin",
            "LANG": os.environ.get("LANG", "en_US.UTF-8"),
            "HOME": self.working_dir,
            "TERM": "xterm-256color",
            "SECURE_SHELL": "1",  # Mark as running in secure shell
        }
        
        # Add some safe environment variables
        for var in ["TZ", "DISPLAY", "SHELL"]:
            if var in os.environ:
                env[var] = os.environ[var]
        
        return env
    
    def execute(self, command: str, timeout: int = 10) -> Tuple[int, str, str]:
        """
        Execute a command in the sandbox
        
        Args:
            command: Command to execute
            timeout: Timeout in seconds
        
        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        try:
            # Use subprocess with strict security settings
            process = subprocess.Popen(
                shlex.split(command),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.working_dir,
                env=self.environment,
                shell=False,  # Avoid shell injection
                universal_newlines=True
            )
            
            # Wait for process with timeout
            stdout, stderr = process.communicate(timeout=timeout)
            return_code = process.returncode
            
            return (return_code, stdout, stderr)
        
        except subprocess.TimeoutExpired:
            # Kill process if it times out
            process.kill()
            stdout, stderr = process.communicate()
            return (124, stdout, "Error: Command timed out")
        
        except Exception as e:
            return (1, "", f"Error executing command: {str(e)}")

class SecureShell:
    """
    Secure shell with command whitelist and security controls
    """
    def __init__(self, config_manager=None, security_manager=None):
        self.config_manager = config_manager
        self.security_manager = security_manager
        self.commands: Dict[str, Callable] = {}
        self.command_help: Dict[str, str] = {}
        self.command_history: List[str] = []
        self.max_history = 100
        self.sandbox = CommandSandbox()
        
        # Register built-in commands
        self._register_builtin_commands()
    
    def _register_builtin_commands(self) -> None:
        """Register built-in commands"""
        # Help and information commands
        self.register_command("help", self.cmd_help, "Display help information")
        self.register_command("echo", self.cmd_echo, "Display text")
        self.register_command("version", self.cmd_version, "Display system version")
        self.register_command("info", self.cmd_info, "Display system information")
        
        # File system commands (restricted)
        self.register_command("ls", self.cmd_ls, "List directory contents")
        self.register_command("pwd", self.cmd_pwd, "Show current directory")
        self.register_command("cd", self.cmd_cd, "Change directory")
        self.register_command("cat", self.cmd_cat, "Display file contents")
        
        # System commands
        self.register_command("date", self.cmd_date, "Display current date and time")
        self.register_command("uptime", self.cmd_uptime, "Display system uptime")
        self.register_command("ps", self.cmd_ps, "List running processes")
        self.register_command("df", self.cmd_df, "Display disk usage")
        self.register_command("free", self.cmd_free, "Display memory usage")
        
        # Terminal commands
        self.register_command("clear", self.cmd_clear, "Clear the terminal screen")
        self.register_command("history", self.cmd_history, "Display command history")
        
        # Advanced commands (admin only)
        self.register_command("log", self.cmd_log, "View or modify log settings (admin)")
        self.register_command("plugin", self.cmd_plugin, "Manage plugins (admin)")
        self.register_command("config", self.cmd_config, "View or edit configuration settings (admin)")
        
        # System control commands (admin only)
        self.register_command("exit", self.cmd_exit, "Exit terminal mode")
        self.register_command("logout", self.cmd_logout, "Log out current user")
        self.register_command("shutdown", self.cmd_shutdown, "Shut down the system (admin)")
        self.register_command("restart", self.cmd_restart, "Restart the system (admin)")
    
    def register_command(self, name: str, handler: Callable, help_text: str) -> None:
        """Register a new allowed command"""
        self.commands[name] = handler
        self.command_help[name] = help_text
    
    def execute(self, command_line: str) -> str:
        """
        Execute a command if it's in the whitelist
        
        Args:
            command_line: Command line to execute
        
        Returns:
            Command output as a string
        """
        if not command_line:
            return ""
            
        # Add to history
        self.command_history.append(command_line)
        if len(self.command_history) > self.max_history:
            self.command_history.pop(0)
            
        # Parse command and args
        parts = self._parse_command_line(command_line)
        if not parts:
            return ""
            
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Execute if whitelisted
        if cmd in self.commands:
            # Check if command requires admin and user is authorized
            if cmd in ["log", "plugin", "config", "shutdown", "restart"]:
                if not self._check_admin_access():
                    return "Error: This command requires administrative privileges"
            
            try:
                # Log command execution (before)
                self._log_execution(cmd, args, None)
                
                # Execute command
                result = self.commands[cmd](*args)
                
                # Log successful execution (after)
                self._log_execution(cmd, args, True)
                
                return result
            except Exception as e:
                # Log failed execution
                self._log_execution(cmd, args, False, str(e))
                return f"Error: {e}"
        else:
            return f"Command not found: {cmd}"
    
    def _parse_command_line(self, command_line: str) -> List[str]:
        """
        Parse command line into command and arguments
        Handles quotes and escapes
        """
        try:
            return shlex.split(command_line)
        except ValueError as e:
            return []
    
    def _check_admin_access(self) -> bool:
        """Check if current user has admin access"""
        if self.security_manager:
            return self.security_manager.authorized
        return False
    
    def _log_execution(self, cmd: str, args: List[str], success: Optional[bool], error: str = None) -> None:
        """Log command execution for auditing"""
        # Get current user from security manager
        user = "unknown"
        if self.security_manager:
            user = self.security_manager.current_user
        
        # Create log entry
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user,
            "command": cmd,
            "arguments": args,
            "success": success,
            "error": error
        }
        
        # Log to file (in a real implementation, this would go to a secure log)
        logging.info(f"Terminal: {user} executed '{cmd} {' '.join(args)}' - Success: {success}")
        
        # Could also store in a database or other secure storage
    
    # Command implementations
    
    def cmd_help(self, *args) -> str:
        """Display help information"""
        if args:
            # Help for specific command
            cmd = args[0].lower()
            if cmd in self.command_help:
                return f"{cmd}: {self.command_help[cmd]}"
            else:
                return f"No help available for '{cmd}'"
        
        # General help
        help_text = "Available commands:\n"
        help_text += "------------------\n"
        
        # Group commands by category
        categories = {
            "General": ["help", "echo", "version", "info", "clear", "history"],
            "File System": ["ls", "pwd", "cd", "cat"],
            "System Info": ["date", "uptime", "ps", "df", "free"],
            "Administration": ["log", "plugin", "config", "exit", "logout", "shutdown", "restart"]
        }
        
        for category, cmds in categories.items():
            help_text += f"\n{category}:\n"
            for cmd in cmds:
                if cmd in self.command_help:
                    help_text += f"  {cmd.ljust(10)} - {self.command_help[cmd]}\n"
        
        return help_text
    
    def cmd_echo(self, *args) -> str:
        """Echo the provided text"""
        return " ".join(args)
    
    def cmd_version(self, *args) -> str:
        """Display version information"""
        version = "0.1.0"
        if self.config_manager:
            version = self.config_manager.get("general", "version", "0.1.0")
        return f"Secure GUI Platform v{version}"
    
    def cmd_info(self, *args) -> str:
        """Display system information"""
        info = "System Information:\n"
        info += "------------------\n"
        info += f"Platform: {os.name}\n"
        
        # Add more system info if available
        try:
            import platform
            info += f"OS: {platform.system()} {platform.release()}\n"
            info += f"Python: {platform.python_version()}\n"
        except ImportError:
            pass
        
        return info
    
    def cmd_clear(self, *args) -> str:
        """Clear the terminal screen"""
        # This is typically handled by the terminal widget itself
        return "<clear>"
    
    def cmd_history(self, *args) -> str:
        """Display command history"""
        if not self.command_history:
            return "No commands in history"
        
        history = "Command History:\n"
        history += "----------------\n"
        
        # Determine how many entries to show
        limit = 10  # Default
        if args and args[0].isdigit():
            limit = int(args[0])
        
        # Display history entries
        start = max(0, len(self.command_history) - limit)
        for i, cmd in enumerate(self.command_history[start:], start + 1):
            history += f"{i}: {cmd}\n"
        
        return history
    
    def cmd_ls(self, *args) -> str:
        """List directory contents"""
        # Sanitize path argument
        path = "."
        if args:
            path = args[0]
            
        # Security check - don't allow absolute paths
        if os.path.isabs(path) and not self._check_admin_access():
            return "Error: Absolute paths are restricted"
        
        # Execute ls command through sandbox
        return_code, stdout, stderr = self.sandbox.execute(f"ls -la {path}")
        
        if return_code == 0:
            return stdout
        else:
            return f"Error: {stderr}"
    
    def cmd_pwd(self, *args) -> str:
        """Show current directory"""
        return_code, stdout, stderr = self.sandbox.execute("pwd")
        
        if return_code == 0:
            return stdout.strip()
        else:
            return f"Error: {stderr}"
    
    def cmd_cd(self, *args) -> str:
        """Change directory"""
        # Sanitize path argument
        path = "."
        if args:
            path = args[0]
            
        # Security check - don't allow absolute paths
        if os.path.isabs(path) and not self._check_admin_access():
            return "Error: Absolute paths are restricted"
        
        # Change working directory for sandbox
        try:
            new_path = os.path.join(self.sandbox.working_dir, path)
            if os.path.isdir(new_path):
                self.sandbox.working_dir = os.path.abspath(new_path)
                return f"Current directory: {self.sandbox.working_dir}"
            else:
                return f"Error: Directory '{path}' not found"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def cmd_cat(self, *args) -> str:
        """Display file contents"""
        if not args:
            return "Usage: cat <filename>"
            
        # Sanitize path argument
        path = args[0]
            
        # Security check - don't allow absolute paths
        if os.path.isabs(path) and not self._check_admin_access():
            return "Error: Absolute paths are restricted"
        
        # Execute cat command through sandbox
        return_code, stdout, stderr = self.sandbox.execute(f"cat {path}")
        
        if return_code == 0:
            return stdout
        else:
            return f"Error: {stderr}"
    
    def cmd_date(self, *args) -> str:
        """Display current date and time"""
        return_code, stdout, stderr = self.sandbox.execute("date")
        
        if return_code == 0:
            return stdout.strip()
        else:
            return f"Error: {stderr}"
    
    def cmd_uptime(self, *args) -> str:
        """Display system uptime"""
        return_code, stdout, stderr = self.sandbox.execute("uptime")
        
        if return_code == 0:
            return stdout.strip()
        else:
            return f"Error: {stderr}"
    
    def cmd_ps(self, *args) -> str:
        """List running processes"""
        # Use restricted ps command
        cmd = "ps -eo user,pid,ppid,cmd"
        return_code, stdout, stderr = self.sandbox.execute(cmd)
        
        if return_code == 0:
            return stdout
        else:
            return f"Error: {stderr}"
    
    def cmd_df(self, *args) -> str:
        """Display disk usage"""
        return_code, stdout, stderr = self.sandbox.execute("df -h")
        
        if return_code == 0:
            return stdout
        else:
            return f"Error: {stderr}"
    
    def cmd_free(self, *args) -> str:
        """Display memory usage"""
        # Try different commands based on platform
        if os.name == 'posix':
            return_code, stdout, stderr = self.sandbox.execute("free -h")
            
            if return_code == 0:
                return stdout
            else:
                # Try alternative for macOS
                return_code, stdout, stderr = self.sandbox.execute("vm_stat")
                
                if return_code == 0:
                    return stdout
        
        # Fallback for Windows or other platforms
        return "Memory usage information not available"
    
    def cmd_log(self, *args) -> str:
        """View or modify log settings (admin only)"""
        if not args:
            return "Usage: log <view|level> [args]"
            
        action = args[0].lower()
        
        if action == "view":
            return "Log viewing not implemented in this version"
        elif action == "level":
            if len(args) < 2:
                return "Usage: log level <debug|info|warning|error|critical>"
                
            level = args[1].upper()
            valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            
            if level not in valid_levels:
                return f"Invalid log level. Valid levels are: {', '.join(valid_levels)}"
                
            if self.config_manager:
                self.config_manager.set("general", "log_level", level)
                return f"Log level set to {level}"
            else:
                return "Configuration manager not available"
        else:
            return f"Unknown log action: {action}"
    
    def cmd_plugin(self, *args) -> str:
        """Manage plugins (admin only)"""
        if not args:
            return "Usage: plugin <list|info|enable|disable> [args]"
            
        action = args[0].lower()
        
        if action == "list":
            return "Plugin listing not implemented in this version"
        elif action == "info":
            if len(args) < 2:
                return "Usage: plugin info <plugin_name>"
            return f"Plugin info for '{args[1]}' not implemented in this version"
        elif action == "enable":
            if len(args) < 2:
                return "Usage: plugin enable <plugin_name>"
            return f"Enabling plugin '{args[1]}' not implemented in this version"
        elif action == "disable":
            if len(args) < 2:
                return "Usage: plugin disable <plugin_name>"
            return f"Disabling plugin '{args[1]}' not implemented in this version"
        else:
            return f"Unknown plugin action: {action}"
    
    def cmd_config(self, *args) -> str:
        """View or edit configuration settings (admin only)"""
        if not args:
            return "Usage: config <get|set|list> [section] [key] [value]"
            
        action = args[0].lower()
        
        if self.config_manager is None:
            return "Configuration manager not available"
            
        if action == "get":
            if len(args) < 3:
                return "Usage: config get <section> <key>"
                
            section = args[1]
            key = args[2]
            
            value = self.config_manager.get(section, key, None)
            if value is None:
                return f"Configuration {section}.{key} not found"
            else:
                return f"{section}.{key} = {value}"
                
        elif action == "set":
            if len(args) < 4:
                return "Usage: config set <section> <key> <value>"
                
            section = args[1]
            key = args[2]
            value = args[3]
            
            # Convert value to appropriate type
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            elif value.isdigit():
                value = int(value)
            
            self.config_manager.set(section, key, value)
            return f"Configuration {section}.{key} set to {value}"
            
        elif action == "list":
            if len(args) < 2:
                # List all sections
                sections = self.config_manager.config.keys()
                if not sections:
                    return "No configuration sections found"
                    
                result = "Configuration Sections:\n"
                for section in sorted(sections):
                    result += f"- {section}\n"
                return result
            else:
                # List keys in a section
                section = args[1]
                if section not in self.config_manager.config:
                    return f"Section '{section}' not found"
                    
                keys = self.config_manager.config[section].keys()
                if not keys:
                    return f"No keys found in section '{section}'"
                    
                result = f"Configuration Keys in '{section}':\n"
                for key in sorted(keys):
                    value = self.config_manager.config[section][key]
                    result += f"- {key} = {value}\n"
                return result
        else:
            return f"Unknown config action: {action}"
    
    def cmd_exit(self, *args) -> str:
        """Exit terminal mode"""
        return "<exit>"
    
    def cmd_logout(self, *args) -> str:
        """Log out current user"""
        if self.security_manager:
            self.security_manager.logout()
            return "User logged out successfully"
        return "Logout functionality not available"
    
    def cmd_shutdown(self, *args) -> str:
        """Shut down the system (admin only)"""
        if args and args[0] == "--force":
            return "<shutdown>"
        
        return "System shutdown requires confirmation. Use 'shutdown --force' to confirm."
    
    def cmd_restart(self, *args) -> str:
        """Restart the system (admin only)"""
        if args and args[0] == "--force":
            return "<restart>"
        
        return "System restart requires confirmation. Use 'restart --force' to confirm."