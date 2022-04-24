SHELL := /bin/bash

.DEFAULT_GOAL := help

help: ## Show help info
	@echo '_________________'
	@echo '| Make targets: |'
	@echo '-----------------'
	@echo
	@cat Makefile | grep -E '^[a-zA-Z\/_-]+:.*?## .*$$' | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
	@echo

users issues attachments: format=$(if $(f),$(f),table)

users: ## Get users from JIRA
	pipenv run python -m main --query users --format=${format}

issues: ## Get issues from JIRA
	pipenv run python -m main --query issues --format=${format}

attachments: ## Get users from JIRA
	pipenv run python -m main --query attachments --format=${format}

install: ## Run pipenv install
	pipenv install

