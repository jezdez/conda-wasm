# Python Runtime Package Reference

The Python source tree under `python/` builds the `conda-wasm` Python
distribution. Its import package is `conda_wasm`.

This package is the browser runtime and conda plugin layer for
Emscripten-hosted Python. It is not the whole project, and it is not useful as a
standalone replacement for conda. The full browser stack also needs:

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} Rust artifacts
`crates/conda-wasm/pkg/`
^^^
Generated `wasm-pack` output copied into the Python package at recipe build
time.
:::

:::{grid-item-card} Patched conda
`recipes/conda/`
^^^
Conda with Emscripten-oriented patches for browser filesystem and platform
constraints.
:::

:::{grid-item-card} Browser Python runtime
JupyterLite / xeus-python
^^^
Python compiled for Emscripten, usually running in a WebWorker.
:::

:::{grid-item-card} Compatible channels
`emscripten-wasm32` packages
^^^
Channels that provide browser-compatible packages for the target platform.
:::
::::

The `recipes/conda-wasm/` recipe copies `conda_wasm.js` and
`conda_wasm_bg.wasm` into `conda_wasm/runtime_assets/` before packaging. In the
demo environment, patched conda is installed separately; the `conda-wasm`
runtime package keeps native imports light enough for package-build smoke tests.

## Top-level `conda_wasm`

The top-level package provides the IPython extension entry point:

```python
%load_ext conda_wasm
```

`load_ipython_extension()` registers the `%conda` and `%conda_wasm` magics via
`conda_wasm.magic.register()` and imports `conda_wasm.runtime` to start
background runtime loading under Emscripten.

On Emscripten, `conda_wasm.__init__` also suppresses noisy browser-runtime
warnings and urllib3 debug logs. Native imports should remain safe.

## `conda_wasm.runtime`

`conda_wasm.runtime` owns browser runtime setup. Its `__init__.py` is the public
runtime API:

```python
import conda_wasm.runtime as runtime

await runtime.setup()
runtime.is_ready()
```

The runtime package contains:

| Module | Role |
|---|---|
| `assets.py` | Locates packaged `conda_wasm.js` and `conda_wasm_bg.wasm` |
| `loader.py` | Loads the generated ES module and initializes wasm-bindgen |
| `globals.py` | Registers JS globals and Python callbacks used by Rust and conda |
| `prefetch.py` | Prefetches sharded repodata for installed packages |
| `state.py` | Stores runtime setup state, locks, and long-lived pyjs handles |

The runtime auto-schedules setup when imported under `sys.platform ==
"emscripten"`. Native imports are safe and do not try to load browser APIs.

```{dropdown} Runtime setup lifecycle
`runtime.setup()` is async because it has to read packaged assets, create
browser `Blob` URLs, dynamically import the generated ES module, initialize
wasm-bindgen, register JS globals, and prefetch sharded repodata. The module
keeps state in `runtime.state` so repeated setup calls share the same task.
```

## `conda_wasm.magic`

`conda_wasm.magic` owns magic registration and command dispatch. It is used by
the top-level `%load_ext conda_wasm` entry point, but users normally do not load
`conda_wasm.magic` directly.

The public helper is:

```python
from conda_wasm.magic import register
```

After registration, notebooks use:

```python
%conda install lz4
```

The magic package contains:

| Module | Role |
|---|---|
| `command.py` | `%conda` / `%conda_wasm` command parsing and dispatch |
| `prefix.py` | Minimal browser prefix bootstrap and `.condarc` setup |
| `shared_libs.py` | Post-install shared-library discovery and loading |

The magic calls `conda.cli.main.main` directly. It does not shell out to a
`conda` executable.

```{tip}
User notebooks normally interact with the top-level extension:
`%load_ext conda_wasm`. Direct imports from `conda_wasm.magic` are mainly for
integration and testing code.
```

## `conda_wasm.plugin`

`conda_wasm.plugin` is the conda plugin entry point declared in
`python/pyproject.toml`:

```toml
[project.entry-points.conda]
conda-wasm = "conda_wasm.plugin"
```

When conda loads the plugin, it registers:

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} `conda_solvers`
Exposes `CondaWasmSolver` as `conda-wasm`.
:::

:::{grid-item-card} `conda_package_extractors`
Exposes the WASM extractor in Emscripten.
:::

:::{grid-item-card} `conda_pre_commands`
Applies browser compatibility patches before mutating commands.
:::

:::{grid-item-card} `conda_virtual_packages`
Exposes `__unix` and `__emscripten` virtual package records for Emscripten
subdirs.
:::
::::

The plugin package keeps imports lazy where native smoke tests or conda startup
would otherwise import browser-only or heavy runtime code too early.

`conda_wasm.plugin` can be imported on native Python without conda installed,
but its hook implementations only do useful work when conda is present and, for
browser-only behavior, when `sys.platform == "emscripten"`.

## `conda_wasm.plugin.compat`

`plugin/compat/` contains focused runtime patches:

| Module | Patch |
|---|---|
| `download.py` | Replaces conda download writes with a no-seek MEMFS-safe path |
| `extract.py` | Routes package extraction through the WASM extractor |
| `notices.py` | Disables the outdated conda notice in browser environments |
| `repodata.py` | Ignores MEMFS cache-save edge cases |
| `subprocess.py` | No-ops conda subprocess calls that cannot work in the browser |
| `timing.py` | Installs optional timing wrappers when `CONDA_WASM_TIMING` is enabled |
| `urllib3.py` | Routes urllib3's Emscripten transport through synchronous XHR |

`plugin/patches.py` coordinates those patches and remains the stable import
surface for callers.
