# Project Scope

`conda-wasm` owns the browser and WebAssembly conda stack.

It is not the native conda bootstrap builder, and it is not the `cx` product
distribution. Those responsibilities belong to `pronto` and `conda-express`.

::::{grid} 1 1 3 3
:gutter: 3

:::{grid-item-card} conda-wasm
:class-card: sd-shadow-sm
{bdg-primary}`browser runtime`
^^^
Browser, WebAssembly, Emscripten, JupyterLite, and browser package handling.
:::

:::{grid-item-card} pronto
:class-card: sd-shadow-sm
{bdg-secondary}`native builder`
^^^
Generic native builder/runtime for ready-to-run conda bootstrap binaries.
:::

:::{grid-item-card} conda-express
:class-card: sd-shadow-sm
{bdg-info}`product distribution`
^^^
Opinionated native conda distribution that publishes `cx` and `cxz`.
:::
::::

## What conda-wasm Owns

This repository owns browser-specific conda infrastructure:

- WebAssembly crates for solving, shard decoding, and package extraction
- Python runtime loading for generated WASM assets
- conda plugin hooks for the browser solver, extractor, virtual packages, and
  pre-command patches
- Emscripten conda recipes and patches
- IPython magics for running conda inside a browser kernel
- JupyterLite extension and demo notebooks
- packaging of the browser runtime as the `conda-wasm` Python distribution
- documentation for running and developing conda in JupyterLite or another
  Emscripten-hosted Python environment

The repository should be explicit about browser constraints: MEMFS, no native
subprocess support, synchronous XHR requirements in the worker path, Emscripten
platform tags, and package availability from Emscripten-compatible channels.

## What Pronto Owns

Pronto owns generic native bootstrap binary construction:

- deriving a runtime lock from conda or Pixi project metadata
- downloading package archives into native bundle layouts
- compiling the generic native runtime template
- producing `none`, `external`, and `embedded` artifact layouts
- writing artifact metadata and checksums
- exposing local builder and GitHub Action workflows

Pronto does not own JupyterLite, Emscripten conda patches, browser filesystem
behavior, or WebAssembly package extraction. It may consume conda package
metadata, but it targets native bootstrap binaries, not browser kernels.

## What conda-express Owns

`conda-express` owns the downstream `cx` and `cxz` distribution:

- binary names and user-facing product identity
- default native package set
- release channels and installer wrappers
- Homebrew, Docker, PyPI, crates.io, and GitHub Release packaging
- `cx` / `cxz` documentation and release policy

`conda-express` calls Pronto to build native binaries. It should not carry
browser-specific code, WebAssembly crates, JupyterLite extension code, or
Emscripten recipes.

## What Moved Here

Browser/WASM work that previously lived near `conda-express` now belongs in
`conda-wasm`:

- the Rust WASM solver and extractor crate
- Emscripten conda patches and recipes
- JupyterLite extension and static demo site
- Python runtime loader and packaged WASM assets
- `%conda` / `%conda_wasm` notebook workflow
- browser-specific conda plugin behavior

This split keeps each repository honest: `conda-wasm` explains browser conda,
Pronto explains native bootstrap construction, and `conda-express` explains the
official `cx` product.

## Contributor Routing

Use this rule of thumb:

::::{grid} 1 1 3 3
:gutter: 3

:::{grid-item-card} Put it in conda-wasm
Conda inside JupyterLite, Emscripten, browser fetch, MEMFS, WASM solving, WASM
extraction, or Emscripten recipes.
:::

:::{grid-item-card} Put it in Pronto
Generic native bootstrap binary generation or artifact layouts.
:::

:::{grid-item-card} Put it in conda-express
Official `cx` package choices, installation methods, Docker images, Homebrew
formulae, release workflows, or user-facing product defaults.
:::
::::
