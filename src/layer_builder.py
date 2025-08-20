import tempfile
import shutil
import subprocess
import zipfile
from pathlib import Path
from typing import List

# Handle both relative and absolute imports
try:
    from .package_parser import PackageSpec
    from .logger import get_logger
except ImportError:
    from package_parser import PackageSpec
    from logger import get_logger


class LayerBuilder:
    def __init__(self, python_version: str = "python3.10"):
        self.python_version = python_version
        
    def create_layer_zip(self, packages: List[PackageSpec]) -> bytes:
        """Create a Lambda layer zip file with the specified packages."""
        logger = get_logger()
        logger.info("Building Lambda layer", step=True)
        logger.detail("Python version", self.python_version)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            logger.progress("Setting up layer directory structure")
            # Create the Lambda layer directory structure
            layer_dir = Path(temp_dir) / "python"
            layer_dir.mkdir(parents=True)
            logger.detail("Layer directory", str(layer_dir))
            
            # Install packages
            self._install_packages(packages, layer_dir)
            
            # Create zip file
            logger.progress("Creating layer zip file")
            zip_content = self._create_zip(Path(temp_dir))
            
            size_mb = len(zip_content) / (1024 * 1024)
            logger.success(f"Layer zip created successfully ({size_mb:.2f} MB)")
            return zip_content
    
    def _install_packages(self, packages: List[PackageSpec], target_dir: Path):
        """Install packages using pip to the target directory."""
        logger = get_logger()
        logger.progress("Installing packages and dependencies")
        
        pip_cmd = [
            "pip", "install",
            "--target", str(target_dir),
            "--no-cache-dir",
            "--no-deps"  # Install without dependencies first
        ]
        
        # First pass: install packages without dependencies
        logger.info(f"📥 Installing {len(packages)} packages...")
        for i, pkg in enumerate(packages, 1):
            logger.progress(f"Installing {pkg.name}", f"{i}/{len(packages)}")
            try:
                result = subprocess.run(
                    pip_cmd + [str(pkg)],
                    check=True,
                    capture_output=True,
                    text=True
                )
                logger.success(f"Installed {pkg.name}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install {pkg}: {e.stderr}")
                raise RuntimeError(f"Failed to install {pkg}: {e.stderr}")
        
        # Second pass: install dependencies
        logger.info("📥 Installing dependencies...")
        deps_cmd = [
            "pip", "install",
            "--target", str(target_dir),
            "--no-cache-dir",
            "--upgrade"  # Ensure we get the latest compatible versions
        ]
        
        for i, pkg in enumerate(packages, 1):
            logger.progress(f"Installing dependencies for {pkg.name}", f"{i}/{len(packages)}")
            try:
                result = subprocess.run(
                    deps_cmd + [str(pkg)],
                    check=True,
                    capture_output=True,
                    text=True
                )
                logger.success(f"Dependencies installed for {pkg.name}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install dependencies for {pkg}: {e.stderr}")
                raise RuntimeError(f"Failed to install dependencies for {pkg}: {e.stderr}")
        
        # Third pass: ensure all sub-dependencies are properly installed
        logger.info("📥 Verifying complete dependency tree...")
        verify_cmd = [
            "pip", "install",
            "--target", str(target_dir),
            "--no-cache-dir",
            "--upgrade",
            "--force-reinstall"
        ]
        
        # Install all packages one more time to ensure completeness
        all_packages = [str(pkg) for pkg in packages]
        if all_packages:
            logger.progress("Final dependency verification", "ensuring completeness")
            try:
                result = subprocess.run(
                    verify_cmd + all_packages,
                    check=True,
                    capture_output=True,
                    text=True
                )
                logger.success("Dependency tree verification completed")
            except subprocess.CalledProcessError as e:
                logger.warning(f"Verification step had issues but continuing: {e.stderr}")
        
        # Clean up unnecessary files
        logger.progress("Cleaning up unnecessary files")
        self._cleanup_layer_dir(target_dir)
        logger.success("Package installation completed")
    
    def _cleanup_layer_dir(self, layer_dir: Path):
        """Remove unnecessary files from the layer directory."""
        logger = get_logger()
        
        # More conservative cleanup - only remove clearly unnecessary files
        patterns_to_remove = [
            "*.pyc", "__pycache__", "*.pyo", "*.pyd"
        ]
        
        # Directories to remove (but be more selective)
        dirs_to_remove = [
            "tests", "test", "testing", 
            "examples", "example",
            "benchmarks", "benchmark"
        ]
        
        removed_count = 0
        
        # Remove file patterns
        for pattern in patterns_to_remove:
            for path in layer_dir.rglob(pattern):
                if path.is_file():
                    path.unlink()
                    removed_count += 1
                elif path.is_dir():
                    shutil.rmtree(path, ignore_errors=True)
                    removed_count += 1
        
        # Remove specific directories but keep docs that might be needed
        for dir_name in dirs_to_remove:
            for path in layer_dir.rglob(dir_name):
                if path.is_dir():
                    # Only remove if it's clearly a test/example directory
                    parent_name = path.parent.name.lower()
                    if any(test_word in parent_name for test_word in ['test', 'example', 'benchmark']):
                        shutil.rmtree(path, ignore_errors=True)
                        removed_count += 1
                    elif path.name.lower() in dirs_to_remove:
                        shutil.rmtree(path, ignore_errors=True)
                        removed_count += 1
        
        # Remove .dist-info and .egg-info but keep them if they contain important metadata
        for info_dir in layer_dir.rglob("*.dist-info"):
            if info_dir.is_dir():
                shutil.rmtree(info_dir, ignore_errors=True)
                removed_count += 1
                
        for info_dir in layer_dir.rglob("*.egg-info"):
            if info_dir.is_dir():
                shutil.rmtree(info_dir, ignore_errors=True)
                removed_count += 1
        
        if removed_count > 0:
            logger.detail("Cleanup", f"Removed {removed_count} unnecessary files/directories")
        else:
            logger.detail("Cleanup", "No unnecessary files found to remove")
    
    def _create_zip(self, source_dir: Path) -> bytes:
        """Create a zip file from the source directory."""
        logger = get_logger()
        zip_buffer = tempfile.NamedTemporaryFile()
        
        # Count files first for progress
        files = [f for f in source_dir.rglob('*') if f.is_file()]
        logger.detail("Files to compress", str(len(files)))
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for i, file_path in enumerate(files, 1):
                arcname = file_path.relative_to(source_dir)
                zipf.write(file_path, arcname)
                
                if i % 100 == 0 or i == len(files):
                    logger.progress(f"Compressing files", f"{i}/{len(files)}")
        
        zip_buffer.seek(0)
        return zip_buffer.read() 