"""
Graphical user interface for EFV.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
from pathlib import Path
import json
from datetime import datetime
from .analyzer import FilesystemAnalyzer


class EFVGUI:
    """GUI application for Embedded Filesystem Visualizer."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Embedded Filesystem Visualizer")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2b2b2b')
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('Treeview', background='#3c3c3c', foreground='white', fieldbackground='#3c3c3c')
        self.style.configure('Treeview.Heading', background='#4a4a4a', foreground='white')
        
        self.analyzer = None
        self.report = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="Embedded Filesystem Visualizer",
            font=("Arial", 16, "bold"),
            bg='#2b2b2b',
            fg='white'
        )
        title_label.pack(pady=(0, 20))
        
        # Control frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Path selection
        path_frame = ttk.Frame(control_frame)
        path_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(path_frame, text="Filesystem Path:").pack(side=tk.LEFT)
        self.path_var = tk.StringVar(value="/")
        self.path_entry = ttk.Entry(path_frame, textvariable=self.path_var, width=50)
        self.path_entry.pack(side=tk.LEFT, padx=(10, 5))
        
        ttk.Button(path_frame, text="Browse", command=self.browse_path).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(path_frame, text="Analyze", command=self.start_analysis).pack(side=tk.LEFT)
        
        # Progress bar
        self.progress_var = tk.StringVar(value="Ready")
        self.progress_label = ttk.Label(control_frame, textvariable=self.progress_var)
        self.progress_label.pack(pady=5)
        
        self.progress_bar = ttk.Progressbar(control_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Overview tab
        self.setup_overview_tab()
        
        # File Analysis tab
        self.setup_file_analysis_tab()
        
        # Init Scripts tab
        self.setup_init_scripts_tab()
        
        # Large Files tab
        self.setup_large_files_tab()
        
        # Directory Analysis tab
        self.setup_directory_analysis_tab()
        
        # Bloat Analysis tab
        self.setup_bloat_analysis_tab()
        
        # Export frame
        export_frame = ttk.Frame(main_frame)
        export_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(export_frame, text="Export Report", command=self.export_report).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(export_frame, text="Save as JSON", command=self.save_json).pack(side=tk.LEFT)
    
    def setup_overview_tab(self):
        """Setup the overview tab."""
        overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(overview_frame, text="Overview")
        
        # Overview text
        self.overview_text = scrolledtext.ScrolledText(
            overview_frame,
            wrap=tk.WORD,
            bg='#3c3c3c',
            fg='white',
            insertbackground='white'
        )
        self.overview_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def setup_file_analysis_tab(self):
        """Setup the file analysis tab."""
        file_frame = ttk.Frame(self.notebook)
        self.notebook.add(file_frame, text="File Analysis")
        
        # File types treeview
        file_tree_frame = ttk.Frame(file_frame)
        file_tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Type", "Count", "Percentage")
        self.file_tree = ttk.Treeview(file_tree_frame, columns=columns, show="headings")
        
        for col in columns:
            self.file_tree.heading(col, text=col)
            self.file_tree.column(col, width=150)
        
        self.file_tree.pack(fill=tk.BOTH, expand=True)
    
    def setup_init_scripts_tab(self):
        """Setup the init scripts tab."""
        init_frame = ttk.Frame(self.notebook)
        self.notebook.add(init_frame, text="Init Scripts")
        
        # Init scripts treeview
        init_tree_frame = ttk.Frame(init_frame)
        init_tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Path", "Size", "Permissions", "Interpreter")
        self.init_tree = ttk.Treeview(init_tree_frame, columns=columns, show="headings")
        
        for col in columns:
            self.init_tree.heading(col, text=col)
            self.init_tree.column(col, width=200)
        
        self.init_tree.pack(fill=tk.BOTH, expand=True)
    
    def setup_large_files_tab(self):
        """Setup the large files tab."""
        large_frame = ttk.Frame(self.notebook)
        self.notebook.add(large_frame, text="Large Files")
        
        # Large files treeview
        large_tree_frame = ttk.Frame(large_frame)
        large_tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Rank", "Path", "Size")
        self.large_tree = ttk.Treeview(large_tree_frame, columns=columns, show="headings")
        
        for col in columns:
            self.large_tree.heading(col, text=col)
            self.large_tree.column(col, width=200)
        
        self.large_tree.pack(fill=tk.BOTH, expand=True)
    
    def setup_directory_analysis_tab(self):
        """Setup the directory analysis tab."""
        dir_frame = ttk.Frame(self.notebook)
        self.notebook.add(dir_frame, text="Directory Analysis")
        
        # Directory treeview
        dir_tree_frame = ttk.Frame(dir_frame)
        dir_tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Directory", "Size", "Percentage")
        self.dir_tree = ttk.Treeview(dir_tree_frame, columns=columns, show="headings")
        
        for col in columns:
            self.dir_tree.heading(col, text=col)
            self.dir_tree.column(col, width=250)
        
        self.dir_tree.pack(fill=tk.BOTH, expand=True)
    
    def setup_bloat_analysis_tab(self):
        """Setup the bloat analysis tab."""
        bloat_frame = ttk.Frame(self.notebook)
        self.notebook.add(bloat_frame, text="Bloat Analysis")
        
        # Bloat analysis text
        self.bloat_text = scrolledtext.ScrolledText(
            bloat_frame,
            wrap=tk.WORD,
            bg='#3c3c3c',
            fg='white',
            insertbackground='white'
        )
        self.bloat_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def browse_path(self):
        """Browse for a directory path."""
        path = filedialog.askdirectory(initialdir="/")
        if path:
            self.path_var.set(path)
    
    def start_analysis(self):
        """Start the filesystem analysis in a separate thread."""
        path = self.path_var.get()
        if not os.path.exists(path):
            messagebox.showerror("Error", f"Path '{path}' does not exist.")
            return
        
        # Clear previous results
        self.clear_results()
        
        # Start analysis thread
        self.progress_var.set("Analyzing filesystem...")
        self.progress_bar.start()
        
        thread = threading.Thread(target=self.run_analysis, args=(path,))
        thread.daemon = True
        thread.start()
    
    def run_analysis(self, path):
        """Run the analysis in a separate thread."""
        try:
            self.analyzer = FilesystemAnalyzer(path)
            self.report = self.analyzer.analyze_filesystem()
            
            # Update UI in main thread
            self.root.after(0, self.analysis_complete)
            
        except Exception as e:
            self.root.after(0, lambda: self.analysis_error(str(e)))
    
    def analysis_complete(self):
        """Called when analysis is complete."""
        self.progress_bar.stop()
        self.progress_var.set("Analysis complete!")
        
        # Update all tabs
        self.update_overview()
        self.update_file_analysis()
        self.update_init_scripts()
        self.update_large_files()
        self.update_directory_analysis()
        self.update_bloat_analysis()
        
        messagebox.showinfo("Complete", "Filesystem analysis completed successfully!")
    
    def analysis_error(self, error_msg):
        """Called when analysis encounters an error."""
        self.progress_bar.stop()
        self.progress_var.set("Analysis failed!")
        messagebox.showerror("Error", f"Analysis failed: {error_msg}")
    
    def clear_results(self):
        """Clear all result displays."""
        self.overview_text.delete(1.0, tk.END)
        self.bloat_text.delete(1.0, tk.END)
        
        for tree in [self.file_tree, self.init_tree, self.large_tree, self.dir_tree]:
            for item in tree.get_children():
                tree.delete(item)
    
    def update_overview(self):
        """Update the overview tab."""
        if not self.report:
            return
        
        overview = f"""Filesystem Overview
{'='*50}

Total Files: {self.report['total_files']:,}
Total Size: {self.report['total_size_human']}
Average File Size: {self.analyzer._human_readable_size(self.report['total_size'] // max(self.report['total_files'], 1))}

Mount Information:
"""
        
        if self.report['mount_info']:
            for key, value in self.report['mount_info'].items():
                overview += f"  {key.title()}: {value}\n"
        else:
            overview += "  No mount information available\n"
        
        self.overview_text.delete(1.0, tk.END)
        self.overview_text.insert(1.0, overview)
    
    def update_file_analysis(self):
        """Update the file analysis tab."""
        if not self.report or not self.report['file_types']:
            return
        
        # Clear existing items
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        # Add file types
        total_files = sum(self.report['file_types'].values())
        for file_type, count in sorted(self.report['file_types'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_files) * 100
            self.file_tree.insert("", tk.END, values=(file_type, count, f"{percentage:.1f}%"))
    
    def update_init_scripts(self):
        """Update the init scripts tab."""
        if not self.report or not self.report['init_scripts']:
            return
        
        # Clear existing items
        for item in self.init_tree.get_children():
            self.init_tree.delete(item)
        
        # Add init scripts
        for script in self.report['init_scripts']:
            interpreter = script.get('interpreter', 'N/A')
            self.init_tree.insert("", tk.END, values=(
                script['path'],
                self.analyzer._human_readable_size(script['size']),
                script['permissions'],
                interpreter
            ))
    
    def update_large_files(self):
        """Update the large files tab."""
        if not self.report or not self.report['large_files']:
            return
        
        # Clear existing items
        for item in self.large_tree.get_children():
            self.large_tree.delete(item)
        
        # Add large files
        for i, file_info in enumerate(self.report['large_files'], 1):
            self.large_tree.insert("", tk.END, values=(
                i,
                file_info['path'],
                file_info['size_human']
            ))
    
    def update_directory_analysis(self):
        """Update the directory analysis tab."""
        if not self.report or not self.report['directory_sizes']:
            return
        
        # Clear existing items
        for item in self.dir_tree.get_children():
            self.dir_tree.delete(item)
        
        # Add directory sizes
        sorted_dirs = sorted(
            self.report['directory_sizes'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        total_size = sum(self.report['directory_sizes'].values())
        for directory, size in sorted_dirs[:20]:  # Top 20
            percentage = (size / total_size) * 100
            self.dir_tree.insert("", tk.END, values=(
                directory,
                self.analyzer._human_readable_size(size),
                f"{percentage:.1f}%"
            ))
    
    def update_bloat_analysis(self):
        """Update the bloat analysis tab."""
        if not self.report:
            return
        
        bloat_text = "BLOAT ANALYSIS\n" + "="*40 + "\n\n"
        
        # Analyze potential bloat sources
        bloat_sources = []
        
        # Check for large binaries
        large_binaries = [f for f in self.report['large_files'] if f['size'] > 10*1024*1024]  # > 10MB
        if large_binaries:
            bloat_sources.append(f"Large binaries: {len(large_binaries)} files > 10MB")
        
        # Check for duplicate files (same size)
        size_groups = {}
        for file_path, stats in self.analyzer.file_stats.items():
            size = stats['size']
            if size not in size_groups:
                size_groups[size] = []
            size_groups[size].append(file_path)
        
        duplicates = {size: files for size, files in size_groups.items() if len(files) > 1}
        if duplicates:
            total_duplicate_size = sum(size * (len(files) - 1) for size, files in duplicates.items())
            bloat_sources.append(f"Potential duplicates: {self.analyzer._human_readable_size(total_duplicate_size)}")
        
        # Check for old files
        import time
        current_time = time.time()
        old_files = []
        for file_path, stats in self.analyzer.file_stats.items():
            if current_time - stats['mtime'] > 365 * 24 * 3600:  # > 1 year
                old_files.append(file_path)
        
        if old_files:
            old_files_size = sum(self.analyzer.file_stats[f]['size'] for f in old_files)
            bloat_sources.append(f"Old files (>1 year): {self.analyzer._human_readable_size(old_files_size)}")
        
        if bloat_sources:
            for source in bloat_sources:
                bloat_text += f"• {source}\n"
        else:
            bloat_text += "No obvious bloat sources detected.\n"
        
        self.bloat_text.delete(1.0, tk.END)
        self.bloat_text.insert(1.0, bloat_text)
    
    def export_report(self):
        """Export the report to a text file."""
        if not self.report:
            messagebox.showwarning("Warning", "No analysis report available.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write("Embedded Filesystem Visualizer Report\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(f"Analyzed path: {self.path_var.get()}\n")
                    f.write(f"Total files: {self.report['total_files']:,}\n")
                    f.write(f"Total size: {self.report['total_size_human']}\n")
                    f.write(f"Analysis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                
                messagebox.showinfo("Success", f"Report exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export report: {e}")
    
    def save_json(self):
        """Save the report as JSON."""
        if not self.report:
            messagebox.showwarning("Warning", "No analysis report available.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                # Convert report to JSON-serializable format
                json_report = {
                    'metadata': {
                        'analyzed_path': self.path_var.get(),
                        'total_files': self.report['total_files'],
                        'total_size': self.report['total_size'],
                        'total_size_human': self.report['total_size_human'],
                        'analysis_time': datetime.now().isoformat()
                    },
                    'file_types': self.report['file_types'],
                    'init_scripts': self.report['init_scripts'],
                    'large_files': self.report['large_files'],
                    'directory_sizes': self.report['directory_sizes'],
                    'mount_info': self.report['mount_info']
                }
                
                with open(filename, 'w') as f:
                    json.dump(json_report, f, indent=2)
                
                messagebox.showinfo("Success", f"JSON report saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save JSON: {e}")


def main():
    """Main entry point for GUI application."""
    root = tk.Tk()
    app = EFVGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main() 