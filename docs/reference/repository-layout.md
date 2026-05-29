# Repository Layout

This repository contains all browser and WebAssembly-specific conda work.

| Path | Purpose |
|---|---|
| `crates/conda-wasm/` | Rust crate compiled to WebAssembly |
| `python/conda_wasm/` | Python runtime package and conda plugin |
| `jupyterlite/` | JupyterLite frontend extension |
| `demo/` | Static JupyterLite site and notebooks |
| `recipes/conda/` | Patched conda recipe for Emscripten |
| `recipes/conda-wasm/` | Recipe for the Python runtime package and WASM assets |
| `docs/` | Sphinx documentation |

## Rust Crate

`crates/conda-wasm/` is the Rust/WebAssembly implementation.

| File | Role |
|---|---|
| `src/lib.rs` | WASM exports and top-level module wiring |
| `src/solve.rs` | Solver request handling and resolvo integration |
| `src/extract.rs` | Streaming extraction for `.conda` and `.tar.bz2` packages |
| `src/sharded.rs` | Sharded repodata URL and dependency helpers |
| `src/gateway.rs` | Fetch/decode plumbing shared by browser entry points |
| `src/bootstrap.rs` | Bootstrap helpers |
| `src/error.rs` | Error types and conversions |

Generated `wasm-pack` output goes under `crates/conda-wasm/pkg/`.

## Python Runtime Package

`python/conda_wasm/` is installed as the `conda-wasm` Python distribution.

| Path | Role |
|---|---|
| `runtime/` | Browser runtime loader, JS global registration, shard prefetch, and runtime state |
| `magic/` | IPython magic registration, `%conda` command dispatch, prefix bootstrap, shared-library loading |
| `plugin/` | Conda plugin hooks, solver backend, extractor, and compatibility patch facade |
| `plugin/compat/` | Focused Emscripten compatibility patches for conda internals |
| `diagnostics.py` | Shared opt-in timing diagnostics |
| `runtime_assets/` | Packaged `conda_wasm.js` and `conda_wasm_bg.wasm` copied during recipe builds |

`conda_wasm.runtime`, `conda_wasm.magic`, and `conda_wasm.plugin.patches` are
the stable import surfaces for users and integrations.

## JupyterLite Extension

`jupyterlite/` contains the frontend extension used by the demo site. Source
TypeScript lives in `jupyterlite/src/`. Built `lib/` and `labextension/` output
is generated.

## Demo Site

`demo/` contains the JupyterLite site configuration, notebooks, empack config,
and build script. The demo can use public Emscripten packages or locally built
packages from this checkout's `output/` channel.

## Recipes

`recipes/conda/` builds a conda package patched for Emscripten constraints such
as MEMFS, missing subprocess support, and browser platform behavior.

`recipes/conda-wasm/` builds the Python package and includes the generated WASM
assets from the Rust crate.
