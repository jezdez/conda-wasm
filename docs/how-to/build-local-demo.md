# Build the Local Demo

Use this guide to build the WebAssembly module, package the Python runtime, and
serve the JupyterLite demo from this checkout.

::::{grid} 1 1 3 3
:gutter: 3

:::{grid-item-card} 1. Compile WASM
:class-card: sd-shadow-sm
Build `crates/conda-wasm` with `wasm-pack`.
:::

:::{grid-item-card} 2. Build packages
:class-card: sd-shadow-sm
Build patched conda, support packages, and the `conda-wasm` runtime package.
:::

:::{grid-item-card} 3. Build JupyterLite
:class-card: sd-shadow-sm
Create the static demo site under `demo/_output/`.
:::
::::

## Prerequisites

Install `pixi`. The repository tasks provide the Rust, Python, JupyterLite, and
recipe tooling through pixi environments.

Install `wasm-pack` if it is not already available:

```bash
pixi run cargo install wasm-pack
```

```{dropdown} Generated directories
The build writes generated artifacts under `crates/conda-wasm/pkg/`,
`output/`, `recipes/conda/lockfile-env/`, `jupyterlite/lib/`,
`jupyterlite/labextension/`, `demo/_env/`, and `demo/_output/`. They are
rebuildable and should not be edited by hand.
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

Choose the build mode that matches what you want to test.

::::{tab-set}

:::{tab-item} Local packages
Build the demo site with locally built packages:

```bash
pixi run -e demo demo-build-local
```

The local build adds this repository's `output/` channel so the JupyterLite
environment gets the locally built `conda`, `conda-wasm`, and support packages.
:::

:::{tab-item} Public channels
For a public-channel-only demo build:

```bash
pixi run -e demo demo-build
```
:::
::::

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

::::{tab-set}

:::{tab-item} Demo
```bash
pixi run -e demo demo-clean
```
:::

:::{tab-item} WASM
```bash
pixi run -e web wasm-clean
```
:::
::::

You may also remove recipe artifacts from `output/` when you need a clean
package rebuild.
