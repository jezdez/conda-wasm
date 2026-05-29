from __future__ import annotations

import logging
import os

log = logging.getLogger(__name__)


def is_shared_lib(filename: str) -> bool:
    """Return True for ``.so``, ``.so.1``, ``.so.1.10.0``, etc."""
    return "so" in filename.split(".")


def find_shared_libs(prefix: str) -> set[str]:
    """Return all shared library paths below *prefix*."""
    libs: set[str] = set()
    for dirpath, _, filenames in os.walk(prefix):
        for filename in filenames:
            if is_shared_lib(filename):
                libs.add(os.path.join(dirpath, filename))
    return libs


def load_shared_lib(path: str) -> None:
    """Load one WASM shared library into Emscripten's dynamic linker."""
    import ctypes  # noqa: PLC0415

    ctypes.CDLL(path, mode=ctypes.RTLD_GLOBAL)


def load_new_shared_libs(before: set[str], prefix: str) -> None:
    """Load shared libraries that appeared under *prefix* after a conda command."""
    after = find_shared_libs(prefix)
    new_libs = sorted(after - before, key=lambda path: path.count(os.sep))
    if not new_libs:
        return

    log.info("conda-wasm: %d new shared libraries to load", len(new_libs))
    failed: list[tuple[str, Exception]] = []

    for path in new_libs:
        try:
            load_shared_lib(path)
            log.debug("conda-wasm: loaded %s", path)
        except Exception as exc:  # noqa: BLE001
            failed.append((path, exc))

    still_failed: list[tuple[str, Exception]] = []
    for path, _ in failed:
        try:
            load_shared_lib(path)
            log.debug("conda-wasm: loaded %s (retry)", path)
        except Exception as exc:  # noqa: BLE001
            still_failed.append((path, exc))
            log.warning("conda-wasm: failed to load %s: %s", path, exc)

    loaded = len(new_libs) - len(still_failed)
    log.info("conda-wasm: loaded %d/%d shared libraries", loaded, len(new_libs))
