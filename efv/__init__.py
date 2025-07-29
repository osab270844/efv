"""
Embedded Filesystem Visualizer (EFV)
Analyze mounted rootfs filesystems and provide detailed insights.
"""

__version__ = "1.0.0"
__author__ = "Osama Abdelkader"
__email__ = "osama.abdelkader@gmail.com"

from .analyzer import FilesystemAnalyzer

__all__ = ["FilesystemAnalyzer"] 