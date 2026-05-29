# Browser Runtime Reference

The browser runtime is the glue between Python, JavaScript, and the Rust WASM
module.

::::{grid} 1 1 3 3
:gutter: 3

:::{grid-item-card} Setup API
:class-card: sd-shadow-sm
Initializes packaged WASM assets and registers browser call points.
:::

:::{grid-item-card} Global bridge
:class-card: sd-shadow-sm
Exposes stable JS functions used by conda, Python, pyjs, and Rust.
:::

:::{grid-item-card} Shard prefetch
:class-card: sd-shadow-sm
Moves predictable repodata network work into startup.
:::
::::

## Setup API

```python
import conda_wasm.runtime as runtime

await runtime.setup()
runtime.is_ready()
```

`setup()` performs these steps:

::::{grid} 1 1 2 2
:gutter: 2

:::{grid-item-card} 1. Locate assets
Find packaged `conda_wasm.js` and `conda_wasm_bg.wasm`.
:::

:::{grid-item-card} 2. Import WASM module
Create browser `Blob` URLs, dynamically import the generated ES module, and run
wasm-bindgen initialization.
:::

:::{grid-item-card} 3. Register globals
Install JS global functions used by conda and the Rust WASM module.
:::

:::{grid-item-card} 4. Prefetch shards
Mark setup complete and prefetch sharded repodata for packages already
installed in the browser prefix.
:::
::::

`is_ready()` reports whether setup has completed.

## Registered Globals

The runtime registers a small set of JS global functions because conda, Python,
pyjs, and Rust all need to meet at stable call points:

| Global | Purpose |
|---|---|
| `sync_fetch_binary(url)` | Synchronous binary fetch callback used by Rust |
| `sync_fetch_text(url)` | Synchronous text fetch callback used by Rust |
| `fetch_and_solve(request)` | Solver entry point called by `CondaWasmSolver` |
| `conda_wasm_extract_package(bytes, filename, onFile)` | Extractor entry point |
| `get_shard_urls(request)` | Computes sharded repodata URLs for seed package names |
| `decode_shard_deps(data)` | Decodes dependency names from a fetched shard |
| `clear_repodata_cache()` | Clears Rust-side repodata cache |
| `condaWasmPrefetchBatch(urls)` | Fetches shard URLs asynchronously in parallel |

The runtime also keeps pyjs callable handles alive in Python state. Without
those references, pyjs can garbage-collect callbacks while JavaScript still
needs them.

```{dropdown} Why globals instead of direct imports everywhere?
Conda, Python callbacks, pyjs, and Rust-generated JavaScript are loaded through
different mechanisms. The globals provide a narrow rendezvous point that stays
stable while each layer keeps its own import and initialization rules.
```

## Shard Prefetch

At setup time, `prefetch_installed()` scans `sys.prefix/conda-meta/` for
installed package records and uses those package names as seeds.

For each level:

1. Ask Rust for shard URLs for the current package names.
2. Fetch new shard URLs in parallel with JavaScript `fetch()`.
3. Store fetched bytes in a JavaScript `Map`.
4. Decode dependency names from the fetched shard bytes.
5. Queue unseen dependencies for the next level.

Later, when the solver synchronously requests shard bytes, it first checks the
prefetch cache. This moves most network work to startup and leaves interactive
solves mostly CPU-bound.

```{note}
Browser worker solves still need a synchronous fetch path for conda call sites
that are not async-aware. Prefetching reduces how often that path has to touch
the network during an interactive notebook command.
```

## Timing Diagnostics

Set `CONDA_WASM_TIMING=1` to print timing output from the Python runtime,
magic, and compatibility patches.

```python
import os

os.environ["CONDA_WASM_TIMING"] = "1"
```

Timing output is intentionally opt-in. The normal notebook path should not emit
phase timings unless a user or developer asks for them.
