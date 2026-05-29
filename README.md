# conda-wasm

Browser and WebAssembly tooling for conda.

This repository owns the browser-specific conda stack: WebAssembly solver and
extraction support, Emscripten conda integration, the Python browser runtime,
JupyterLite integration, demo notebooks, and recipes for packaging that stack.

It is intentionally separate from the native bootstrap projects:

- [`pronto`](https://github.com/jezdez/pronto) builds generic native conda
  bootstrap binaries.
- [`conda-express`](https://github.com/jezdez/conda-express) publishes the
  opinionated `cx` and `cxz` native distribution built with Pronto.
- `conda-wasm` is for conda in the browser: Emscripten, WebAssembly,
  JupyterLite, MEMFS, and browser package handling.

Repository areas:

- `crates/conda-wasm`: Rust/WASM solver and package extraction support
- `python`: Python runtime package, conda plugin, IPython magic package, and
  WASM loader assets
- `jupyterlite`: JupyterLite integration
- `demo`: demo site
- `recipes/conda`: patched conda recipe for Emscripten
- `recipes/conda-wasm`: Python package recipe

Documentation is organized by goal:

- Tutorial: try conda in the live browser demo
- How-to guides: use notebook magics and build the local demo
- Reference: repository layout, Python runtime package layout, browser runtime,
  and conda plugin behavior
- Explanation: architecture and project boundaries with Pronto and
  conda-express

Historical browser/WASM release notes now live in [CHANGELOG.md](CHANGELOG.md).
