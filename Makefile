
define striptrailingslash
	$(patsubst %/,%,$(1))
endef

# We assume naming of `<type>.<ext>`: where `type` is `app` or `report`
PY_REPORT = report.py
IPYNB_REPORT = report.ipynb
PY_APP = app.py
IPYNB_APP = app.ipynb

PY_APPS := $(call striptrailingslash,$(dir $(wildcard apps/*/app.py)))
IPYNB_APPS := $(call striptrailingslash,$(dir $(wildcard apps/*/app.ipynb)))
APPS := $(PY_APPS) $(IPYNB_APPS)

PY_REPORTS := $(call striptrailingslash,$(dir $(wildcard reports/*/report.py)))
IPYNB_REPORTS := $(call striptrailingslash,$(dir $(wildcard reports/*/report.ipynb)))
REPORTS := $(PY_REPORTS) $(IPYNB_REPORTS)

.PHONY: debug
debug:
	@echo "REPORTS: $(REPORTS)"
	@echo "PY_REPORTS: $(PY_REPORTS)"
	@echo "IPYNB_REPORTS: $(IPYNB_REPORTS)"
	@echo ""
	@echo "APPS: $(APPS)"
	@echo "PY_APPS: $(PY_APPS)"
	@echo "IPYNB_APPS: $(IPYNB_APPS)"

disable-analytics:
	touch ~/.config/datapane/no_analytics

login:
ifndef DATAPANE_TOKEN
	$(error "DATAPANE_TOKEN is not set")
endif
	datapane login --token "$${DATAPANE_TOKEN}"

install:
	python -m pip install requirements.txt


.PHONY: $(PY_REPORTS) $(addsuffix /,$(PY_REPORTS))
$(PY_REPORTS) $(addsuffix /,$(PY_REPORTS)):
	@echo "Building $@"
	cd $@; \
		BROWSER=true DATAPANE_DEPLOY=1 python "$(PY_REPORT)"

.PHONY: $(IPYNB_REPORTS) $(addsuffix /,$(IPYNB_REPORTS))
$(IPYNB_REPORTS) $(addsuffix /,$(IPYNB_REPORTS)):
	@echo "Building $@"
	cd $@; \
		BROWSER=true DATAPANE_DEPLOY=1 datapane app generate script-from-nb \
			--nb "$(IPYNB_REPORT)" \
			--out - \
		| python -

.PHONY: $(PY_APPS) $(addsuffix /,$(PY_APPS))
$(PY_APPS) $(addsuffix /,$(PY_APPS))):
	@echo "Building $@"
	# TODO

.PHONY: $(IPYNB_APPS) $(addsuffix /,$(IPYNB_APPS))
$(IPYNB_APPS) $(addsuffix /,$(IPYNB_APPS))):
	@echo "Building $@"
	# TODO

.PHONY: reports
reports: $(REPORTS)

.PHONY: apps
apps: $(APPS)
