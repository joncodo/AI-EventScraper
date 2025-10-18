# Contributing to AI Event Scraper

Thank you for your interest in contributing to the AI Event Scraper project! This document provides guidelines and information for contributors.

## Getting Started

### Prerequisites

- Python 3.11+
- MongoDB (local or Atlas)
- OpenAI API key
- Git

### Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/your-username/AI-EventScraper.git
   cd AI-EventScraper
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp config/dev/env.example .env
   # Edit .env with your configuration
   ```

5. **Run tests**
   ```bash
   python -m pytest tests/
   ```

## Development Workflow

### Branch Naming

Use descriptive branch names that indicate the type of change:

- `feature/add-new-scraper` - New features
- `bugfix/fix-api-error` - Bug fixes
- `docs/update-readme` - Documentation updates
- `refactor/cleanup-code` - Code refactoring
- `test/add-unit-tests` - Test additions

### Commit Messages

Follow the conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(scrapers): add LinkedIn Events scraper
fix(api): resolve pagination issue in events endpoint
docs(readme): update installation instructions
test(scrapers): add unit tests for Eventbrite scraper
```

### Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, readable code
   - Add tests for new functionality
   - Update documentation as needed
   - Follow the existing code style

3. **Test your changes**
   ```bash
   python -m pytest tests/
   python main.py status  # Verify system works
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat(scrapers): add new event source"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Provide a clear description of your changes
   - Reference any related issues
   - Include screenshots for UI changes
   - Ensure all tests pass

## Code Style

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line length**: 100 characters (instead of 80)
- **Import order**: Standard library, third-party, local imports
- **Docstrings**: Use Google style docstrings

### Code Formatting

We use Black for code formatting:

```bash
# Format code
black src/ tests/

# Check formatting
black --check src/ tests/
```

### Linting

We use flake8 for linting:

```bash
# Run linter
flake8 src/ tests/
```

### Type Hints

Use type hints for function parameters and return values:

```python
from typing import List, Optional, Dict, Any

def scrape_events(city: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Scrape events for a given city."""
    pass
```

## Testing

### Test Structure

```
tests/
├── unit/           # Unit tests for individual components
├── integration/    # Integration tests for component interactions
└── e2e/           # End-to-end tests for complete workflows
```

### Writing Tests

**Unit Tests:**
```python
import pytest
from src.scrapers.eventbrite_scraper import EventbriteScraper

def test_eventbrite_scraper_initialization():
    scraper = EventbriteScraper()
    assert scraper.name == "eventbrite"
    assert scraper.base_url == "https://www.eventbrite.com"
```

**Integration Tests:**
```python
import pytest
from src.core.database import db
from src.scrapers.scraper_manager import ScraperManager

@pytest.mark.asyncio
async def test_scraper_manager_integration():
    await db.connect()
    manager = ScraperManager()
    events = await manager.scrape_events("New York", "United States")
    assert len(events) > 0
    await db.disconnect()
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/unit/test_scrapers.py

# Run with coverage
python -m pytest --cov=src tests/

# Run with verbose output
python -m pytest -v
```

## Documentation

### Code Documentation

- Use docstrings for all public functions and classes
- Include type hints for better IDE support
- Add inline comments for complex logic

**Example:**
```python
def scrape_events(self, city: str, limit: int = 100) -> List[Event]:
    """
    Scrape events from the platform for a given city.
    
    Args:
        city: The city name to search for events
        limit: Maximum number of events to return
        
    Returns:
        List of Event objects
        
    Raises:
        ScrapingError: If scraping fails
    """
    pass
```

### API Documentation

- Update API documentation when adding new endpoints
- Include request/response examples
- Document error codes and messages

### README Updates

- Update README.md for significant changes
- Include setup instructions for new features
- Update examples and usage information

## Adding New Scrapers

### Scraper Interface

All scrapers must implement the `BaseScraper` interface:

```python
from abc import ABC, abstractmethod
from typing import List
from src.core.models import Event

class BaseScraper(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the scraper name."""
        pass
    
    @abstractmethod
    async def scrape_events(self, city: str, country: str, limit: int = 100) -> List[Event]:
        """Scrape events for the given location."""
        pass
```

### Example Scraper

```python
class NewPlatformScraper(BaseScraper):
    def __init__(self):
        self.name = "new_platform"
        self.base_url = "https://api.newplatform.com"
    
    async def scrape_events(self, city: str, country: str, limit: int = 100) -> List[Event]:
        """Scrape events from New Platform."""
        # Implementation here
        pass
```

### Registering Scrapers

Add your scraper to the `ScraperManager`:

```python
from src.scrapers.new_platform_scraper import NewPlatformScraper

class ScraperManager:
    def __init__(self):
        self.scrapers = [
            EventbriteScraper(),
            MeetupScraper(),
            FacebookScraper(),
            NewPlatformScraper(),  # Add your scraper here
        ]
```

## Reporting Issues

### Bug Reports

When reporting bugs, please include:

1. **Description**: Clear description of the issue
2. **Steps to reproduce**: Detailed steps to reproduce the bug
3. **Expected behavior**: What you expected to happen
4. **Actual behavior**: What actually happened
5. **Environment**: OS, Python version, dependencies
6. **Logs**: Relevant error messages or logs

### Feature Requests

When requesting features, please include:

1. **Description**: Clear description of the feature
2. **Use case**: Why this feature would be useful
3. **Proposed solution**: How you think it should work
4. **Alternatives**: Other solutions you've considered

## Code Review Process

### Review Checklist

**For Reviewers:**
- [ ] Code follows the style guide
- [ ] Tests are included and pass
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] Performance considerations addressed
- [ ] Error handling is appropriate

**For Authors:**
- [ ] All tests pass
- [ ] Code is properly formatted
- [ ] Documentation is updated
- [ ] PR description is clear
- [ ] Related issues are referenced

### Review Guidelines

- Be constructive and respectful
- Focus on the code, not the person
- Suggest improvements, don't just point out problems
- Ask questions if something is unclear
- Approve when you're confident the code is ready

## Release Process

### Version Numbering

We use semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Version number is incremented
- [ ] CHANGELOG.md is updated
- [ ] Release notes are written
- [ ] Tag is created

## Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different opinions and approaches

### Getting Help

- Check existing issues and discussions
- Ask questions in GitHub Discussions
- Join our community chat (if available)
- Read the documentation thoroughly

## License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to AI Event Scraper! 🚀
