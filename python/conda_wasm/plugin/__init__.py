from __future__ import annotations

import sys

try:
    from conda import plugins
    from conda.base.context import context
    from conda.plugins.types import CondaPreCommand, CondaSolver, CondaVirtualPackage
except ImportError:
    plugins = None
    context = None
    CondaPreCommand = CondaSolver = CondaVirtualPackage = None

pre_command_init_done = False


def hookimpl(function):
    """Apply conda's hook decorator when conda is importable."""
    if plugins is None:
        return function
    return plugins.hookimpl(function)


def on_pre_command(command: str) -> None:
    global pre_command_init_done

    del command

    if sys.platform != "emscripten" or pre_command_init_done:
        return

    from .patches import patch_conda_internals, patch_urllib3

    patch_urllib3()
    patch_conda_internals()

    pre_command_init_done = True


def emscripten_version() -> str | None:
    info = getattr(sys, "_emscripten_info", None)
    if info is None:
        return None
    major, minor, tiny = info.emscripten_version
    return f"{major}.{minor}.{tiny}"


@hookimpl
def conda_solvers():
    if CondaSolver is None:
        return

    from .solver import CondaWasmSolver

    yield CondaSolver(name="conda-wasm", backend=CondaWasmSolver)


@hookimpl
def conda_package_extractors():
    if plugins is None:
        return

    if sys.platform == "emscripten":
        from .extractor import extract_wasm

        yield plugins.types.CondaPackageExtractor(
            name="wasm-extractor",
            extensions=[".tar.bz2", ".conda"],
            extract=extract_wasm,
        )


@hookimpl
def conda_pre_commands():
    if CondaPreCommand is None:
        return

    yield CondaPreCommand(
        name="conda-wasm-runtime-preload",
        action=on_pre_command,
        run_for={"install", "update", "create", "remove"},
    )


@hookimpl
def conda_virtual_packages():
    if context is None or CondaVirtualPackage is None:
        return

    if not context.subdir.startswith("emscripten-"):
        return
    yield CondaVirtualPackage(name="unix", version=None, build=None)
    yield CondaVirtualPackage(
        name="emscripten", version=emscripten_version(), build=None
    )
