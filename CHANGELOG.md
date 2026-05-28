# Changelog

## Split from conda-express (2026-05-28)

`conda-wasm` was split out of `jezdez/conda-express` to own the browser,
WebAssembly, Emscripten, and JupyterLite parts of the project.

Moved project areas:

- `crates/cx-wasm`: WebAssembly build of the rattler solver, extractor, and
  sharded repodata helpers.
- `conda-emscripten`: conda plugin for Emscripten environments, including the
  `CxWasmSolver`, WASM extraction, IPython magics, and MEMFS-oriented runtime
  patches.
- `cx-jupyterlite`: JupyterLite extension that routes conda commands through
  the browser kernel.
- `recipes/cx-wasm-kernel`: WASM bridge package and startup shard prefetch.
- `lite`: static JupyterLite demo site and notebooks.
- `recipes/conda-emscripten`: Emscripten conda recipe and patches.

## Historical conda-express changes

These entries were originally recorded in the `conda-express` changelog before
the browser stack moved into this repository.

### 0.6.0 (2026-05-06)

- Fixed `getrandom` 0.3 usage in `cx-wasm` to match `ahash`'s transitive
  dependency.
- Fixed the JupyterLite `yarn.lock` TypeScript compatibility patch hash.
- Bumped npm dependencies in `cx-jupyterlite`: `lodash`, `postcss`,
  `brace-expansion`, and `yaml`.

### 0.4.0 (2026-03-31)

- Added `cx-wasm`, a WebAssembly build of the rattler solver and package
  extractor for use in the browser.
- Added `conda-emscripten`, a conda plugin for Emscripten with `CxWasmSolver`,
  WASM extraction, `%cx` / `%conda` IPython magics, MEMFS-oriented patches,
  and shared-library loading for C extensions after install.
- Added `cx-jupyterlite`, a JupyterLite federated extension that rewrites bare
  `conda` cell commands so the kernel magics handle them.
- Added `cx-wasm-kernel`, a conda recipe packaging WASM artifacts and the
  `cx_wasm_bridge` shard prefetch bridge for xeus-python.
- Added the JupyterLite demo site under `lite/`.
- Added async shard prefetch: parallel `fetch()` at startup plus sync solve,
  improving solve time when using sharded repodata.
- Fixed cross-channel transitive dependency resolution, pyjs coercion, repodata
  URL derivation, session-level shard caching, and related install-path issues
  in `cx-wasm` / `conda-emscripten`.
- Updated demo notebooks with WASM-friendly examples and runtime
  `conda install` examples.
