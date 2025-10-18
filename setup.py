"""Setup script for the AI Event Scraper."""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ai-event-scraper",
    version="1.0.0",
    author="AI Event Scraper Team",
    author_email="team@aieventscraper.com",
    description="A powerful CLI tool that scrapes events from multiple sources with AI processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/AI-EventScraper",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "ai-event-scraper=main:app",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)

