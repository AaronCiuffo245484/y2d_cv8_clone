.PHONY: docs docs-open tests lint test docker-build
DOCS_INDEX := docs/_build/html/index.html

docs:
	uv run sphinx-apidoc -f -o docs/reference src/thalianacv
	uv run sphinx-build -b html -W docs/ docs/_build/html

docs-open: docs
	uv run python -c "import platform, subprocess; p = '$(DOCS_INDEX)'; s = platform.system(); subprocess.run(['open', p] if s == 'Darwin' else ['cmd', '/c', 'start', '', p] if s == 'Windows' else ['xdg-open', p], check=True)"

tests:
	uv run pytest tests/ -v

lint:
	uv run pre-commit run --all-files

test:
	uv run pytest tests/ -v --cov=src/thalianacv --cov-report=term-missing

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
	uv version --bump patch
	git add pyproject.toml
	git commit -m "chore: bump version to $$(uv version --short)"
	git push
# uncomment the line below once docker is set up
#   $(MAKE) docker-build

release-minor:
	uv version --bump minor
	git add pyproject.toml
	git commit -m "chore: bump version to $$(uv version --short)"
	git push
# uncomment the lines below once docker is set up
#   $(MAKE) docker-build
#   $(MAKE) build
#   $(MAKE) upload

release-major:
	uv version --bump major
	git add pyproject.toml
	git commit -m "chore: bump version to $$(uv version --short)"
	git push
# uncomment the lines below once docker is set up
#   $(MAKE) docker-build
#   $(MAKE) build
#   $(MAKE) upload

help:
	@grep -E '^[a-zA-Z_-]+:' Makefile | sed 's/:.*//' | sort