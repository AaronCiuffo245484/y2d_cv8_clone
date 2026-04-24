.PHONY: docs docs-open tests lint test docker-build
DOCS_INDEX := docs/_build/html/index.html
docs:
	poetry run sphinx-apidoc -f -o docs/reference src/thalianacv
	poetry run sphinx-build -b html -W docs/ docs/_build/html
docs-open: docs
	poetry run python -c "import platform, subprocess; p = '$(DOCS_INDEX)'; s = platform.system(); subprocess.run(['open', p] if s == 'Darwin' else ['cmd', '/c', 'start', '', p] if s == 'Windows' else ['xdg-open', p], check=True)"
tests:
	poetry run pytest tests/ -v
lint:
	poetry run pre-commit run --all-files
test:
	poetry run pytest tests/ -v --cov=src/thalianacv --cov-report=term-missing
docker-build:
	docker buildx build --platform linux/amd64,linux/arm64 .

# docker-build:
#   docker buildx build --platform linux/amd64,linux/arm64 \
#      -t $(REGISTRY)/$(IMAGE):$(VERSION) \
#      -t $(REGISTRY)/$(IMAGE):latest \
#      --push .

# docker-push:
#   docker push $(REGISTRY)/$(IMAGE):$(VERSION)
#   docker push $(REGISTRY)/$(IMAGE):latest

release-patch:
	poetry version patch
	git add pyproject.toml
	git commit -m "chore: bump version to $$(poetry version -s)"
	git push
# uncomment the line below once docker is set up
#   $(MAKE) docker-build

release-minor:
	poetry version minor
	git add pyproject.toml
	git commit -m "chore: bump version to $$(poetry version -s)"
	git push
# uncomment the lines below once docker is set up
#   $(MAKE) docker-build
#   $(MAKE) build
#   $(MAKE) upload

release-major:
	poetry version major
	git add pyproject.toml
	git commit -m "chore: bump version to $$(poetry version -s)"
	git push
# uncomment the lines below once docker is set up
#   $(MAKE) docker-build
#   $(MAKE) build
#   $(MAKE) upload

help:
	@grep -E '^[a-zA-Z_-]+:' Makefile | sed 's/:.*//' | sort
