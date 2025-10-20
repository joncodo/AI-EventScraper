"""Dependency installer to guarantee critical packages are available."""
import subprocess
import sys
import logging
import importlib
from typing import List, Tuple

logger = logging.getLogger(__name__)

# Critical dependencies that must be available
CRITICAL_DEPENDENCIES = [
    ("atoma", "0.0.12"),
    ("icalendar", "5.0.11"),
    ("dateutil", "2.8.0"),  # python-dateutil imports as dateutil
    ("pytz", "2023.3"),
    ("lxml", "4.9.0"),
]

def install_package(package_name: str, version: str = None) -> bool:
    """Install a package using pip."""
    try:
        # Special case for dateutil - install as python-dateutil
        install_name = "python-dateutil" if package_name == "dateutil" else package_name
        package_spec = f"{install_name}=={version}" if version else install_name
        logger.info(f"Installing {package_spec}...")
        
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "--no-cache-dir", "--force-reinstall", package_spec
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            logger.info(f"✅ Successfully installed {package_spec}")
            return True
        else:
            logger.error(f"❌ Failed to install {package_spec}: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"❌ Timeout installing {package_name}")
        return False
    except Exception as e:
        logger.error(f"❌ Error installing {package_name}: {e}")
        return False

def test_import(package_name: str) -> bool:
    """Test if a package can be imported."""
    try:
        importlib.import_module(package_name)
        logger.info(f"✅ {package_name} import successful")
        return True
    except ImportError as e:
        logger.warning(f"❌ {package_name} import failed: {e}")
        return False

def ensure_dependencies() -> bool:
    """Ensure all critical dependencies are installed and importable."""
    logger.info("🔍 Checking critical dependencies...")
    
    missing_packages = []
    
    # First, test what's already available
    for package_name, version in CRITICAL_DEPENDENCIES:
        if not test_import(package_name):
            missing_packages.append((package_name, version))
    
    if not missing_packages:
        logger.info("✅ All critical dependencies are available!")
        return True
    
    logger.warning(f"⚠️ Missing {len(missing_packages)} critical dependencies")
    
    # Install missing packages
    failed_installs = []
    for package_name, version in missing_packages:
        if not install_package(package_name, version):
            failed_installs.append(package_name)
    
    if failed_installs:
        logger.error(f"❌ Failed to install: {', '.join(failed_installs)}")
        return False
    
    # Test imports again
    logger.info("🔍 Re-testing imports after installation...")
    for package_name, version in CRITICAL_DEPENDENCIES:
        if not test_import(package_name):
            logger.error(f"❌ {package_name} still not importable after installation")
            return False
    
    logger.info("✅ All critical dependencies are now available!")
    return True

def install_with_fallback(package_name: str, version: str = None) -> bool:
    """Install package with multiple fallback methods."""
    methods = [
        # Method 1: Standard install
        lambda: install_package(package_name, version),
        
        # Method 2: Install without dependencies
        lambda: install_package_no_deps(package_name, version),
        
        # Method 3: Install from PyPI with different version
        lambda: install_package(package_name, None),
    ]
    
    for i, method in enumerate(methods, 1):
        logger.info(f"Trying installation method {i} for {package_name}...")
        if method():
            if test_import(package_name):
                return True
        logger.warning(f"Method {i} failed for {package_name}")
    
    return False

def install_package_no_deps(package_name: str, version: str = None) -> bool:
    """Install package without dependencies."""
    try:
        # Special case for dateutil - install as python-dateutil
        install_name = "python-dateutil" if package_name == "dateutil" else package_name
        package_spec = f"{install_name}=={version}" if version else install_name
        logger.info(f"Installing {package_spec} without dependencies...")
        
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "--no-cache-dir", "--no-deps", package_spec
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            logger.info(f"✅ Successfully installed {package_spec} without deps")
            return True
        else:
            logger.error(f"❌ Failed to install {package_spec} without deps: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error installing {package_name} without deps: {e}")
        return False

if __name__ == "__main__":
    # Run dependency check when called directly
    logging.basicConfig(level=logging.INFO)
    success = ensure_dependencies()
    sys.exit(0 if success else 1)
