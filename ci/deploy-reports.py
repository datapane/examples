#!/usr/bin/env python

from contextlib import contextmanager
from glob import glob
from operator import xor
import os
from pathlib import Path
import sys
import sh


CI_DIR = Path(__file__).parent
WORKSPACE_DIR = CI_DIR.parent
EXCLUDED_REPORTS = [
    "sales-report", # hangs on `plot4.show()`
    "sqlite-dashboard",  # hangs on `employee_sales_monthly.show()`
    "stock-reporting",  # hangs on `fig0.show()`
    "superstore-reporting",  # hangs on `fig0.show()`
    "text-heavy-report",  # reports currently only deploy with shared requirements
]
REPORT_DIRS = sorted([
    d
    for d in (WORKSPACE_DIR / "reports").iterdir()
    if d.is_dir()
    and d.name not in EXCLUDED_REPORTS
])

_run_py = sh.python.bake()
_run_py_traced = sh.python.bake(
    "-m", "trace", "-t", "-g",
    # We only care about tracing our code
    # Exclude python + dependencies
    ignore_dir=os.pathsep.join(sys.path)
)

TRACE = os.environ.get("DP_REPORT_TRACE", "0").lower() in ("1", "true")
if TRACE:
    run_py = _run_py_traced
else:
    run_py = _run_py


_log_context = ""
def log(*args, **kwargs):
    prefix = f"report({_log_context}):" if _log_context else ""
    print(prefix, *args, **kwargs)


def is_py_report(report_dir: Path):
    return (report_dir / "report.py").is_file()


def is_nb_report(report_dir: Path):
    return (report_dir / "report.ipynb").is_file()


def is_valid_report(report_dir: Path):
    return xor(is_py_report(report_dir), is_nb_report(report_dir))


def run_py_report(report_dir: Path, script_name: str = "report.py"):
    log("Running")

    # Always execute from their directory, so that assets can be loaded
    with sh.pushd(report_dir):
        run_py(script_name, _fg=True, _env={
            # alias to the 'true' command, so that browsers don't open
            "BROWSER": "true",
            # flag so reports can alter behaviour between dev + deploy
            "DATAPANE_DEPLOY": "1",
        })


@contextmanager
def nb_to_py_report(report_dir: Path, script_name: str = "report.py"):
    """Generate the 'report.py' script from the 'report.ipynb' notebook.

    'report.py' will be placed in `report_dir`, and deleted after closing the context
    """
    script_path = report_dir / script_name
    nb_path = report_dir / "report.ipynb"
    assert nb_path.is_file()
    assert not script_path.exists()

    log("Converting to script")

    try:
        sh.datapane.app.generate(
            "script-from-nb",
            nb=nb_path.resolve(),
            out=script_path.resolve(),
            _fg=True,
        )
        yield
    finally:
        script_path.unlink()


def run_nb_report(report_dir: Path):
    # improves the output of traces by tagging the filename with the report name
    script_name = f"{report_dir.name}-report.py"
    with nb_to_py_report(report_dir, script_name=script_name):
        run_py_report(report_dir, script_name=script_name)


def run_report(report_dir: Path):
    log("Starting")
    if is_nb_report(report_dir):
        run_nb_report(report_dir)
    else:
        run_py_report(report_dir)


def main():
    global _log_context
    dirs = REPORT_DIRS

    try:
        name = sys.argv[1]
    except IndexError:
        pass
    else:
        name = name.removeprefix('reports/')
        dirs = [d for d in dirs if d.name == name]

    for dir in dirs:
        _log_context = dir.name
        run_report(dir)


if __name__ == "__main__":
    main()
