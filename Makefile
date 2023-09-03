.DEFAULT_GOAL := help

# Executables (local)
DOCKER_COMP = docker-compose

CURRENT_UID := $(shell id -u)
CURRENT_GID := $(shell id -g)

PRIVILEGES = ${APP} chown -R $(CURRENT_UID):$(CURRENT_GID)

# Executables
DOCKER_EXEC = $(DOCKER_COMP) exec

# Executables docker containers
APP = $(DOCKER_EXEC) app

help: ## Help message
	@echo "Please choose a task:"
	@grep -E '(^[a-zA-Z_-]+:.*?##.*$$)|(^##)' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[32m%-30s\033[0m %s\n", $$1, $$2}' | sed -e 's/\[32m##/[33m/'

PROJECT_DIR=$(shell dirname $(realpath $(MAKEFILE_LIST)))

ifeq (manage,$(firstword $(MAKECMDGOALS)))
  RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  $(eval $(RUN_ARGS):;@:)
endif

prod: build

install: build start migrate ## Spin-up the project with minimal data

build: ## Build docker containers
	$(DOCKER_COMP) build
	@echo ">>> Base build done!"

shell: ## Run bash inside superapp container
	${APP} bash

rebuild: ## Build docker containers without cache
	$(DOCKER_COMP) build --no-cache
	@echo ">>> Rebuild done!"

start: ## Start all services
	${DOCKER_COMP} up -d
	@echo ">>> Containers started!"

stop: ## Stop all services
	${DOCKER_COMP} stop
	@echo ">>> Containers stopped!"

destroy: ## Stop and remove all containers, networks, images, and volumes
	${DOCKER_COMP} down --volumes --remove-orphans
	@echo ">>> Containers destroyed!"

collectstatic: ## Collectstatic
	${APP} python manage.py collectstatic --noinput
	${APP} chown -R $(CURRENT_UID):$(CURRENT_GID) static
	@echo ">>> Controller done!"

makemigrations: ## Make migrations
	${APP} python manage.py makemigrations
	@echo ">>> Controller done!"

migrate: ## Create new migration
	${APP} python manage.py migrate
	@echo ">>> Migration done!"

celery: ## Run celery server
	${APP} celery -A config worker --loglevel=INFO
	@echo ">>> Celery started"

lint:  ## Python lint
	flake8 src
	@echo ">>> Lint done"

createadmin:  ## Create admin user
	${APP} python manage.py create_admin
	@echo ">>> Admin created, login: admin@gmail.com password:123"

create_products: ## Create products
	${APP} python manage.py create_products
	@echo ">>> Products create"

pytest: ## Run test
	${APP} pytest -rP
	@echo ">>> Test done!"