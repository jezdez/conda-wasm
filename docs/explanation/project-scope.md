# Development Scope

Use this page when deciding whether a change belongs in this repository.

`conda-wasm` is focused on making conda work inside browser-hosted Python
environments. That scope includes the runtime pieces, packaging recipes,
JupyterLite integration, and documentation needed to build, test, and explain
that workflow.

::::{grid} 1 1 3 3
:gutter: 3

:::{grid-item-card} Browser runtime
:class-card: sd-shadow-sm
{bdg-primary}`runtime`
^^^
Runtime setup, plugin hooks, `%conda` magics, browser filesystem behavior, and
shared-library loading.
:::

:::{grid-item-card} WebAssembly
:class-card: sd-shadow-sm
{bdg-secondary}`wasm`
^^^
Solver, extractor, sharded repodata helpers, and generated WASM assets used by
the Python runtime.
:::

:::{grid-item-card} Demo stack
:class-card: sd-shadow-sm
{bdg-info}`jupyterlite`
^^^
JupyterLite extension, demo notebooks, local demo build, docs, and
Emscripten-compatible recipes.
:::
::::

## In Scope

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

## Out of Scope

Keep these concerns out of this repository unless they directly affect the
browser runtime:

- native desktop or server bootstrap binaries
- installer, launcher, and product-distribution packaging for native platforms
- package selection policy for native user distributions
- generic conda behavior that is not changed by browser or Emscripten
  constraints
- release workflows for downstream products that consume conda packages

Native bootstrap binaries belong in
{external+conda-ship:doc}`conda-ship <index>`. Product-specific native
distribution policy belongs in the downstream distribution that publishes those
native artifacts.

It is fine for docs or comments to mention an external project when that helps
explain a concrete migration or compatibility issue. Avoid using this repository
to explain external ownership as part of the normal user journey.

## Contributor Routing

Use this rule of thumb:

::::{grid} 1 1 3 3
:gutter: 3

:::{grid-item-card} Keep it here
The change touches JupyterLite, Emscripten, browser fetch, MEMFS, WASM solving,
WASM extraction, `%conda` in a browser kernel, or Emscripten recipes.
:::

:::{grid-item-card} Coordinate elsewhere
The change is about native installers, native artifact layouts, desktop/server
launchers, or downstream product defaults.
:::

:::{grid-item-card} Document the constraint
If a browser-specific workaround looks surprising, explain the browser,
Emscripten, or conda plugin constraint next to the implementation or in the
nearest reference page.
:::
::::
