from __future__ import annotations

import logging

from .assets import runtime_asset_paths
from . import state

log = logging.getLogger(__name__)

LOAD_MODULE_JS = (
    "var jsUrl = URL.createObjectURL("
    "  new Blob([String(jsText)], {type: 'text/javascript'}));"
    "var wasmUrl = URL.createObjectURL("
    "  new Blob([wasmData], {type: 'application/wasm'}));"
    "return import(jsUrl).then(function(m) {"
    "  return m.default(wasmUrl).then(function() {"
    "    URL.revokeObjectURL(jsUrl);"
    "    URL.revokeObjectURL(wasmUrl);"
    "    return m;"
    "  });"
    "});"
)


async def load_conda_wasm():
    """Load and cache the conda-wasm ES module from packaged assets."""
    if state.conda_wasm_module is not None:
        return state.conda_wasm_module

    async with state.get_lock("load"):
        if state.conda_wasm_module is not None:
            return state.conda_wasm_module

        import js  # noqa: PLC0415
        import pyjs  # noqa: PLC0415

        js_path, wasm_path = runtime_asset_paths()
        log.info("conda-wasm-runtime: loading WASM (%d bytes)", wasm_path.stat().st_size)

        wasm_data = pyjs.to_js(wasm_path.read_bytes())
        js_text = js_path.read_text(encoding="utf-8")

        # Keep Blob creation, dynamic import, and wasm-bindgen init in native JS:
        # pyjs string/array proxies fail wasm-bindgen's strict type checks here.
        load_module = js.Function.new("jsText", "wasmData", LOAD_MODULE_JS)
        state.conda_wasm_module = await load_module(js_text, wasm_data)
        log.info("conda-wasm-runtime: WASM module loaded")
        return state.conda_wasm_module
