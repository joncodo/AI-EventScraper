# AI Event Scraper Makefile
# Provides convenient commands for development and deployment

.PHONY: help install setup test lint format clean run api scrape docker-build docker-run docker-stop

# Default target
help:
	@echo "AI Event Scraper - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  install     Install dependencies"
	@echo "  setup       Setup development environment"
	@echo "  test        Run tests"
	@echo "  lint        Run linting"
	@echo "  format      Format code"
	@echo "  clean       Clean up temporary files"
	@echo ""
	@echo "Running:"
	@echo "  run         Run the CLI application"
	@echo "  api         Start the API server"
	@echo "  scrape      Run event scraping"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build    Build Docker image"
	@echo "  docker-run      Run with Docker Compose"
	@echo "  docker-stop     Stop Docker containers"
	@echo ""
	@echo "Database:"
	@echo "  db-start    Start MongoDB"
	@echo "  db-stop     Stop MongoDB"
	@echo "  db-reset    Reset database"
	@echo ""
	@echo "Examples:"
	@echo "  make setup"
	@echo "  make api"
	@echo "  make scrape CITY='New York' COUNTRY='United States'"

# Development setup
install:
	pip install -r requirements.txt

setup: install
	@echo "Setting up development environment..."
	@if [ ! -f .env ]; then \
		cp config/dev/env.example .env; \
		echo "Created .env file from template. Please update with your settings."; \
	fi
	@mkdir -p logs data/exports data/samples
	@echo "Development environment setup complete!"

# Testing
test:
	python -m pytest tests/ -v

test-coverage:
	python -m pytest tests/ --cov=src --cov-report=html --cov-report=term

# Code quality
lint:
	flake8 src/ tests/
	mypy src/

format:
	black src/ tests/
	isort src/ tests/

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache/

# Running the application
run:
	python main.py

api:
	python api_server.py --reload

scrape:
	@if [ -z "$(CITY)" ] || [ -z "$(COUNTRY)" ]; then \
		echo "Usage: make scrape CITY='New York' COUNTRY='United States'"; \
		exit 1; \
	fi
	python main.py scrape "$(CITY)" "$(COUNTRY)"

# Docker commands
docker-build:
	docker build -t ai-event-scraper .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Database commands
db-start:
	@if command -v mongod >/dev/null 2>&1; then \
		mongod --dbpath ./data/db --fork --logpath ./logs/mongodb.log; \
		echo "MongoDB started"; \
	else \
		echo "MongoDB not found. Please install MongoDB or use Docker."; \
	fi

db-stop:
	@if pgrep mongod >/dev/null; then \
		pkill mongod; \
		echo "MongoDB stopped"; \
	else \
		echo "MongoDB is not running"; \
	fi

db-reset:
	@echo "Resetting database..."
	@if command -v mongosh >/dev/null 2>&1; then \
		mongosh event_scraper --eval "db.dropDatabase()"; \
		echo "Database reset complete"; \
	else \
		echo "MongoDB shell not found. Please install MongoDB or use Docker."; \
	fi

# Production deployment
deploy-prod:
	@echo "Deploying to production..."
	docker-compose -f docker-compose.prod.yml up -d

# Health checks
health:
	@echo "Checking system health..."
	@curl -f http://localhost:8000/health || echo "API server not responding"
	@if command -v mongosh >/dev/null 2>&1; then \
		mongosh --eval "db.adminCommand('ping')" >/dev/null 2>&1 && echo "MongoDB is healthy" || echo "MongoDB not responding"; \
	fi

# Documentation
docs:
	@echo "Generating documentation..."
	@if command -v sphinx-build >/dev/null 2>&1; then \
		sphinx-build -b html docs/ docs/_build/html; \
		echo "Documentation generated in docs/_build/html/"; \
	else \
		echo "Sphinx not found. Install with: pip install sphinx"; \
	fi

# Cron / background jobs
cron-hourly:
	python scripts/cron_hourly_refresh.py

# Backup
backup:
	@echo "Creating backup..."
	@mkdir -p backups
	@if command -v mongodump >/dev/null 2>&1; then \
		mongodump --db event_scraper --out backups/$(shell date +%Y%m%d_%H%M%S); \
		echo "Backup created in backups/"; \
	else \
		echo "MongoDB tools not found. Please install MongoDB or use Docker."; \
	fi

# Restore
restore:
	@if [ -z "$(BACKUP_DIR)" ]; then \
		echo "Usage: make restore BACKUP_DIR=backups/20250118_120000"; \
		exit 1; \
	fi
	@echo "Restoring from backup..."
	@if command -v mongorestore >/dev/null 2>&1; then \
		mongorestore --db event_scraper $(BACKUP_DIR)/event_scraper; \
		echo "Restore complete"; \
	else \
		echo "MongoDB tools not found. Please install MongoDB or use Docker."; \
	fi

# Development workflow
dev: setup
	@echo "Starting development environment..."
	@make db-start
	@make api

dev-stop:
	@echo "Stopping development environment..."
	@make db-stop
	@make docker-stop

# Cloud deployment
cloud-setup:
	@echo "Setting up for cloud deployment..."
	@if [ ! -f .env ]; then \
		cp config/prod/env.example .env; \
		echo "Created .env file from production template. Please update with your cloud settings."; \
	fi
	@echo "Cloud setup complete! Next steps:"
	@echo "1. Update .env with your MongoDB Atlas URI and OpenAI API key"
	@echo "2. Deploy to your chosen cloud platform (Railway, Render, or Vercel)"
	@echo "3. Run 'make cloud-populate' to populate the cloud database"

cloud-validate:
	python scripts/deploy_to_cloud.py --validate

cloud-test-db:
	python scripts/deploy_to_cloud.py --test-db

cloud-migrate:
	python scripts/deploy_to_cloud.py --migrate

cloud-start:
	python scripts/deploy_to_cloud.py --start

cloud-full-setup:
	python scripts/deploy_to_cloud.py --full-setup

# Database operations
export-local:
	python scripts/export_local_data.py

import-cloud:
	python scripts/migrate_to_cloud.py --import-cloud

cloud-populate:
	python scripts/populate_cloud_db.py --sample-cities --limit 200

cloud-populate-all:
	python scripts/populate_cloud_db.py --all-major-cities --limit 500

cloud-stats:
	python scripts/populate_cloud_db.py --stats

# Quick start
quickstart: setup
	@echo "Quick start setup complete!"
	@echo "Next steps:"
	@echo "1. Update .env with your OpenAI API key"
	@echo "2. Run 'make api' to start the API server"
	@echo "3. Run 'make scrape CITY=\"New York\" COUNTRY=\"United States\"' to scrape events"
	@echo "4. Visit http://localhost:8000/docs for API documentation"

cloud-quickstart: cloud-setup
	@echo "Cloud deployment setup complete!"
	@echo "Next steps:"
	@echo "1. Update .env with your MongoDB Atlas URI and OpenAI API key"
	@echo "2. Deploy to Railway: https://railway.app"
	@echo "3. Deploy to Render: https://render.com"
	@echo "4. Deploy to Vercel: https://vercel.com"
	@echo "5. Run 'make cloud-populate' to populate the cloud database"
