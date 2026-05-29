# Build the Local Demo

Use this guide to build the WebAssembly module, package the Python runtime, and
serve the JupyterLite demo from this checkout.

## Prerequisites

Install `pixi`. The repository tasks provide the Rust, Python, JupyterLite, and
recipe tooling through pixi environments.

Install `wasm-pack` if it is not already available:

```bash
pixi run cargo install wasm-pack
```

## Build the WASM Module

Build the Rust crate for web use:

```bash
pixi run -e web wasm-build
```

This writes generated artifacts under `crates/conda-wasm/pkg/`. Those files are
generated build output; do not edit them by hand.

## Build the Recipes and Lockfile

Build the patched conda recipe, the noarch support recipe, the conda-wasm
Python package, and the lockfile used by the demo environment:

```bash
pixi run -e recipes build-conda-wasm-lockfile
```

The `recipes/conda-wasm` package copies `conda_wasm.js` and
`conda_wasm_bg.wasm` from the Rust build output into the Python package's
`runtime_assets/` directory before packaging.

## Build the JupyterLite Site

Build the demo site with locally built packages:

```bash
pixi run -e demo demo-build-local
```

The local build adds this repository's `output/` channel so the JupyterLite
environment gets the locally built `conda`, `conda-wasm`, and support packages.

For a public-channel-only demo build, use:

```bash
pixi run -e demo demo-build
```

## Serve the Demo

Run:

```bash
pixi run -e demo demo-serve
```

Open:

```text
http://localhost:8888/lab/index.html
```

## Clean Generated Output

Use:

```bash
pixi run -e demo demo-clean
pixi run -e web wasm-clean
```

You may also remove recipe artifacts from `output/` when you need a clean
package rebuild.
