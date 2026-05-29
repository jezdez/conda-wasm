from __future__ import annotations

import logging

from . import state

log = logging.getLogger(__name__)

RUNTIME_JS = (
    "globalThis.condaWasmPrefetchCache = new Map();"
    "globalThis.condaWasmPrefetchHits = 0;"
    "globalThis.condaWasmSyncFetchBinary = fetchBin;"
    "globalThis.sync_fetch_binary = function(url) {"
    "  url = String(url);"
    "  var c = globalThis.condaWasmPrefetchCache.get(url);"
    "  if (c) {"
    "    globalThis.condaWasmPrefetchCache.delete(url);"
    "    globalThis.condaWasmPrefetchHits++;"
    "    return c;"
    "  }"
    "  return globalThis.condaWasmSyncFetchBinary(url);"
    "};"
    "globalThis.sync_fetch_text = fetchText;"
    "globalThis.condaWasmSolveRaw = condaWasm.conda_wasm_fetch_and_solve;"
    "globalThis.fetch_and_solve = function(request) {"
    "  globalThis.condaWasmPrefetchHits = 0;"
    "  var result = globalThis.condaWasmSolveRaw("
    "    String(request), globalThis.sync_fetch_binary, globalThis.sync_fetch_text);"
    "  console.warn('conda-wasm: solve used ' + globalThis.condaWasmPrefetchHits"
    "    + ' prefetch cache hits, ' + globalThis.condaWasmPrefetchCache.size + ' still cached');"
    "  return result;"
    "};"
    "globalThis.condaWasmExtractRaw = condaWasm.conda_wasm_extract_package;"
    "globalThis.conda_wasm_extract_package = function(bytes, filename, onFile) {"
    "  return globalThis.condaWasmExtractRaw(bytes, String(filename), onFile);"
    "};"
    "globalThis.condaWasmGetShardUrlsRaw = condaWasm.conda_wasm_get_shard_urls;"
    "globalThis.get_shard_urls = function(request) {"
    "  return globalThis.condaWasmGetShardUrlsRaw("
    "    String(request), globalThis.sync_fetch_binary);"
    "};"
    "globalThis.decode_shard_deps = function(data) {"
    "  return condaWasm.conda_wasm_decode_shard_deps(data);"
    "};"
    "globalThis.clear_repodata_cache = function() {"
    "  return condaWasm.conda_wasm_clear_repodata_cache();"
    "};"
    "globalThis.condaWasmPrefetchBatch = function(urlsOrJson) {"
    "  var urls = typeof urlsOrJson === 'string'"
    "    ? JSON.parse(urlsOrJson) : Array.from(urlsOrJson);"
    "  if (!urls || !urls.length) return Promise.resolve();"
    "  var n = urls.length, done = 0;"
    "  console.warn('conda-wasm: prefetching ' + n + ' shards');"
    "  return new Promise(function(resolve) {"
    "    for (var i = 0; i < n; i++) {"
    "      (function(url) {"
    "        fetch(url)"
    "        .then(function(r) { return r.arrayBuffer(); })"
    "        .then(function(buf) {"
    "          globalThis.condaWasmPrefetchCache.set(url, new Uint8Array(buf));"
    "        })"
    "        .catch(function(e) {"
    "          console.warn('conda-wasm: prefetch fail ' + url.slice(-50) + ': ' + e);"
    "        })"
    "        .finally(function() {"
    "          if (++done >= n) {"
    "            console.warn('conda-wasm: prefetch done, '"
    "              + globalThis.condaWasmPrefetchCache.size + ' cached');"
    "            resolve();"
    "          }"
    "        });"
    "      })(urls[i]);"
    "    }"
    "  });"
    "};"
)


def sync_fetch_binary(url: str):
    """Synchronous XHR to JS ``Uint8Array`` callback for Rust."""
    import js  # noqa: PLC0415

    xhr = js.XMLHttpRequest.new()
    xhr.open("GET", str(url), False)
    xhr.responseType = "arraybuffer"
    xhr.send()
    return js.Uint8Array.new(xhr.response)


def sync_fetch_text(url: str) -> str:
    """Synchronous XHR to Python ``str`` callback for Rust."""
    import js  # noqa: PLC0415

    xhr = js.XMLHttpRequest.new()
    xhr.open("GET", str(url), False)
    xhr.send()
    return str(xhr.responseText)


def register_runtime_globals(conda_wasm) -> None:
    """Register conda-wasm callbacks on JS ``globalThis``."""
    import js  # noqa: PLC0415
    import pyjs  # noqa: PLC0415

    js_fetch_binary, hnd1 = pyjs.create_callable(sync_fetch_binary)
    js_fetch_text, hnd2 = pyjs.create_callable(sync_fetch_text)
    state.runtime_refs.extend([js_fetch_binary, hnd1, js_fetch_text, hnd2])

    # Assign through native JS so global functions remain callable from JS.
    register_runtime = js.Function.new(
        "condaWasm",
        "fetchBin",
        "fetchText",
        RUNTIME_JS,
    )
    register_runtime(conda_wasm, js_fetch_binary, js_fetch_text)
    log.info("conda-wasm-runtime: js.fetch_and_solve registered")
