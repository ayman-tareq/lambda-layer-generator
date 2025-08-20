import re
from typing import List

# Handle both relative and absolute imports
try:
    from .logger import get_logger
except ImportError:
    from logger import get_logger


class PackageSpec:
    def __init__(self, name: str, version_spec: str = None):
        self.name = name.strip()
        self.version_spec = version_spec.strip() if version_spec else None
    
    def __str__(self):
        return f"{self.name}{self.version_spec}" if self.version_spec else self.name
    
    @property
    def clean_name(self):
        return re.sub(r'[^a-zA-Z0-9_-]', '', self.name.lower())
    
    @property
    def version_for_description(self):
        """Extract just the version number for description purposes."""
        if not self.version_spec:
            return None
        # Extract version number from specs like >=1.26.1, ==2.5.0, ~=1.0.0
        version_match = re.search(r'[\d\w.-]+$', self.version_spec)
        return version_match.group() if version_match else self.version_spec


def parse_packages(package_string: str) -> List[PackageSpec]:
    """Parse comma-separated package specifications with support for all pip version specifiers."""
    logger = get_logger()
    logger.info("Parsing package specifications", step=True)
    
    if not package_string or not package_string.strip():
        raise ValueError("Package string cannot be empty")
    
    logger.detail("Raw input", package_string)
    
    packages = []
    # Pattern to match package names and version specifiers (>=, >, <=, <, ==, ~=, !=)
    version_pattern = r'^([a-zA-Z0-9_.-]+)\s*(>=|>|<=|<|==|~=|!=)\s*(.+)$'
    
    for pkg in package_string.split(','):
        pkg = pkg.strip()
        if not pkg:
            continue
            
        # Try to match version specifier pattern
        match = re.match(version_pattern, pkg)
        if match:
            name, operator, version = match.groups()
            version_spec = f"{operator}{version}"
            packages.append(PackageSpec(name, version_spec))
            logger.info(f"Parsed: {name} with version constraint {version_spec}")
        else:
            # No version specifier, just package name
            packages.append(PackageSpec(pkg))
            logger.info(f"Parsed: {pkg} (latest version)")
    
    if not packages:
        raise ValueError("No valid packages found in input string")
    
    logger.packages_summary(packages)
    return packages


def generate_layer_name(packages: List[PackageSpec]) -> str:
    """Generate a clean layer name from package names."""
    logger = get_logger()
    
    names = [pkg.clean_name for pkg in packages]
    if len(names) == 1:
        layer_name = f"layer-{names[0]}"
    else:
        layer_name = f"layer-{'-'.join(sorted(names[:3]))}"  # Limit to 3 names for readability
    
    logger.detail("Generated layer name", layer_name)
    return layer_name


def generate_layer_description(packages: List[PackageSpec], python_version: str) -> str:
    """Generate layer description with package versions and Python compatibility."""
    logger = get_logger()
    
    pkg_details = []
    for pkg in packages:
        if pkg.version_for_description:
            pkg_details.append(f"{pkg.name} {pkg.version_for_description}")
        else:
            pkg_details.append(pkg.name)
    
    description = f"Python {python_version} layer with: {', '.join(pkg_details)}"
    logger.detail("Generated description", description)
    return description 