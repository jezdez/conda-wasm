# Browser Workflow Overview

This page is the older combined guide. The docs are now split by purpose:

- Start with {doc}`../tutorials/try-browser-demo` for a guided first run.
- Use {doc}`../how-to/use-conda-in-notebook` for notebook commands and runtime
  behavior.
- Use {doc}`../how-to/build-local-demo` to build the demo from source.
- Read {doc}`../reference/browser-runtime` for the runtime details.
- Read {doc}`../explanation/architecture` for the full execution model.

## Short Version

`conda-wasm` lets real conda run in the browser. It is not a JavaScript package
manager and it is not a separate package manager. The actual conda CLI runs in
Python compiled to WebAssembly, while conda-wasm supplies browser-specific
pieces that conda cannot get from native libraries in an Emscripten runtime:

- a Rust WASM solver path for conda's solver plugin API
- a Rust WASM package extractor for `.conda` and `.tar.bz2` archives
- sharded repodata prefetch and decode helpers
- runtime patches for MEMFS, synchronous browser fetches, subprocess behavior,
  and conda package-cache bookkeeping
- IPython magics that call `conda.cli.main` inside the kernel
- a JupyterLite extension and demo site

The browser stack looks like this:

```
Browser tab
  `-- JupyterLite (main thread)
      `-- JupyterLite extension (rewrites bare "conda" -> "%conda_wasm")
          `-- xeus-python kernel (WebWorker)
              `-- Python 3.13 (WASM/Emscripten)
                  |-- conda_wasm.runtime (shard prefetch at startup)
                  `-- conda (real conda, compiled to WASM)
                      `-- conda-wasm plugins (Rust -> WASM)
                          |-- solver: rattler/resolvo (replaces libsolv)
                          |-- repodata: CEP-16 sharded fetch (msgpack.zst)
                          `-- extractor: streaming .conda/.tar.bz2 -> MEMFS
```
