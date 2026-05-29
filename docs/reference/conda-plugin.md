# Conda Plugin Reference

`conda-wasm` integrates with conda through conda's plugin API and a small set
of runtime patches for Emscripten.

::::{grid} 1 1 4 4
:gutter: 3

:::{grid-item-card} Solver
{bdg-primary}`conda_solvers`
:::

:::{grid-item-card} Extractor
{bdg-info}`conda_package_extractors`
:::

:::{grid-item-card} Patches
{bdg-warning}`conda_pre_commands`
:::

:::{grid-item-card} Platform
{bdg-secondary}`conda_virtual_packages`
:::
::::

## Entry Point

The Python package declares:

```toml
[project.entry-points.conda]
conda-wasm = "conda_wasm.plugin"
```

Conda discovers `conda_wasm.plugin` during plugin loading.

## Solver

`CondaWasmSolver` is registered under the solver name `conda-wasm`.

The solver:

1. Collects installed `PrefixRecord` entries from the target prefix.
2. Converts installed records and requested specs into a JSON request.
3. Calls the browser runtime's `js.fetch_and_solve`.
4. Converts returned solution records back into conda `PackageRecord` objects.
5. Preserves unchanged installed records so conda does not reinstall packages
   just because channel metadata was normalized.

The solver expects `js.fetch_and_solve` to be registered by
`conda_wasm.runtime.setup()`. If the runtime is installed but not ready, the
error message tells users how to call `await runtime.setup()`.

```{dropdown} Solver boundary
Conda still owns CLI semantics, transaction planning, prefix records, and link
actions. The plugin replaces the browser-incompatible solving backend with a
WASM-backed solver call.
```

## Package Extraction

In Emscripten environments, `conda_package_extractors` registers the
`wasm-extractor` package extractor for `.conda` and `.tar.bz2` archives.

The extractor reads package bytes, converts them to a JS `Uint8Array`, calls the
Rust WASM extractor, and writes extracted files into MEMFS through a Python
callback. For `.tar.bz2`, it can fall back to Python's streaming `tarfile`
mode when the WASM path fails.

## Pre-command Patches

`conda_pre_commands` applies compatibility patches before mutating commands.
The same patches can also be applied by the IPython magic path.

Patch behavior is idempotent. Calling `patch_conda_internals()` more than once
does not stack wrappers or reapply the same mutation.

::::{grid} 1 1 2 3
:gutter: 2

:::{grid-item-card} Downloads
MEMFS-safe package writes.
:::

:::{grid-item-card} Subprocesses
No-op browser-incompatible subprocess calls.
:::

:::{grid-item-card} Notices
Disable outdated notice behavior in browser environments.
:::

:::{grid-item-card} Repodata
Ignore cache-save edge cases under MEMFS.
:::

:::{grid-item-card} urllib3
Route Emscripten transport through synchronous XHR.
:::

:::{grid-item-card} Timing
Install opt-in timing wrappers.
:::
::::

## Virtual Packages

For `emscripten-*` subdirs, the plugin registers:

- `__unix`
- `__emscripten`

Those virtual package records let conda solves express browser/Emscripten
constraints using conda's normal virtual package machinery.

## Native Imports

Native Python imports should remain safe for smoke tests and package builds.
The plugin avoids importing browser-only APIs at module import time and guards
Emscripten-only behavior with `sys.platform == "emscripten"`.
