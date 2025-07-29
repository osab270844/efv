# Embedded Filesystem Visualizer (EFV)

A comprehensive tool for analyzing mounted rootfs filesystems (ext4, squashfs, etc.) and providing detailed insights about file sizes, permissions, init scripts, and bloat analysis.

## Features

### 🔍 **Filesystem Analysis**
- **File Statistics**: Complete file size, permission, and metadata analysis
- **Directory Sizing**: Recursive directory size calculation with percentage breakdown
- **File Type Detection**: Automatic detection of binaries, scripts, and various file types
- **Mount Information**: Filesystem mount point and type detection

### 🚀 **Init/Startup Script Detection**
- **Pattern Matching**: Detects init scripts using common naming patterns
- **Shebang Analysis**: Identifies executable scripts by interpreter
- **Permission Analysis**: Shows script permissions and execution rights
- **Interpreter Detection**: Identifies the interpreter used by each script

### 📊 **Bloat Analysis**
- **Large File Detection**: Identifies files larger than 10MB
- **Duplicate Detection**: Finds potential duplicate files by size
- **Age Analysis**: Identifies old files (>1 year)
- **Space Usage**: Detailed breakdown of what's consuming space

### 🖥️ **User Interfaces**
- **Terminal Interface**: Rich, colored terminal output with progress indicators
- **GUI Interface**: Modern tkinter-based graphical interface with tabs
- **Export Options**: Save reports as text or JSON format

## Installation

### Prerequisites
- Python 3.7 or higher
- Linux system (for filesystem analysis)

### Install from PyPI (when published)
```bash
pip install efv
```

### Install from Source
```bash
# Clone the repository
git clone https://github.com/osamakader/efv.git
cd efv

# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### Install Dependencies Only
```bash
pip install -r requirements.txt
```

## Usage

### Terminal Interface

#### Basic Analysis
```bash
# Analyze the current root filesystem
efv

# Analyze a specific path
efv /path/to/rootfs

# Analyze with output to file
efv /path/to/rootfs -o report.txt
```

#### Command Line Options
```bash
efv [PATH] [OPTIONS]

Options:
  PATH                    Path to analyze (default: /)
  -o, --output FILE      Save report to file
  -v, --verbose          Verbose output
  -h, --help            Show help message
```

### GUI Interface

#### Launch GUI
```bash
efv-gui
```

#### GUI Features
- **Path Selection**: Browse or enter filesystem path
- **Tabbed Interface**: 
  - Overview: Filesystem summary and mount info
  - File Analysis: File type breakdown
  - Init Scripts: Startup script detection
  - Large Files: Top 20 largest files
  - Directory Analysis: Directory size breakdown
  - Bloat Analysis: Space optimization suggestions
- **Export Options**: Save reports as text or JSON

## Output Examples

### Terminal Output
```
================================================================================
EMBEDDED FILESYSTEM VISUALIZER REPORT
================================================================================

┌─ Filesystem Overview ─────────────────────────────────────────────────────────┐
│ Total Files: 45,231                                                          │
│ Total Size: 2.3GB                                                            │
│ Average File Size: 52.1KB                                                    │
└───────────────────────────────────────────────────────────────────────────────┘

┌─ Mount Information ──────────────────────────────────────────────────────────┐
│ Device: /dev/sda1                                                           │
│ Mountpoint: /                                                               │
│ Fstype: ext4                                                                │
│ Opts: rw,relatime                                                           │
└───────────────────────────────────────────────────────────────────────────────┘

┌─ File Type Analysis ────────────────────────────────────────────────────────┐
│ .so     │ 1,234 │ 2.7%  │                                                      │
│ .py     │ 890   │ 2.0%  │                                                      │
│ binary  │ 567   │ 1.3%  │                                                      │
│ script  │ 234   │ 0.5%  │                                                      │
└───────────────────────────────────────────────────────────────────────────────┘

