dev:
	uvicorn app.main:app --reload
up:
	docker compose up -d
down:
	docker compose down
logs:
	docker compose logs -f api
migrate:
	alembic upgrade head
test:
	pytest -q
lint:
	ruff check app tests
skill-check:
	python third_party/manju-laoli-skill/short-drama-director/scripts/check_package.py
worker-logs:
	docker compose logs -f worker
