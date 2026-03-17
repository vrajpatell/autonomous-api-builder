PYTHONPATH ?= .

.PHONY: migrate migration-create migration-downgrade migration-check test

migrate:
	alembic upgrade head

migration-create:
	@if [ -z "$(message)" ]; then echo "Usage: make migration-create message=\"add table\""; exit 1; fi
	alembic revision --autogenerate -m "$(message)"

migration-downgrade:
	alembic downgrade -1

migration-check:
	alembic check

test:
	PYTHONPATH=$(PYTHONPATH) pytest -q
