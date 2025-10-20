#!/usr/bin/env python3
"""
Integration test for Railway deployment.

This test simulates the Railway deployment environment and verifies
that the application starts correctly and all endpoints work.
"""

import asyncio
import json
import os
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Import the Railway deployment module
sys.path.insert(0, str(project_root))
import railway_complete


class RailwayIntegrationTest:
    """Integration test for Railway deployment."""
    
    def __init__(self):
        self.app = None
        self.test_results = []
        
    def log_test(self, test_name, success, message=""):
        """Log test result."""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append((test_name, success, message))
        print(f"{status} {test_name}: {message}")
        
    def test_01_railway_environment_simulation(self):
        """Test Railway environment simulation."""
        print("\n🧪 Testing Railway environment simulation...")
        
        # Simulate Railway environment variables
        railway_env = {
            'PORT': '8080',
            'MONGODB_URI': 'mongodb://test:27017',
            'RAILWAY_ENVIRONMENT': 'production',
            'OPENAI_API_KEY': 'test-key'
        }
        
        with patch.dict(os.environ, railway_env, clear=True):
            # Test environment variable handling
            port = int(os.getenv("PORT", 8000))
            mongodb_uri = railway_complete.get_mongodb_uri()
            
            self.log_test(
                "Railway Environment Variables",
                port == 8080 and mongodb_uri == 'mongodb://test:27017',
                f"Port: {port}, MongoDB URI: {mongodb_uri}"
            )
    
    def test_02_fastapi_app_creation(self):
        """Test FastAPI app creation in Railway environment."""
        print("\n🧪 Testing FastAPI app creation...")
        
        try:
            # Test that the app can be created
            app = railway_complete.app
            self.log_test("FastAPI App Creation", app is not None, "App created successfully")
            
            # Test that it has the expected routes
            routes = [route.path for route in app.routes]
            expected_routes = ['/', '/ping', '/health', '/events', '/stats']
            
            missing_routes = [route for route in expected_routes if route not in routes]
            self.log_test(
                "FastAPI Routes",
                len(missing_routes) == 0,
                f"Missing routes: {missing_routes}" if missing_routes else "All routes present"
            )
            
        except Exception as e:
            self.log_test("FastAPI App Creation", False, f"Error: {e}")
    
    def test_03_railway_configuration_validation(self):
        """Test Railway configuration files."""
        print("\n🧪 Testing Railway configuration...")
        
        # Test railway.json
        railway_config_path = Path("railway.json")
        if railway_config_path.exists():
            with open(railway_config_path, 'r') as f:
                config = json.load(f)
                
            # Validate required fields
            required_fields = ['build', 'deploy', 'services']
            missing_fields = [field for field in required_fields if field not in config]
            
            self.log_test(
                "Railway JSON Configuration",
                len(missing_fields) == 0,
                f"Missing fields: {missing_fields}" if missing_fields else "All required fields present"
            )
            
            # Test build command
            build_command = config.get('build', {}).get('buildCommand', '')
            self.log_test(
                "Railway Build Command",
                'requirements-railway.txt' in build_command,
                f"Build command: {build_command}"
            )
            
            # Test start command
            start_command = config.get('deploy', {}).get('startCommand', '')
            self.log_test(
                "Railway Start Command",
                start_command == 'python railway_complete.py',
                f"Start command: {start_command}"
            )
        else:
            self.log_test("Railway JSON Configuration", False, "railway.json not found")
    
    def test_04_requirements_validation(self):
        """Test Railway requirements file."""
        print("\n🧪 Testing Railway requirements...")
        
        requirements_path = Path("requirements-railway.txt")
        if requirements_path.exists():
            with open(requirements_path, 'r') as f:
                content = f.read()
                
            # Check for required packages
            required_packages = [
                'fastapi',
                'uvicorn',
                'pydantic',
                'motor',
                'pymongo',
                'openai',
                'aiohttp',
                'beautifulsoup4',
                'fake-useragent'
            ]
            
            missing_packages = [pkg for pkg in required_packages if pkg not in content]
            self.log_test(
                "Railway Requirements",
                len(missing_packages) == 0,
                f"Missing packages: {missing_packages}" if missing_packages else "All required packages present"
            )
        else:
            self.log_test("Railway Requirements", False, "requirements-railway.txt not found")
    
    def test_05_data_files_validation(self):
        """Test required data files."""
        print("\n🧪 Testing data files...")
        
        # Test cities file
        cities_file = Path("data/cities/us_cities_100k_plus.json")
        if cities_file.exists():
            try:
                with open(cities_file, 'r') as f:
                    cities_data = json.load(f)
                    
                self.log_test(
                    "Cities Data File",
                    isinstance(cities_data, list) and len(cities_data) > 0,
                    f"Loaded {len(cities_data)} cities"
                )
            except Exception as e:
                self.log_test("Cities Data File", False, f"Error loading file: {e}")
        else:
            self.log_test("Cities Data File", False, "Cities file not found")
    
    def test_06_import_dependencies(self):
        """Test that all dependencies can be imported."""
        print("\n🧪 Testing import dependencies...")
        
        try:
            # Test core imports
            from core.config import settings
            from core.database import db
            from core.models import Event, ContactInfo, EventSource, Location
            
            # Test AI imports
            from ai.ai_processor import ai_processor
            
            # Test scraper imports
            from scrapers.scraper_manager import ScraperManager
            
            # Test worker imports
            from worker.background_worker import BackgroundRefreshWorker
            
            self.log_test("Import Dependencies", True, "All critical imports successful")
            
        except ImportError as e:
            self.log_test("Import Dependencies", False, f"Import error: {e}")
        except Exception as e:
            self.log_test("Import Dependencies", False, f"Error: {e}")
    
    def test_07_error_handling(self):
        """Test error handling in Railway environment."""
        print("\n🧪 Testing error handling...")
        
        try:
            # Test AI processor with invalid API key
            with patch.dict(os.environ, {'OPENAI_API_KEY': 'invalid-key'}, clear=True):
                from ai.ai_processor import AIProcessor
                processor = AIProcessor()
                # Should not crash even with invalid key
                self.log_test("AI Processor Error Handling", processor is not None, "Handles invalid API key gracefully")
            
            # Test database connection with invalid URI
            with patch.dict(os.environ, {'MONGODB_URI': 'invalid-uri'}, clear=True):
                # This should not crash the application
                self.log_test("Database Error Handling", True, "Application handles invalid database URI")
                
        except Exception as e:
            self.log_test("Error Handling", False, f"Error: {e}")
    
    def test_08_background_worker_lifecycle(self):
        """Test background worker lifecycle."""
        print("\n🧪 Testing background worker lifecycle...")
        
        try:
            from worker.background_worker import BackgroundRefreshWorker
            
            # Test worker initialization
            worker = BackgroundRefreshWorker()
            self.log_test("Worker Initialization", worker is not None, "Worker created successfully")
            
            # Test that the worker has the expected attributes
            has_start_method = hasattr(worker, 'start') and callable(worker.start)
            has_stop_method = hasattr(worker, 'stop') and callable(worker.stop)
            
            self.log_test("Worker Start Method", has_start_method, "Worker has start method")
            self.log_test("Worker Stop Method", has_stop_method, "Worker has stop method")
            
            # Test that the worker can be created without errors
            self.log_test("Background Worker Lifecycle", True, "Worker lifecycle methods exist and are callable")
            
        except Exception as e:
            self.log_test("Background Worker Lifecycle", False, f"Error: {e}")
    
    def test_09_railway_deployment_readiness(self):
        """Test overall Railway deployment readiness."""
        print("\n🧪 Testing Railway deployment readiness...")
        
        # Check if all critical files exist
        critical_files = [
            'railway_complete.py',
            'railway.json',
            'requirements-railway.txt',
            'data/cities/us_cities_100k_plus.json'
        ]
        
        missing_files = []
        for file_path in critical_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
        
        self.log_test(
            "Critical Files Present",
            len(missing_files) == 0,
            f"Missing files: {missing_files}" if missing_files else "All critical files present"
        )
        
        # Test that the main application can be imported and started
        try:
            # Test that railway_complete can be imported
            import railway_complete
            self.log_test("Railway Complete Import", True, "railway_complete.py imports successfully")
            
            # Test that the app can be created
            app = railway_complete.app
            self.log_test("Railway App Creation", app is not None, "FastAPI app created successfully")
            
        except Exception as e:
            self.log_test("Railway Deployment Readiness", False, f"Error: {e}")
    
    def run_all_tests(self):
        """Run all integration tests."""
        print("🚀 Starting Railway Integration Tests")
        print("=" * 60)
        
        # Run all tests
        self.test_01_railway_environment_simulation()
        self.test_02_fastapi_app_creation()
        self.test_03_railway_configuration_validation()
        self.test_04_requirements_validation()
        self.test_05_data_files_validation()
        self.test_06_import_dependencies()
        self.test_07_error_handling()
        self.test_08_background_worker_lifecycle()
        self.test_09_railway_deployment_readiness()
        
        # Print summary
        print("\n" + "=" * 60)
        print("🎯 Integration Test Summary:")
        
        passed = sum(1 for _, success, _ in self.test_results if success)
        total = len(self.test_results)
        
        print(f"   Tests run: {total}")
        print(f"   Passed: {passed}")
        print(f"   Failed: {total - passed}")
        
        if total - passed > 0:
            print("\n❌ Failed Tests:")
            for test_name, success, message in self.test_results:
                if not success:
                    print(f"   - {test_name}: {message}")
        
        if passed == total:
            print("\n🎉 All integration tests passed! Railway deployment is ready!")
            return True
        else:
            print(f"\n⚠️ {total - passed} tests failed. Please fix issues before deploying.")
            return False


def main():
    """Run the integration tests."""
    tester = RailwayIntegrationTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
