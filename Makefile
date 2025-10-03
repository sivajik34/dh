.PHONY: help install test lint run-local docker-build docker-up docker-down k8s-deploy

help:
	@echo "Available commands:"
	@echo "  make install       - Install dependencies"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Run linting"
	@echo "  make run-local     - Run services locally"
	@echo "  make docker-build  - Build Docker images"
	@echo "  make docker-up     - Start Docker Compose"
	@echo "  make docker-down   - Stop Docker Compose"
	@echo "  make k8s-deploy    - Deploy to Kubernetes"

install:
	pip install -r requirements.txt
	python -m spacy download en_core_web_sm

test:
	pytest tests/ -v --cov=. --cov-report=html

lint:
	flake8 . --max-line-length=120
	black --check .
	mypy . --ignore-missing-imports

format:
	black .
	isort .

run-local:
	@echo "Starting services locally..."
	uvicorn gateway.main:app --reload --port 8000 &
	uvicorn nlu.main:app_nlu --reload --port 8001 &
	uvicorn orchestrator.main:app_orch --reload --port 8004 &

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

k8s-deploy:
	kubectl apply -f k8s/
	kubectl rollout status deployment/gateway -n chatbot

k8s-delete:
	kubectl delete -f k8s/

helm-install:
	helm install chatbot ./helm/chatbot -n chatbot --create-namespace

helm-upgrade:
	helm upgrade chatbot ./helm/chatbot -n chatbot

argocd-deploy:
	kubectl apply -f argocd/application.yaml

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache htmlcov .coverage

init-db:
	psql -U chatbot_user -d chatbot_db -f scripts/init_db.sql
