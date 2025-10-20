#!/usr/bin/env python3
"""
Comprehensive unit tests for Railway deployment readiness.

This test suite verifies all critical components work correctly
and are ready for Railway deployment.
"""

import asyncio
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Import modules to test
from core.config import settings
from core.database import db
from core.models import Event, ContactInfo, EventSource, Location
from ai.ai_processor import ai_processor
from scrapers.scraper_manager import ScraperManager
from worker.background_worker import BackgroundRefreshWorker, _run_single_pass


class TestRailwayDeployment(unittest.TestCase):
    """Test suite for Railway deployment readiness."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_data_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment."""
        # Clean up any temporary files
        import shutil
        if os.path.exists(self.test_data_dir):
            shutil.rmtree(self.test_data_dir)

    def test_01_imports_work(self):
        """Test that all critical imports work."""
        print("\n🧪 Testing critical imports...")
        
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
        
        print("✅ All critical imports successful")

    def test_02_config_loading(self):
        """Test configuration loading."""
        print("\n🧪 Testing configuration loading...")
        
        # Test that settings can be loaded
        self.assertIsNotNone(settings)
        self.assertIsNotNone(settings.mongodb_url)
        self.assertIsNotNone(settings.mongodb_database)
        
        # Test environment variable handling
        with patch.dict(os.environ, {'MONGODB_URI': 'test://localhost:27017'}):
            from core.config import Settings
            test_settings = Settings()
            # Should use environment variable if available
            self.assertTrue(hasattr(test_settings, 'mongodb_uri'))
        
        print("✅ Configuration loading successful")

    def test_03_ai_processor_initialization(self):
        """Test AI processor initialization with error handling."""
        print("\n🧪 Testing AI processor initialization...")
        
        # Test that AI processor initializes without crashing
        self.assertIsNotNone(ai_processor)
        
        # Test that it handles missing API key gracefully
        with patch.dict(os.environ, {}, clear=True):
            from ai.ai_processor import AIProcessor
            test_processor = AIProcessor()
            self.assertIsNotNone(test_processor)
            # Should have client as None when no API key
            self.assertIsNone(test_processor.client)
        
        print("✅ AI processor initialization successful")

    def test_04_database_models(self):
        """Test database models."""
        print("\n🧪 Testing database models...")
        
        # Test Event model creation
        event = Event(
            title="Test Event",
            description="Test Description",
            start_date="2024-01-01T10:00:00Z",
            location=Location(
                address="123 Test Street",
                city="Test City",
                country="Test Country",
                venue_name="Test Venue"
            ),
            contact_info=ContactInfo(),
            sources=[EventSource(platform="test", url="http://test.com", scraped_at="2024-01-01T10:00:00Z")]
        )
        
        self.assertEqual(event.title, "Test Event")
        self.assertEqual(event.location.city, "Test City")
        self.assertIsNotNone(event.id)
        
        # Test model serialization
        event_dict = event.model_dump()
        self.assertIn("title", event_dict)
        self.assertIn("location", event_dict)
        
        print("✅ Database models working correctly")

    def test_05_scraper_manager_initialization(self):
        """Test scraper manager initialization."""
        print("\n🧪 Testing scraper manager initialization...")
        
        # Test that scraper manager initializes
        scraper_manager = ScraperManager()
        self.assertIsNotNone(scraper_manager)
        self.assertIsInstance(scraper_manager.scrapers, list)
        self.assertGreater(len(scraper_manager.scrapers), 0)
        
        print("✅ Scraper manager initialization successful")

    def test_06_background_worker_initialization(self):
        """Test background worker initialization."""
        print("\n🧪 Testing background worker initialization...")
        
        # Test that background worker initializes
        worker = BackgroundRefreshWorker()
        self.assertIsNotNone(worker)
        self.assertIsNone(worker._task)
        self.assertIsNone(worker._stop_event)
        
        print("✅ Background worker initialization successful")

    @patch('scripts.cron_hourly_refresh.run_hourly_refresh')
    def test_07_background_worker_execution(self, mock_refresh):
        """Test background worker execution."""
        print("\n🧪 Testing background worker execution...")
        
        # Mock the refresh function
        mock_refresh.return_value = AsyncMock()
        
        # Test that the worker can run a single pass
        asyncio.run(_run_single_pass())
        
        # Verify the mock was called
        mock_refresh.assert_called_once()
        
        print("✅ Background worker execution successful")

    def test_08_railway_complete_imports(self):
        """Test that railway_complete.py can be imported."""
        print("\n🧪 Testing railway_complete.py imports...")
        
        # Test importing the main Railway deployment file
        sys.path.insert(0, str(project_root))
        try:
            import railway_complete
            self.assertIsNotNone(railway_complete.app)
            self.assertIsNotNone(railway_complete.connect_to_database)
            print("✅ railway_complete.py imports successful")
        except ImportError as e:
            self.fail(f"Failed to import railway_complete: {e}")

    def test_09_environment_variables(self):
        """Test environment variable handling."""
        print("\n🧪 Testing environment variable handling...")
        
        # Test MongoDB URI handling
        with patch.dict(os.environ, {'MONGODB_URI': 'mongodb://test:27017'}):
            sys.path.insert(0, str(project_root))
            import railway_complete
            uri = railway_complete.get_mongodb_uri()
            self.assertEqual(uri, 'mongodb://test:27017')
        
        # Test fallback handling
        with patch.dict(os.environ, {}, clear=True):
            sys.path.insert(0, str(project_root))
            import railway_complete
            uri = railway_complete.get_mongodb_uri()
            self.assertEqual(uri, 'mongodb://localhost:27017')
        
        print("✅ Environment variable handling successful")

    def test_10_data_files_exist(self):
        """Test that required data files exist."""
        print("\n🧪 Testing data files...")
        
        # Test cities file exists
        cities_file = Path("data/cities/us_cities_100k_plus.json")
        self.assertTrue(cities_file.exists(), f"Cities file not found: {cities_file}")
        
        # Test cities file is valid JSON
        with open(cities_file, 'r') as f:
            cities_data = json.load(f)
            self.assertIsInstance(cities_data, list)
            self.assertGreater(len(cities_data), 0)
        
        print("✅ Data files exist and are valid")

    def test_11_requirements_files(self):
        """Test that requirements files exist and are valid."""
        print("\n🧪 Testing requirements files...")
        
        # Test Railway requirements file
        railway_req = Path("requirements-railway.txt")
        self.assertTrue(railway_req.exists(), "Railway requirements file not found")
        
        # Test that it contains required packages
        with open(railway_req, 'r') as f:
            content = f.read()
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
            for package in required_packages:
                self.assertIn(package, content, f"Required package {package} not found in requirements")
        
        print("✅ Requirements files are valid")

    def test_12_railway_config(self):
        """Test Railway configuration file."""
        print("\n🧪 Testing Railway configuration...")
        
        # Test railway.json exists
        railway_config = Path("railway.json")
        self.assertTrue(railway_config.exists(), "Railway config file not found")
        
        # Test it's valid JSON
        with open(railway_config, 'r') as f:
            config = json.load(f)
            self.assertIn('build', config)
            self.assertIn('deploy', config)
            self.assertIn('services', config)
            
            # Test build command
            self.assertIn('buildCommand', config['build'])
            self.assertIn('requirements-railway.txt', config['build']['buildCommand'])
            
            # Test start command
            self.assertIn('startCommand', config['deploy'])
            self.assertEqual(config['deploy']['startCommand'], 'python railway_complete.py')
        
        print("✅ Railway configuration is valid")

    def test_13_database_connection_function(self):
        """Test database connection function exists and can be called."""
        print("\n🧪 Testing database connection function...")
        
        sys.path.insert(0, str(project_root))
        import railway_complete
        
        # Test that the function exists and is callable
        self.assertTrue(hasattr(railway_complete, 'connect_to_database'))
        self.assertTrue(callable(railway_complete.connect_to_database))
        
        # Test that get_mongodb_uri function works
        self.assertTrue(hasattr(railway_complete, 'get_mongodb_uri'))
        self.assertTrue(callable(railway_complete.get_mongodb_uri))
        
        # Test URI retrieval
        uri = railway_complete.get_mongodb_uri()
        self.assertIsInstance(uri, str)
        self.assertTrue(uri.startswith('mongodb://'))
        
        print("✅ Database connection function working correctly")

    def test_14_fastapi_app_creation(self):
        """Test FastAPI app creation."""
        print("\n🧪 Testing FastAPI app creation...")
        
        sys.path.insert(0, str(project_root))
        import railway_complete
        
        # Test that app is created
        app = railway_complete.app
        self.assertIsNotNone(app)
        
        # Test that it has the expected routes
        routes = [route.path for route in app.routes]
        expected_routes = ['/', '/ping', '/health', '/events', '/stats']
        
        for route in expected_routes:
            self.assertIn(route, routes, f"Expected route {route} not found")
        
        print("✅ FastAPI app creation successful")

    def test_15_error_handling(self):
        """Test error handling in critical components."""
        print("\n🧪 Testing error handling...")
        
        # Test AI processor error handling
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'invalid_key'}):
            from ai.ai_processor import AIProcessor
            processor = AIProcessor()
            # Should not crash even with invalid key
            self.assertIsNotNone(processor)
        
        print("✅ Error handling working correctly")


class TestRailwayDeploymentAsync(unittest.IsolatedAsyncioTestCase):
    """Async test cases for Railway deployment."""
    
    async def test_async_components(self):
        """Test async components."""
        print("\n🧪 Testing async components...")
        
        # Test background worker lifecycle
        worker = BackgroundRefreshWorker()
        
        # Start worker
        worker.start()
        self.assertIsNotNone(worker._task)
        self.assertIsNotNone(worker._stop_event)
        
        # Stop worker
        await worker.stop()
        self.assertIsNone(worker._task)
        self.assertIsNone(worker._stop_event)
        
        print("✅ Async components working correctly")


def run_tests():
    """Run all tests."""
    print("🚀 Starting Railway Deployment Tests")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add sync tests
    suite.addTests(loader.loadTestsFromTestCase(TestRailwayDeployment))
    
    # Add async tests
    suite.addTests(loader.loadTestsFromTestCase(TestRailwayDeploymentAsync))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback}")
    
    if result.errors:
        print("\n❌ Errors:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n🎉 All tests passed! Railway deployment is ready!")
        return True
    else:
        print("\n⚠️ Some tests failed. Please fix issues before deploying.")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
