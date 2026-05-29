from __future__ import annotations

import asyncio
from typing import Any

conda_wasm_module: Any | None = None
setup_done = False

# Must survive for the entire session: pyjs invalidates the JS-side proxy when
# the Python handle is garbage collected.
runtime_refs: list[Any] = []

locks: dict[str, asyncio.Lock] = {}


def get_lock(name: str) -> asyncio.Lock:
    """Return a named asyncio lock, creating it on first access."""
    if name not in locks:
        locks[name] = asyncio.Lock()
    return locks[name]
