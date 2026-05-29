# Changelog

## Repository split (2026-05-28)

`conda-wasm` now owns the browser, WebAssembly, Emscripten, and JupyterLite
parts of the project.

Moved project areas:

- `crates/conda-wasm`: WebAssembly build of the rattler solver, extractor, and
  sharded repodata helpers.
- `python`: Python runtime and conda plugin for Emscripten environments,
  including the `CondaWasmSolver`, WASM extraction, IPython magics, startup
  shard prefetch, and MEMFS-oriented runtime patches.
- `jupyterlite`: JupyterLite extension that routes conda commands through
  the browser kernel.
- `demo`: static JupyterLite demo site and notebooks.
- `recipes/conda`: patched conda recipe for Emscripten.
- `recipes/conda-wasm`: conda-wasm Python runtime and plugin recipe.

## Historical browser/WASM changes

These entries were recorded before the browser stack moved into this repository.

### 0.6.0 (2026-05-06)

- Fixed `getrandom` 0.3 usage in `conda-wasm` to match `ahash`'s transitive
  dependency.
- Fixed the JupyterLite `yarn.lock` TypeScript compatibility patch hash.
- Bumped npm dependencies in the JupyterLite extension: `lodash`, `postcss`,
  `brace-expansion`, and `yaml`.

### 0.4.0 (2026-03-31)

- Added `conda-wasm`, a WebAssembly build of the rattler solver and package
  extractor for use in the browser.
- Added the conda-wasm Python package for Emscripten with `CondaWasmSolver`,
  WASM extraction, `%conda_wasm` / `%conda` IPython magics, MEMFS-oriented patches,
  startup shard prefetch, and shared-library loading for C extensions after install.
- Added a JupyterLite federated extension that rewrites bare
  `conda` cell commands so the kernel magics handle them.
- Added runtime packaging for WASM artifacts and the `conda_wasm.runtime` shard
  prefetch runtime for xeus-python.
- Added the JupyterLite demo site.
- Added async shard prefetch: parallel `fetch()` at startup plus sync solve,
  improving solve time when using sharded repodata.
- Fixed cross-channel transitive dependency resolution, pyjs coercion, repodata
  URL derivation, session-level shard caching, and related install-path issues
  in `conda-wasm`.
- Updated demo notebooks with WASM-friendly examples and runtime
  `conda install` examples.
