"""conda-wasm browser runtime public API."""

from __future__ import annotations

import asyncio
import logging
import sys

from . import state
from .globals import register_runtime_globals
from .loader import load_conda_wasm
from .prefetch import prefetch_installed

log = logging.getLogger(__name__)

__all__ = ["is_ready", "prefetch_installed", "setup"]


def is_ready() -> bool:
    """Return True if runtime setup has completed."""
    return state.setup_done


async def setup() -> None:
    """Load conda-wasm and register runtime functions on the JS global scope."""
    if state.setup_done:
        return

    async with state.get_lock("setup"):
        if state.setup_done:
            return

        conda_wasm = await load_conda_wasm()
        register_runtime_globals(conda_wasm)
        state.setup_done = True

        await prefetch_installed()


async def setup_background() -> None:
    """Run setup from an import-time background task without surfacing pyjs errors."""
    try:
        await setup()
    except Exception as exc:  # noqa: BLE001
        log.warning("conda-wasm-runtime: background setup failed: %s", exc)


def schedule_auto_setup() -> None:
    """Schedule setup as a background task when running under Emscripten."""
    if sys.platform != "emscripten":
        return
    try:
        asyncio.ensure_future(setup_background())
    except RuntimeError:
        pass


schedule_auto_setup()
