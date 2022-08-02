SHELL := /bin/bash

.DEFAULT_GOAL := help

help: ## Show help info
	@echo '_________________'
	@echo '| Make targets: |'
	@echo '-----------------'
	@echo
	@cat Makefile | grep -E '^[a-zA-Z\/_-]+:.*?## .*$$' | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
	@echo

users issues: format=$(if $(f),$(f),table)

users: ## Get users from JIRA
	pipenv run python -m scrapper.app.main --query users --output_format=${format}
# 	pipenv run python -m scrapper.app.main --query users

issues: ## Get issues from JIRA
	pipenv run python -m scrapper.app.main --query issues --output_format=${format}
# 	pipenv run python -m scrapper.app.main --query issues

attachments: ## Get users from JIRA
	pipenv run python -m scrapper.app.main --query attachments

install: ## Run pipenv install
	pipenv install

