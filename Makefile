


# We assume naming of `<type>.<ext>`: where `type` is `app` or `report`
PY_REPORT = report.py
IPYNB_REPORT = report.ipynb
PY_APP = app.py
IPYNB_APP = app.ipynb

PY_APPS := $(dir $(wildcard apps/*/app.py))
IPYNB_APPS := $(dir $(wildcard apps/*/app.ipynb))
PY_REPORTS := $(dir $(wildcard reports/*/report.py))
IPYNB_REPORTS := $(dir $(wildcard reports/*/report.ipynb))

# Target names support with and without a trailing slash
# This is for a better experience for autocomplete;
# where some leave the slash, and others don't
define striptailslash
	$(patsubst %/,%,$(1))
endef
PY_APPS_TARGETS := $(PY_APPS) $(call striptailslash,$(PY_APPS))
IPYNB_APPS_TARGETS := $(IPYNB_APPS) $(call striptailslash,$(IPYNB_APPS))
PY_REPORTS_TARGETS := $(PY_REPORTS) $(call striptailslash,$(PY_REPORTS))
IPYNB_REPORTS_TARGETS := $(IPYNB_REPORTS) $(call striptailslash,$(IPYNB_REPORTS))

REPORTS := $(PY_REPORTS) $(IPYNB_REPORTS)
APPS := $(PY_APPS) $(IPYNB_APPS)

.PHONY: debug
debug:
	@echo "REPORTS: $(REPORTS)"
	@echo "PY_REPORTS: $(PY_REPORTS_TARGETS)"
	@echo "IPYNB_REPORTS: $(IPYNB_REPORTS_TARGETS)"
	@echo ""
	@echo "APPS: $(APPS)"
	@echo "PY_APPS: $(PY_APPS_TARGETS)"
	@echo "IPYNB_APPS: $(IPYNB_APPS_TARGETS)"

disable-analytics:
	touch ~/.config/datapane/no_analytics

login:
ifndef DATAPANE_TOKEN
	$(error "DATAPANE_TOKEN is not set")
endif
	datapane login --token "$${DATAPANE_TOKEN}"

install:
	python -m pip install requirements.txt


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

.PHONY: $(PY_APPS_TARGETS)
$(PY_APPS_TARGETS):
	@echo "Building $@"
	# TODO

.PHONY: $(IPYNB_APPS_TARGETS)
$(IPYNB_APPS_TARGETS):
	@echo "Building $@"
	# TODO

.PHONY: reports
reports: $(REPORTS)

.PHONY: apps
apps: $(APPS)
