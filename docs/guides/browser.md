# Browser Workflow Overview

This page is the older combined guide. The docs are now split by purpose:

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} First run
:link: ../tutorials/try-browser-demo
:link-type: doc
:class-card: sd-shadow-sm sd-card-hover
Guided walkthrough of the live browser demo.
:::

:::{grid-item-card} Notebook commands
:link: ../how-to/use-conda-in-notebook
:link-type: doc
:class-card: sd-shadow-sm sd-card-hover
Practical `%conda` usage and runtime behavior.
:::

:::{grid-item-card} Local build
:link: ../how-to/build-local-demo
:link-type: doc
:class-card: sd-shadow-sm sd-card-hover
Build the demo from this checkout.
:::

:::{grid-item-card} Architecture
:link: ../explanation/architecture
:link-type: doc
:class-card: sd-shadow-sm sd-card-hover
Execution model and component boundaries.
:::
::::

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
