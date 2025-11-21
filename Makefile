.PHONY: test lint format security docs docker clean

# Development
install:
	pip install -r requirements.txt
	npm install --prefix src/js

test:
	pytest src/tests/ -v --cov=src --cov-report=html

lint:
	flake8 src/
	black --check src/
	bandit -r src/

format:
	black src/
	isort src/

security:
	bandit -r src/ -f json
	safety check --json

# Documentation
docs:
	mkdocs serve

docs-build:
	mkdocs build

# Docker
docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Database
db-migrate:
	psql $$DATABASE_URL -f archive/postgres_schema.sql

db-reset: docker-down docker-up
	sleep 5
	$(MAKE) db-migrate

# Deployment
deploy-test:
	./scripts/deploy.sh test

deploy-prod:
	./scripts/deploy.sh prod

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .coverage htmlcov

help:
	@echo "Available commands:"
	@echo "  install     - Install dependencies"
	@echo "  test        - Run tests with coverage"
	@echo "  lint        - Check code quality"
	@echo "  format      - Format code"
	@echo "  security    - Run security checks"
	@echo "  docs        - Serve documentation"
	@echo "  docker-up   - Start development stack"
	@echo "  db-reset    - Reset database"
	@echo "  clean       - Clean temporary files"
