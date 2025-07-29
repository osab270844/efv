"""
Unit tests for the EFV analyzer module.
"""

import pytest
import tempfile
import os
from pathlib import Path
from efv.analyzer import FilesystemAnalyzer


class TestFilesystemAnalyzer:
    """Test cases for FilesystemAnalyzer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.analyzer = FilesystemAnalyzer(self.temp_dir)
        
        # Create test filesystem structure
        self._create_test_filesystem()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_test_filesystem(self):
        """Create a test filesystem structure."""
        test_path = Path(self.temp_dir)
        
        # Create directories
        (test_path / "bin").mkdir()
        (test_path / "etc").mkdir()
        (test_path / "etc" / "init.d").mkdir()
        (test_path / "usr").mkdir()
        (test_path / "usr" / "bin").mkdir()
        (test_path / "usr" / "lib").mkdir()
        
        # Create test files
        (test_path / "bin" / "bash").write_bytes(b'\x7fELF' + b'\x00' * 1000)
        (test_path / "etc" / "init.d" / "network").write_text("#!/bin/bash\necho 'Starting network'")
        (test_path / "etc" / "rc.local").write_text("#!/bin/bash\necho 'Local startup'")
        (test_path / "usr" / "lib" / "libc.so.6").write_bytes(b'\x7fELF' + b'\x00' * 2000000)
        (test_path / "etc" / "passwd").write_text("root:x:0:0:root:/root:/bin/bash")
        (test_path / "etc" / "hosts").write_text("127.0.0.1 localhost")
    
    def test_init(self):
        """Test analyzer initialization."""
        assert self.analyzer.root_path == Path(self.temp_dir).resolve()
        assert isinstance(self.analyzer.file_stats, dict)
        assert isinstance(self.analyzer.directory_sizes, dict)
        assert isinstance(self.analyzer.init_scripts, list)
        assert isinstance(self.analyzer.large_files, list)
        assert isinstance(self.analyzer.file_types, dict)
    
    def test_collect_file_stats(self):
        """Test file statistics collection."""
        self.analyzer._collect_file_stats()
        
        # Should have collected stats for our test files
        assert len(self.analyzer.file_stats) > 0
        
        # Check that we have stats for known files
        bash_path = str(Path(self.temp_dir) / "bin" / "bash")
        assert bash_path in self.analyzer.file_stats
        
        # Check that stats contain expected keys
        stats = self.analyzer.file_stats[bash_path]
        assert 'size' in stats
        assert 'mode' in stats
        assert 'mtime' in stats
        assert 'uid' in stats
        assert 'gid' in stats
    
    def test_analyze_file_types(self):
        """Test file type analysis."""
        self.analyzer._collect_file_stats()
        self.analyzer._analyze_file_types()
        
        # Should have detected some file types
        assert len(self.analyzer.file_types) > 0
        
        # Should have detected binary files
        assert 'binary' in self.analyzer.file_types or '.so' in self.analyzer.file_types
    
    def test_find_init_scripts(self):
        """Test init script detection."""
        self.analyzer._collect_file_stats()
        self.analyzer._find_init_scripts()
        
        # Should have found init scripts
        assert len(self.analyzer.init_scripts) > 0
        
        # Check for specific init scripts
        init_script_paths = [script['path'] for script in self.analyzer.init_scripts]
        assert any('network' in path for path in init_script_paths)
        assert any('rc.local' in path for path in init_script_paths)
    
    def test_calculate_directory_sizes(self):
        """Test directory size calculation."""
        self.analyzer._collect_file_stats()
        self.analyzer._calculate_directory_sizes()
        
        # Should have calculated sizes for directories
        assert len(self.analyzer.directory_sizes) > 0
        
        # Check that root directory has size
        root_dir = str(Path(self.temp_dir))
        assert root_dir in self.analyzer.directory_sizes
        assert self.analyzer.directory_sizes[root_dir] > 0
    
    def test_find_large_files(self):
        """Test large file detection."""
        self.analyzer._collect_file_stats()
        self.analyzer._find_large_files()
        
        # Should have found large files
        assert len(self.analyzer.large_files) > 0
        
        # Check that files are sorted by size (largest first)
        sizes = [file_info['size'] for file_info in self.analyzer.large_files]
        assert sizes == sorted(sizes, reverse=True)
    
    def test_human_readable_size(self):
        """Test human readable size conversion."""
        assert self.analyzer._human_readable_size(0) == "0B"
        assert self.analyzer._human_readable_size(1024) == "1.0KB"
        assert self.analyzer._human_readable_size(1024 * 1024) == "1.0MB"
        assert self.analyzer._human_readable_size(1024 * 1024 * 1024) == "1.0GB"
    
    def test_generate_report(self):
        """Test report generation."""
        self.analyzer._collect_file_stats()
        self.analyzer._analyze_file_types()
        self.analyzer._find_init_scripts()
        self.analyzer._calculate_directory_sizes()
        self.analyzer._find_large_files()
        
        report = self.analyzer._generate_report()
        
        # Check report structure
        assert 'total_files' in report
        assert 'total_size' in report
        assert 'total_size_human' in report
        assert 'file_types' in report
        assert 'init_scripts' in report
        assert 'large_files' in report
        assert 'directory_sizes' in report
        assert 'mount_info' in report
        
        # Check that values are reasonable
        assert report['total_files'] > 0
        assert report['total_size'] > 0
        assert isinstance(report['total_size_human'], str)
    
    def test_analyze_filesystem(self):
        """Test complete filesystem analysis."""
        report = self.analyzer.analyze_filesystem()
        
        # Should have generated a complete report
        assert isinstance(report, dict)
        assert 'total_files' in report
        assert report['total_files'] > 0
    
    def test_mount_info(self):
        """Test mount information retrieval."""
        mount_info = self.analyzer._get_mount_info()
        
        # Mount info should be a dict (may be empty if not mounted)
        assert isinstance(mount_info, dict)
    
    def test_error_handling(self):
        """Test error handling for non-existent paths."""
        # The analyzer should handle non-existent paths gracefully
        analyzer = FilesystemAnalyzer("/non/existent/path")
        analyzer._collect_file_stats()
        # Should not raise an exception, just collect no files
        assert len(analyzer.file_stats) == 0


class TestFilesystemAnalyzerIntegration:
    """Integration tests for FilesystemAnalyzer."""
    
    def test_empty_directory(self):
        """Test analysis of empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer = FilesystemAnalyzer(temp_dir)
            report = analyzer.analyze_filesystem()
            
            assert report['total_files'] == 0
            assert report['total_size'] == 0
            assert report['total_size_human'] == "0B"
    
    def test_single_file(self):
        """Test analysis of directory with single file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("Hello, World!")
            
            analyzer = FilesystemAnalyzer(temp_dir)
            report = analyzer.analyze_filesystem()
            
            assert report['total_files'] == 1
            assert report['total_size'] > 0
            assert '.txt' in report['file_types']
    
    def test_nested_directories(self):
        """Test analysis of nested directory structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_path = Path(temp_dir)
            
            # Create nested structure
            (test_path / "a" / "b" / "c").mkdir(parents=True)
            (test_path / "a" / "b" / "c" / "file.txt").write_text("Nested file")
            (test_path / "a" / "file.txt").write_text("Parent file")
            
            analyzer = FilesystemAnalyzer(temp_dir)
            report = analyzer.analyze_filesystem()
            
            assert report['total_files'] == 2
            assert report['total_size'] > 0
            
            # Check directory sizes
            assert str(test_path / "a" / "b" / "c") in analyzer.directory_sizes
            assert str(test_path / "a" / "b") in analyzer.directory_sizes
            assert str(test_path / "a") in analyzer.directory_sizes 