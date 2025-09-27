# ---------- config ----------
SHELL := /bin/sh
PY    ?= python3
VENV  ?= .venv

# передаются в ../tenge/benchmarks/run.sh
REPS        ?= 5
WARMUP      ?= 2
INNER_REPS  ?= 0
PROFILE     ?= strict

# каталоги
RESULTS_DIR := benchmarks
PLOTS_DIR   := plots
SCRIPTS_DIR := scripts
DOCS_DIR    := docs
DOCS_PLOTS  := $(DOCS_DIR)/plots

# ---------- helpers ----------
.PHONY: all bench plot publish clean purge venv

all: bench plot

venv:
	@mkdir -p $(VENV)
	@test -x "$(VENV)/bin/$(PY)" || (echo "[venv] create: $(VENV)"; python3 -m venv $(VENV))
	@. $(VENV)/bin/activate; $(PY) -m pip -q install --upgrade pip
	@. $(VENV)/bin/activate; $(PY) -m pip -q install -r requirements.txt

bench:
	@mkdir -p $(RESULTS_DIR) $(PLOTS_DIR) $(SCRIPTS_DIR)
	@echo "[bench] running in ../tenge"
	@REPS=$(REPS) WARMUP=$(WARMUP) INNER_REPS=$(INNER_REPS) PROFILE=$(PROFILE) \
		bash $(SCRIPTS_DIR)/run_bench.sh ../tenge $(RESULTS_DIR)
	@$(MAKE) plot

plot:
	@mkdir -p $(RESULTS_DIR) $(PLOTS_DIR) $(SCRIPTS_DIR)
	@echo "[plot] using results from $(abspath $(RESULTS_DIR))"
	@$(PY) $(SCRIPTS_DIR)/plot.py --results $(RESULTS_DIR) --out $(PLOTS_DIR)

publish:
	@mkdir -p $(DOCS_PLOTS)
	@# копируем графики
	@cp -f $(PLOTS_DIR)/*.png $(DOCS_PLOTS) 2>/dev/null || true
	@cp -f $(PLOTS_DIR)/*.svg $(DOCS_PLOTS) 2>/dev/null || true
	@# генерируем index.html
	@$(PY) $(SCRIPTS_DIR)/make_index.py \
		--plots $(DOCS_PLOTS) \
		--out $(DOCS_DIR)/index.html \
		--title "Tenge Showcase Benchmarks" \
		--subtitle "Profile=$(PROFILE), REPS=$(REPS), WARMUP=$(WARMUP), INNER_REPS=$(INNER_REPS)" \
		--repo "https://github.com/DauletBai/tenge" \
		--showcase "https://github.com/DauletBai/tenge-showcase"
	@echo "[publish] ready: $(DOCS_DIR)/index.html"
	@echo "Enable GitHub Pages -> Source: 'main' / folder: '/docs'"

clean:
	@rm -rf $(PLOTS_DIR)

purge: clean
	@rm -rf $(RESULTS_DIR) $(DOCS_DIR)

# abspath helper for macOS GNU make compatibility
abspath = $(shell python3 -c 'import os,sys;print(os.path.abspath(sys.argv[1]))' $(1))