"""
Command-line interface for EFV.
"""

import os
import sys
import time
import argparse
from pathlib import Path
from .analyzer import FilesystemAnalyzer


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Embedded Filesystem Visualizer - Analyze mounted rootfs filesystems"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default="/",
        help="Path to analyze (default: /)"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output report to file"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Check if path exists
    if not os.path.exists(args.path):
        print(f"Error: Path '{args.path}' does not exist.")
        sys.exit(1)
    
    # Create analyzer and run analysis
    analyzer = FilesystemAnalyzer(args.path)
    
    try:
        report = analyzer.analyze_filesystem()
        analyzer.display_report(report)
        
        # Save report to file if requested
        if args.output:
            with open(args.output, 'w') as f:
                f.write("Embedded Filesystem Visualizer Report\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Analyzed path: {args.path}\n")
                f.write(f"Total files: {report['total_files']:,}\n")
                f.write(f"Total size: {report['total_size_human']}\n")
                f.write(f"Analysis completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            print(f"\nReport saved to: {args.output}")
    
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error during analysis: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 