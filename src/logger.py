import sys
from typing import Optional
from datetime import datetime


class Logger:
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.step_counter = 0
    
    def info(self, message: str, step: bool = False):
        """Print info message with optional step numbering."""
        if not self.verbose:
            return
            
        if step:
            self.step_counter += 1
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"\n🔄 [{timestamp}] Step {self.step_counter}: {message}")
        else:
            print(f"ℹ️  {message}")
    
    def success(self, message: str):
        """Print success message."""
        if not self.verbose:
            return
        print(f"✅ {message}")
    
    def warning(self, message: str):
        """Print warning message."""
        if not self.verbose:
            return
        print(f"⚠️  {message}")
    
    def error(self, message: str):
        """Print error message."""
        print(f"❌ {message}", file=sys.stderr)
    
    def progress(self, message: str, details: Optional[str] = None):
        """Print progress message with optional details."""
        if not self.verbose:
            return
            
        print(f"⏳ {message}", end="")
        if details:
            print(f" ({details})", end="")
        print("...")
    
    def detail(self, key: str, value: str):
        """Print key-value details with consistent formatting."""
        if not self.verbose:
            return
        print(f"   📝 {key}: {value}")
    
    def section(self, title: str):
        """Print section header."""
        if not self.verbose:
            return
        print(f"\n{'=' * 50}")
        print(f"🚀 {title}")
        print(f"{'=' * 50}")
    
    def packages_summary(self, packages: list):
        """Print formatted package summary."""
        if not self.verbose:
            return
            
        print(f"\n📦 Packages to process ({len(packages)}):")
        for i, pkg in enumerate(packages, 1):
            print(f"   {i}. {pkg}")


# Global logger instance
_logger = Logger()

def get_logger() -> Logger:
    """Get the global logger instance."""
    return _logger

def set_verbose(verbose: bool):
    """Set global verbosity level."""
    _logger.verbose = verbose 