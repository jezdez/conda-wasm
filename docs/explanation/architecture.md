# Architecture

`conda-wasm` lets conda run in a browser by keeping conda as the orchestrator
and replacing only the parts that cannot work well in an Emscripten runtime.

The result is not a new package manager. It is real conda, running in Python
compiled to WebAssembly, with browser-specific solver, extractor, fetch, and
filesystem integration.

::::{grid} 1 1 2 4
:gutter: 3

:::{grid-item-card} Conda stays in charge
Command semantics, transactions, prefix records, and CLI behavior remain conda
behavior.
:::

:::{grid-item-card} WASM replaces native gaps
Solving, extraction, and shard decoding move to browser-safe WebAssembly paths.
:::

:::{grid-item-card} Runtime joins the layers
Python, JavaScript, pyjs, and Rust communicate through registered browser call
points.
:::

:::{grid-item-card} MEMFS shapes persistence
Installed files live in the browser filesystem unless the host adds persistent
storage.
:::
::::

## Execution Model

```
Browser tab
  `-- JupyterLite application
      `-- JupyterLite extension
          `-- xeus-python kernel in a WebWorker
              `-- Python on Emscripten
                  |-- conda_wasm.runtime
                  |-- conda_wasm.magic
                  `-- conda
                      `-- conda_wasm.plugin
                          |-- CondaWasmSolver
                          |-- WASM package extractor
                          |-- Emscripten virtual packages
                          `-- compatibility patches
```

The JupyterLite extension improves notebook ergonomics. The Python package is
what makes conda work in the kernel.

```{dropdown} Read the tree from top to bottom
The browser tab hosts JupyterLite on the main thread. The Python kernel runs in
a WebWorker. Inside that worker, `conda_wasm.runtime` initializes the generated
WASM module, `conda_wasm.magic` turns notebook commands into conda calls, and
`conda_wasm.plugin` replaces browser-incompatible conda internals at plugin
boundaries.
```

## Startup

When the runtime is imported under Emscripten, it schedules browser setup:

1. Load packaged `conda_wasm.js` and `conda_wasm_bg.wasm`.
2. Initialize the wasm-bindgen module.
3. Register Python callbacks and JavaScript globals.
4. Prefetch sharded repodata for packages already installed in the prefix.

The prefetch phase overlaps with notebook startup. That matters because conda
solves are interactive in a notebook; the runtime shifts predictable network
work earlier.

## Command Execution

When a user runs:

```python
%conda install lz4
```

the flow is:

::::{grid} 1 1 2 2
:gutter: 2

:::{grid-item-card} 1. Magic dispatch
`conda_wasm.magic.command` parses the line and injects `--yes` for mutating
commands when needed.
:::

:::{grid-item-card} 2. Prefix bootstrap
`conda_wasm.magic.prefix` creates minimal prefix metadata and a browser
`.condarc` on first use.
:::

:::{grid-item-card} 3. Patch and call conda
`conda_wasm.plugin.patches` applies compatibility patches, then the magic calls
`conda.cli.main.main`.
:::

:::{grid-item-card} 4. Solve and extract
Conda resolves through `CondaWasmSolver`, downloads through a MEMFS-safe patch,
and extracts through the WASM extractor.
:::

:::{grid-item-card} 5. Load new shared libraries
After a mutating command, conda-wasm scans for new `.so` files and loads them
so imports work in the same kernel session.
:::
::::

Conda still owns command semantics, transaction planning, link actions, prefix
records, package cache records, and user-facing CLI behavior.

## Why Patches Still Exist

The conda package recipe is patched for Emscripten, but runtime patches remain
as belt-and-suspenders compatibility. They also keep the Python package useful
against unpatched or partially patched conda builds during development.

The runtime patches cover areas where native assumptions leak through:

- file seeking in package downloads and extraction
- subprocess execution
- platform and filesystem paths
- outdated conda notices
- package-cache save behavior
- urllib3's Emscripten transport path

## Package Availability

Compiled packages must exist for `emscripten-wasm32`. `conda-wasm` does not
make arbitrary native packages browser-compatible. It makes conda able to
install and use packages that have been built for the browser platform.

Pure Python packages can come from ordinary noarch conda packages. C extension
packages need Emscripten-compatible builds, typically from Emscripten-oriented
channels.

## Limits

::::{grid} 1 1 2 3
:gutter: 2

:::{grid-item-card} Volatile filesystem
MEMFS is volatile unless the host application adds persistence.
:::

:::{grid-item-card} No post-link subprocesses
Post-link subprocesses are skipped.
:::

:::{grid-item-card} Browser filesystem rules
Symlink and hardlink behavior is constrained by the browser filesystem.
:::

:::{grid-item-card} Browser network rules
Browser security rules govern network access.
:::

:::{grid-item-card} Emscripten platform
The supported platform is `emscripten-wasm32`.
:::
::::
