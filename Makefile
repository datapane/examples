disable-analytics:
	mkdir -p ~/.config/datapane
	touch ~/.config/datapane/no_analytics

login:
ifndef DATAPANE_TOKEN
	$(error "DATAPANE_TOKEN is not set")
endif
	datapane login --token "$${DATAPANE_TOKEN}"

install:
	python -m pip install -r requirements.txt

.PHONY: deploy-reports
deploy-reports:
	python ci/deploy-reports.py

.PHONY: deploy-apps
deploy-apps:
	python ci/deploy-apps.py
