.PHONY: FORCE
FORCE:


# We assume naming of `<type>.<ext>`: where `type` is `app` or `report`
PY_REPORT = report.py
IPYNB_REPORT = report.ipynb

PY_REPORTS := $(dir $(wildcard reports/*/report.py))
IPYNB_REPORTS := $(dir $(wildcard reports/*/report.ipynb))

# Target names support with and without a trailing slash
# This is for a better experience for autocomplete;
# where some leave the slash, and others don't
define striptailslash
	$(patsubst %/,%,$(1))
endef
PY_REPORTS_TARGETS := $(PY_REPORTS) $(call striptailslash,$(PY_REPORTS))
IPYNB_REPORTS_TARGETS := $(IPYNB_REPORTS) $(call striptailslash,$(IPYNB_REPORTS))

REPORTS := $(PY_REPORTS) $(IPYNB_REPORTS)

.PHONY: debug
debug:
	@echo "REPORTS: $(REPORTS)"
	@echo "PY_REPORTS: $(PY_REPORTS_TARGETS)"
	@echo "IPYNB_REPORTS: $(IPYNB_REPORTS_TARGETS)"

disable-analytics:
	touch ~/.config/datapane/no_analytics

login:
ifndef DATAPANE_TOKEN
	$(error "DATAPANE_TOKEN is not set")
endif
	datapane login --token "$${DATAPANE_TOKEN}"

install:
	python -m pip install requirements.txt

# Static artifacts for bundling Apps
ci/nb.Dockerfile:
	@echo "Building $@"
	rm "$@"
	datapane app generate dockerfile --app-file "$(IPYNB_APP)" -o "$@"

ci/py.Dockerfile:
	@echo "Building $@"
	rm "$@"
	datapane app generate dockerfile --app-file "$(PY_APP)" -o "$@"

.PHONY: dockerfiles ci/nb.Dockerfile ci/py.Dockerfile
dockerfiles: ci/nb.Dockerfile ci/py.Dockerfile

.PHONY: $(PY_REPORTS_TARGETS)
$(PY_REPORTS_TARGETS):
	@echo "Building $@"
	cd $@; \
		BROWSER=true DATAPANE_DEPLOY=1 python "$(PY_REPORT)"

.PHONY: $(IPYNB_REPORTS_TARGETS)
$(IPYNB_REPORTS_TARGETS):
	@echo "Building $@"
	cd $@; \
		BROWSER=true DATAPANE_DEPLOY=1 datapane app generate script-from-nb \
			--nb "$(IPYNB_REPORT)" \
			--out - \
		| python -

.PHONY: deploy-reports
deploy-reports: $(REPORTS)

.PHONY: deploy-apps
deploy-apps:
	python ci/deploy-apps.py
