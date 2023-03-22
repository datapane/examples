#!/usr/bin/env python

import json
from operator import xor
from pathlib import Path
import sys
import sh
from contextlib import contextmanager, nullcontext
import shutil

CI_DIR = Path(__file__).parent
WORKSPACE_DIR = CI_DIR.parent
REQUIREMENTS_TXT = WORKSPACE_DIR / "requirements.txt"

# fly expects these as relative paths, not asolutes
# Error failed to fetch an image or build from source: Dockerfile '~/work/datapane/examples/apps/startup-calculator/~/work/datapane/examples/ci/py.Dockerfile' not found
PY_DOCKERFILE = "../../ci/py.Dockerfile"
NB_DOCKERFILE = "../../ci/nb.Dockerfile"

# Used for defining services only
FLY_BASE_CONFIG = "../../ci/fly.toml"

# app names are globally unique, so mix in a quick nonce.
# determined with a D16.
_STATIC_NONCE = "1164c73e"

# determine with `fly orgs list`
_FLY_ORG_SLUG = "leo-anthias"


EXCLUDED_APPS = [
    #    "stock-reporting",  # Error on boot
]
APP_DIRS = sorted([d for d in (WORKSPACE_DIR / "apps").iterdir() if d.is_dir() and d.name not in EXCLUDED_APPS])


@contextmanager
def _tmp_cpy(from_: Path, to_: Path):
    """Copy a file, then delete it when done."""
    try:
        shutil.copyfile(from_, to_)
        yield
    finally:
        try:
            to_.unlink()
        except FileNotFoundError:
            pass  # not sure why we get a file not found


@contextmanager
def sym_to_copy(p: Path):
    """Temporarily turns a symlink into a real file

    useful for tooling that copies the link instead of the content, such as docker.
    """
    assert p.exists()
    assert p.is_symlink()

    # readlink() can be relative to the file: we need to restore this
    # resolve() is absolute
    original_link = p.readlink()
    original = p.resolve(strict=True)

    try:
        p.unlink()
        with _tmp_cpy(original, p):
            yield
    finally:
        p.symlink_to(original_link)


@contextmanager
def requirement_files(app_dir: Path):
    """Manage the lifecycle of requirements files during a deploy

    Usually we want to just copy the base requirements, but sometimes Apps have their own deps
    """
    base = app_dir / "requirements-base.txt"
    if base.exists() and base.is_symlink():
        base_cm = sym_to_copy(base)
    else:
        base_cm = nullcontext()

    requirements = app_dir / "requirements.txt"
    if not requirements.exists():
        requirements_cm = _tmp_cpy(REQUIREMENTS_TXT, requirements)
    else:
        requirements_cm = nullcontext()

    with base_cm:
        with requirements_cm:
            yield


def is_py_app(app_dir: Path):
    return (app_dir / "app.py").exists()


def is_nb_app(app_dir: Path):
    return (app_dir / "app.ipynb").exists()


def is_valid_app(app_dir: Path):
    return xor(is_nb_app(app_dir), is_py_app(app_dir))


def get_dockerfile(app_dir: Path):
    if is_nb_app(app_dir):
        return NB_DOCKERFILE
    else:
        return PY_DOCKERFILE


def _fly_app_name(app_dir: Path):
    return f"dp-examples-{_STATIC_NONCE}-{app_dir.stem}"


def _fly_app_exists(app_dir: Path):
    app_name = _fly_app_name(app_dir)
    app_list_raw = sh.flyctl.apps.list("-j")
    app_list = json.loads(app_list_raw)
    app_names = [a["Name"] for a in app_list]
    return app_name in app_names


def _fly_create_app(app_dir: Path):
    app_name = _fly_app_name(app_dir)
    sh.flyctl.apps.create(
        name=app_name,
        org=_FLY_ORG_SLUG,
        _fg=True,
    )


def _fly_deploy(app_dir: Path):
    app_name = _fly_app_name(app_dir)

    # If encountering OOM errors, increase the Apps memory with this command: (512 == 512mb)
    # flyctl scale meemory -a '{app_name}' 512

    with requirement_files(app_dir):
        sh.flyctl.deploy(
            app_dir,  # build context
            app=app_name,
            env="PORT=8080",
            remote_only=True,
            now=True,
            force_nomad=True,  # doesn't stick when set during app creating. Using v1 until v2 is fully GA.
            region="lhr",
            dockerfile=get_dockerfile(app_dir),
            # config must be specified so that services are joisted
            config=FLY_BASE_CONFIG,
            _fg=True,
        )


def main():
    app_dirs = APP_DIRS
    try:
        app_name = sys.argv[1]
    except IndexError:
        pass
    else:
        app_name = app_name.removeprefix("apps/")
        app_dirs = [d for d in app_dirs if d.name == app_name]

    invalid_apps = [d for d in app_dirs if not is_valid_app(d)]
    if invalid_apps:
        raise RuntimeError(f"Invalid apps found!: {invalid_apps}")

    for app_dir in app_dirs:
        print(f"deploying {app_dir=}")
        if not _fly_app_exists(app_dir):
            _fly_create_app(app_dir)
        _fly_deploy(app_dir)


if __name__ == "__main__":
    main()