┌─ Init/Startup Scripts ─────────────────────────────────────────────────────┐
│ /etc/init.d/network │ 2.1KB │ 755 │ /bin/bash                              │
│ /etc/rc.local       │ 1.8KB │ 755 │ /bin/bash                              │
│ /usr/bin/systemctl  │ 45KB  │ 755 │ N/A                                    │
└───────────────────────────────────────────────────────────────────────────────┘

┌─ Largest Files (Top 20) ──────────────────────────────────────────────────┐
│ 1  │ /usr/lib/libc.so.6        │ 2.1MB │                                    │
│ 2  │ /usr/bin/bash             │ 1.8MB │                                    │
│ 3  │ /usr/lib/libstdc++.so.6   │ 1.5MB │                                    │
└───────────────────────────────────────────────────────────────────────────────┘

┌─ Largest Directories ──────────────────────────────────────────────────────┐
│ /usr/lib     │ 856MB │ 37.2% │                                              │
│ /usr/bin     │ 234MB │ 10.2% │                                              │
│ /var/log     │ 123MB │ 5.3%  │                                              │
└───────────────────────────────────────────────────────────────────────────────┘

BLOAT ANALYSIS
────────────────────────────────────────
• Large binaries: 5 files > 10MB
• Potential duplicates: 45.2MB
• Old files (>1 year): 123.4MB
```

## Use Cases

### Embedded System Analysis
```bash
# Analyze a mounted embedded rootfs
python efv.py /mnt/embedded_rootfs

# Focus on init scripts for boot analysis
python efv.py /mnt/embedded_rootfs | grep -A 10 "Init/Startup Scripts"
```

### Space Optimization
```bash
# Find largest directories for cleanup
python efv.py /path/to/rootfs | grep -A 15 "Largest Directories"

# Identify bloat sources
python efv.py /path/to/rootfs | grep -A 10 "BLOAT ANALYSIS"
```

### Development Environment Analysis
```bash
# Analyze a development container
python efv.py /var/lib/docker/containers/container_id/rootfs
```

## Development

### Setup Development Environment
```bash
# Clone the repository
git clone https://github.com/osab270844/efv.git
cd efv

# Install in development mode with all dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
flake8 efv/ tests/
mypy efv/

# Format code
black efv/ tests/
```

### Available Make Commands
```bash
make help          # Show all available commands
make install       # Install in development mode
make install-dev   # Install with development dependencies
make test          # Run tests
make test-cov      # Run tests with coverage
make lint          # Run linting checks
make format        # Format code
make clean         # Clean build artifacts
make build         # Build the package
make demo          # Run the demo
make cli           # Run the CLI tool
make gui           # Run the GUI tool
make check         # Run all checks (format, lint, test)
```

## Advanced Features

### Custom Analysis
```python
from efv import FilesystemAnalyzer

# Create analyzer
analyzer = FilesystemAnalyzer("/path/to/rootfs")

# Run analysis
report = analyzer.analyze_filesystem()

# Access specific data
print(f"Total files: {report['total_files']}")
print(f"Init scripts: {len(report['init_scripts'])}")
print(f"Large files: {len(report['large_files'])}")
```

### JSON Export
```bash
# Export detailed report as JSON
efv-gui
# Use "Save as JSON" button in GUI
```

## Troubleshooting

### Permission Issues
```bash
# Run with sudo for protected filesystems
sudo python efv.py /path/to/rootfs
```

### Large Filesystem Performance
```bash
# For very large filesystems, use verbose mode to monitor progress
python efv.py /path/to/rootfs -v
```

### GUI Issues
```bash
# Ensure tkinter is available
python -c "import tkinter; print('GUI ready')"
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Roadmap

- [ ] Web-based interface
- [ ] Real-time monitoring
- [ ] Network filesystem support
- [ ] Advanced duplicate detection (content-based)
- [ ] Integration with package managers
- [ ] Automated cleanup suggestions
- [ ] Performance profiling
- [ ] Export to various formats (HTML, PDF, CSV) 