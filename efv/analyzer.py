"""
Filesystem analyzer module for EFV.
"""

import os
import stat
import time
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional
import psutil
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import colorama
from colorama import Fore, Back, Style

# Initialize colorama for cross-platform colored output
colorama.init()


class FilesystemAnalyzer:
    """Analyzes filesystem structure and provides insights."""
    
    def __init__(self, root_path: str = "/"):
        self.root_path = Path(root_path).resolve()
        self.console = Console()
        self.file_stats = {}
        self.directory_sizes = {}
        self.init_scripts = []
        self.large_files = []
        self.file_types = Counter()
        
    def analyze_filesystem(self) -> Dict:
        """Perform comprehensive filesystem analysis."""
        self.console.print(f"[bold blue]Analyzing filesystem at: {self.root_path}[/bold blue]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Scanning filesystem...", total=None)
            
            # Collect file statistics
            self._collect_file_stats()
            progress.update(task, description="Analyzing file types...")
            
            # Analyze file types
            self._analyze_file_types()
            progress.update(task, description="Finding init scripts...")
            
            # Find init scripts
            self._find_init_scripts()
            progress.update(task, description="Calculating directory sizes...")
            
            # Calculate directory sizes
            self._calculate_directory_sizes()
            progress.update(task, description="Finding large files...")
            
            # Find large files
            self._find_large_files()
            
        return self._generate_report()
    
    def _collect_file_stats(self):
        """Collect basic file statistics."""
        for root, dirs, files in os.walk(self.root_path):
            try:
                for file in files:
                    file_path = Path(root) / file
                    try:
                        stat_info = file_path.stat()
                        self.file_stats[str(file_path)] = {
                            'size': stat_info.st_size,
                            'mode': stat_info.st_mode,
                            'mtime': stat_info.st_mtime,
                            'uid': stat_info.st_uid,
                            'gid': stat_info.st_gid
                        }
                    except (OSError, PermissionError):
                        continue
            except (OSError, PermissionError):
                continue
    
    def _analyze_file_types(self):
        """Analyze file types based on extensions and content."""
        for file_path in self.file_stats:
            path = Path(file_path)
            if path.suffix:
                self.file_types[path.suffix.lower()] += 1
            else:
                # Check if it's a binary, script, or other
                try:
                    with open(path, 'rb') as f:
                        header = f.read(4)
                        if header.startswith(b'#!'):
                            self.file_types['script'] += 1
                        elif header.startswith(b'\x7fELF'):
                            self.file_types['binary'] += 1
                        else:
                            self.file_types['no_extension'] += 1
                except:
                    self.file_types['unknown'] += 1
    
    def _find_init_scripts(self):
        """Find init and startup scripts."""
        init_patterns = [
            'init', 'rc', 'startup', 'boot', 'systemd',
            'upstart', 'sysvinit', 'systemctl'
        ]
        
        for file_path in self.file_stats:
            path = Path(file_path)
            filename = path.name.lower()
            
            # Check for init-related patterns
            if any(pattern in filename for pattern in init_patterns):
                self.init_scripts.append({
                    'path': str(path),
                    'size': self.file_stats[file_path]['size'],
                    'permissions': oct(self.file_stats[file_path]['mode'])[-3:]
                })
            
            # Check for shebang scripts
            try:
                with open(path, 'r') as f:
                    first_line = f.readline().strip()
                    if first_line.startswith('#!'):
                        self.init_scripts.append({
                            'path': str(path),
                            'size': self.file_stats[file_path]['size'],
                            'permissions': oct(self.file_stats[file_path]['mode'])[-3:],
                            'interpreter': first_line[2:]
                        })
            except:
                continue
    
    def _calculate_directory_sizes(self):
        """Calculate total size for each directory."""
        root_path_str = str(self.root_path)
        
        for file_path, stats in self.file_stats.items():
            path = Path(file_path)
            size = stats['size']
            
            # Add size to all parent directories within the analyzed filesystem
            for parent in path.parents:
                parent_str = str(parent)
                # Only include directories that are within the analyzed filesystem
                if parent_str.startswith(root_path_str):
                    if parent_str in self.directory_sizes:
                        self.directory_sizes[parent_str] += size
                    else:
                        self.directory_sizes[parent_str] = size
    
    def _find_large_files(self):
        """Find the largest files in the filesystem."""
        sorted_files = sorted(
            self.file_stats.items(),
            key=lambda x: x[1]['size'],
            reverse=True
        )
        
        self.large_files = [
            {
                'path': file_path,
                'size': stats['size'],
                'size_human': self._human_readable_size(stats['size'])
            }
            for file_path, stats in sorted_files[:20]
        ]
    
    def _human_readable_size(self, size_bytes: int) -> str:
        """Convert bytes to human readable format."""
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f}{size_names[i]}"
    
    def _generate_report(self) -> Dict:
        """Generate comprehensive analysis report."""
        total_files = len(self.file_stats)
        total_size = sum(stats['size'] for stats in self.file_stats.values())
        
        return {
            'total_files': total_files,
            'total_size': total_size,
            'total_size_human': self._human_readable_size(total_size),
            'file_types': dict(self.file_types),
            'init_scripts': self.init_scripts,
            'large_files': self.large_files,
            'directory_sizes': self.directory_sizes,
            'mount_info': self._get_mount_info()
        }
    
    def _get_mount_info(self) -> Dict:
        """Get filesystem mount information."""
        try:
            # Find the mount point that contains the analyzed path
            target_path = str(self.root_path)
            best_match = None
            best_match_length = 0
            
            for partition in psutil.disk_partitions():
                mountpoint = partition.mountpoint
                # Find the mount point that is the longest prefix of our target path
                if target_path.startswith(mountpoint) and len(mountpoint) > best_match_length:
                    best_match = partition
                    best_match_length = len(mountpoint)
            
            if best_match:
                return {
                    'device': best_match.device,
                    'mountpoint': best_match.mountpoint,
                    'fstype': best_match.fstype,
                    'opts': best_match.opts
                }
        except Exception as e:
            # Log the error for debugging
            self.console.print(f"[yellow]Warning: Could not get mount info: {e}[/yellow]")
        return {}
    
    def display_report(self, report: Dict):
        """Display the analysis report in a formatted way."""
        self.console.print("\n" + "="*80)
        self.console.print("[bold green]EMBEDDED FILESYSTEM VISUALIZER REPORT[/bold green]")
        self.console.print("="*80)
        
        # Filesystem Overview
        self._display_overview(report)
        
        # Mount Information
        self._display_mount_info(report['mount_info'])
        
        # File Type Analysis
        self._display_file_types(report['file_types'])
        
        # Init Scripts
        self._display_init_scripts(report['init_scripts'])
        
        # Large Files
        self._display_large_files(report['large_files'])
        
        # Directory Analysis
        self._display_directory_analysis(report['directory_sizes'])
        
        # Bloat Analysis
        self._display_bloat_analysis(report)
    
    def _display_overview(self, report: Dict):
        """Display filesystem overview."""
        panel = Panel(
            f"[bold]Total Files:[/bold] {report['total_files']:,}\n"
            f"[bold]Total Size:[/bold] {report['total_size_human']}\n"
            f"[bold]Average File Size:[/bold] {self._human_readable_size(report['total_size'] // max(report['total_files'], 1))}",
            title="[bold blue]Filesystem Overview[/bold blue]",
            border_style="blue"
        )
        self.console.print(panel)
    
    def _display_mount_info(self, mount_info: Dict):
        """Display mount information."""
        if mount_info:
            table = Table(title="[bold blue]Mount Information[/bold blue]")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="white")
            
            for key, value in mount_info.items():
                table.add_row(key.title(), str(value))
            
            self.console.print(table)
    
    def _display_file_types(self, file_types: Dict):
        """Display file type analysis."""
        if not file_types:
            return
            
        table = Table(title="[bold blue]File Type Analysis[/bold blue]")
        table.add_column("File Type", style="cyan")
        table.add_column("Count", style="green")
        table.add_column("Percentage", style="yellow")
        
        total_files = sum(file_types.values())
        for file_type, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_files) * 100
            table.add_row(file_type, str(count), f"{percentage:.1f}%")
        
        self.console.print(table)
    
    def _display_init_scripts(self, init_scripts: List):
        """Display init scripts found."""
        if not init_scripts:
            self.console.print("[yellow]No init scripts found.[/yellow]")
            return
            
        table = Table(title="[bold blue]Init/Startup Scripts[/bold blue]")
        table.add_column("Path", style="cyan")
        table.add_column("Size", style="green")
        table.add_column("Permissions", style="yellow")
        table.add_column("Interpreter", style="magenta")
        
        for script in init_scripts:
            interpreter = script.get('interpreter', 'N/A')
            table.add_row(
                script['path'],
                self._human_readable_size(script['size']),
                script['permissions'],
                interpreter
            )
        
        self.console.print(table)
    
    def _display_large_files(self, large_files: List):
        """Display largest files."""
        if not large_files:
            return
            
        table = Table(title="[bold blue]Largest Files (Top 20)[/bold blue]")
        table.add_column("Rank", style="cyan")
        table.add_column("Path", style="white")
        table.add_column("Size", style="green")
        
        for i, file_info in enumerate(large_files, 1):
            table.add_row(
                str(i),
                file_info['path'],
                file_info['size_human']
            )
        
        self.console.print(table)
    
    def _display_directory_analysis(self, directory_sizes: Dict):
        """Display directory size analysis."""
        if not directory_sizes:
            return
            
        # Sort directories by size
        sorted_dirs = sorted(
            directory_sizes.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        table = Table(title="[bold blue]Largest Directories[/bold blue]")
        table.add_column("Directory", style="cyan")
        table.add_column("Size", style="green")
        table.add_column("Percentage", style="yellow")
        
        total_size = sum(directory_sizes.values())
        for directory, size in sorted_dirs[:15]:
            percentage = (size / total_size) * 100
            table.add_row(
                directory,
                self._human_readable_size(size),
                f"{percentage:.1f}%"
            )
        
        self.console.print(table)
    
    def _display_bloat_analysis(self, report: Dict):
        """Display bloat analysis."""
        self.console.print("\n[bold red]BLOAT ANALYSIS[/bold red]")
        self.console.print("-" * 40)
        
        # Analyze potential bloat sources
        bloat_sources = []
        
        # Check for large binaries
        large_binaries = [f for f in report['large_files'] if f['size'] > 10*1024*1024]  # > 10MB
        if large_binaries:
            bloat_sources.append(f"Large binaries: {len(large_binaries)} files > 10MB")
        
        # Check for duplicate files (same size)
        size_groups = defaultdict(list)
        for file_path, stats in self.file_stats.items():
            size_groups[stats['size']].append(file_path)
        
        duplicates = {size: files for size, files in size_groups.items() if len(files) > 1}
        if duplicates:
            total_duplicate_size = sum(size * (len(files) - 1) for size, files in duplicates.items())
            bloat_sources.append(f"Potential duplicates: {self._human_readable_size(total_duplicate_size)}")
        
        # Check for old files
        current_time = time.time()
        old_files = []
        for file_path, stats in self.file_stats.items():
            if current_time - stats['mtime'] > 365 * 24 * 3600:  # > 1 year
                old_files.append(file_path)
        
        if old_files:
            old_files_size = sum(self.file_stats[f]['size'] for f in old_files)
            bloat_sources.append(f"Old files (>1 year): {self._human_readable_size(old_files_size)}")
        
        if bloat_sources:
            for source in bloat_sources:
                self.console.print(f"[yellow]• {source}[/yellow]")
        else:
            self.console.print("[green]No obvious bloat sources detected.[/green]") 