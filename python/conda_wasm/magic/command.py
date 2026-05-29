from __future__ import annotations

import sys
import time

from conda_wasm.diagnostics import emit_timing

from .prefix import bootstrap_prefix
from .shared_libs import find_shared_libs, load_new_shared_libs

HELP = """\
%conda / %conda_wasm - real conda in the browser (accelerated by conda-wasm)

Calls conda.cli directly - all conda subcommands are supported:

  %conda install <pkg> [pkg2 ...]        Install packages
  %conda remove  <pkg> [pkg2 ...]        Remove packages
  %conda list                            List installed packages
  %conda search  <query>                 Search available packages
  %conda info                            Show conda info
  %conda env list                        List environments

Examples:
  %conda install zlib
  %conda install numpy scipy matplotlib
  %conda list
"""

MUTATING_COMMANDS = {"install", "update", "upgrade", "remove", "uninstall", "create"}

patches_applied = False
cached_conda_main = None


def run_conda_magic(line: str) -> None:
    """Run one ``%conda`` or ``%conda_wasm`` magic command."""
    if not (line := line.strip()) or line in ("-h", "--help", "help"):
        print(HELP)
        return

    command, *args = line.split()
    if command in MUTATING_COMMANDS and "--yes" not in args and "-y" not in args:
        args = ["--yes", *args]

    if not ensure_runtime_ready():
        return

    total_start = time.perf_counter()
    apply_runtime_patches()
    conda_main = get_conda_main()
    if conda_main is None:
        return

    is_mutating = command in MUTATING_COMMANDS
    prefix = sys.prefix

    scan_start = time.perf_counter()
    before_libs = find_shared_libs(prefix) if is_mutating else None
    if is_mutating:
        emit_timing("lib-scan:", time.perf_counter() - scan_start)

    conda_start = time.perf_counter()
    conda_main(command, *args)
    emit_timing("conda:", time.perf_counter() - conda_start)

    if before_libs is not None:
        load_start = time.perf_counter()
        load_new_shared_libs(before_libs, prefix)
        emit_timing("shared-libs:", time.perf_counter() - load_start)

    emit_timing("total:", time.perf_counter() - total_start)


def ensure_runtime_ready() -> bool:
    """Return True when the async runtime is ready enough to run conda."""
    try:
        import conda_wasm.runtime as runtime
    except ImportError:
        return True

    if not runtime.is_ready():
        print("conda-wasm is still loading - please run the cell again in a moment")
        return False

    return True


def apply_runtime_patches() -> None:
    """Bootstrap the prefix and apply browser compatibility patches once."""
    global patches_applied
    if patches_applied:
        return

    start = time.perf_counter()
    bootstrap_prefix()

    from conda_wasm.plugin.patches import patch_conda_internals, patch_urllib3

    patch_urllib3()
    patch_conda_internals()
    patches_applied = True
    emit_timing("patches:", time.perf_counter() - start)


def get_conda_main():
    """Return cached ``conda.cli.main.main`` if conda is available."""
    global cached_conda_main
    if cached_conda_main is not None:
        return cached_conda_main

    try:
        from conda.cli.main import main
    except ImportError:
        print(
            "conda is not installed in this kernel.\n"
            "Rebuild with: pixi run -e demo demo-build-local"
        )
        return None

    cached_conda_main = main
    return cached_conda_main
