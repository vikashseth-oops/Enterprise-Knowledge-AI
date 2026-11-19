.PHONY: dev test eval bench lint format docker-build clean help

help:
	@echo "Enterprise Knowledge AI - Automation Targets:"
	@echo "  make dev          - Start backend and frontend in local development mode"
	@echo "  make test         - Run backend and frontend test suites with coverage"
	@echo "  make eval         - Run retrieval evaluation on 100 labeled queries"
	@echo "  make bench        - Run concurrency latency benchmark"
	@echo "  make lint         - Run ruff linter on backend"
	@echo "  make format       - Format backend code with ruff"
	@echo "  make docker-build - Build backend and frontend multi-stage Docker images"
	@echo "  make clean        - Remove caches and build artifacts"

dev:
	@echo "Starting development services..."
	python -m uvicorn app.main:app --app-dir backend --reload --port 8000 &
	cd frontend && npm run dev

test:
	@echo "Running backend test suite..."
	cd backend && pytest tests --cov=app --cov-report=term-missing
	@echo "Running frontend test suite..."
	cd frontend && npm test

eval:
	@echo "Running evaluation suite against 100 labeled queries..."
	cd backend && python evals/run_retrieval_eval.py

bench:
	@echo "Running concurrency benchmark..."
	cd backend && python evals/run_benchmark.py

lint:
	cd backend && ruff check .

format:
	cd backend && ruff format .

docker-build:
	docker compose build

clean:
	rm -rf backend/.pytest_cache backend/__pycache__ frontend/dist frontend/node_modules/.vite
