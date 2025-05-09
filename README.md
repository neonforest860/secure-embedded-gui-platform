# Secure Embedded GUI Platform

A secure, locked-down embedded GUI application platform using PyQt6/PySide that runs on FreeBSD (primary) and Linux (secondary), designed for security applications with plugin extensibility, comprehensive theming, and a user-friendly interface.

## Project Overview

This platform provides a kiosk-style interface with:
- No desktop environment requirements
- Administrative sidebar for system management
- Map interface capabilities
- Limited shell access
- No window decorations (users can't exit to system shell)
- Plugin architecture for extensibility
- Comprehensive theming system
- Cross-platform compatibility (FreeBSD/Linux)

## Development Environment

- Primary OS for development: Arch Linux/Garuda
- Production target: FreeBSD (primary), Linux (secondary)
- Framework: PyQt6/PySide6
- Language: Python 3.10+
- Build system: Poetry for dependency management

## Features

- **Secure Window Management**: Prevents users from exiting to the system shell
- **Plugin System**: Extensible architecture for adding functionality
- **Theming Engine**: Comprehensive theming with light/dark modes
- **Admin Controls**: Secure administration interface with authentication
- **Terminal**: Limited shell with command restrictions
- **Map Interface**: Support for geographical data visualization (to be implemented)

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Poetry package manager
- Qt 6.x libraries

### Installation

\`\`\`bash
# Clone the repository
git clone https://github.com/yourusername/secure-embedded-gui-platform.git
cd secure-embedded-gui-platform

# Install dependencies
poetry install

# Run the application
poetry run python main.py
\`\`\`

## Project Structure

\`\`\`
secure_gui_platform/
├── core/               # Core application components
├── plugins/            # Plugin system and built-in plugins
├── themes/             # Theming system
├── ui/                 # User interface components
│   └── widgets/        # Reusable UI widgets
└── utils/              # Utility functions and helpers
\`\`\`

## License

[Insert your license information here]

## Acknowledgments

[Add any acknowledgments here]

