# Try conda in the Browser

This tutorial walks through the live JupyterLite demo. It shows the core promise
of `conda-wasm`: run real conda inside a browser tab and install a package into
the running kernel.

::::{grid} 1 1 3 3
:gutter: 3

:::{grid-item-card} Runtime
:class-card: sd-shadow-sm
{bdg-primary}`browser tab`
^^^
The Python kernel, conda runtime, and installed environment run locally in the
browser.
:::

:::{grid-item-card} Package install
:class-card: sd-shadow-sm
{bdg-info}`%conda`
^^^
The notebook magic calls real conda and delegates browser-specific work through
conda-wasm.
:::

:::{grid-item-card} Persistence
:class-card: sd-shadow-sm
{bdg-warning}`MEMFS`
^^^
Installed files live in memory and disappear when the page reloads.
:::
::::

## Open the Demo

```{button-link} https://jezdez.github.io/conda-wasm/demo/lab/index.html
:color: primary
:shadow:

Open the live JupyterLite demo
```

The demo is a static JupyterLite site. There is no notebook server behind the
page. The Python kernel, conda, conda-wasm runtime, packages, and installed
environment all run inside the browser.

## Load the Extension

Open a notebook and run:

```python
%load_ext conda_wasm
```

The extension registers two line magics:

- `%conda`
- `%conda_wasm`

Both call the same implementation. `%conda` is the normal user-facing spelling;
`%conda_wasm` is useful when you want to be explicit that the command is handled
by the browser runtime.

## Install a Package

Run:

```python
%conda install lz4
```

The magic adds `--yes` for mutating commands, bootstraps the conda prefix if
needed, applies Emscripten compatibility patches, and calls `conda.cli.main`.
The solve and package extraction are delegated to the conda-wasm WebAssembly
module through conda plugin hooks.

Now import the package:

```python
import lz4.frame

payload = lz4.frame.compress(b"conda in the browser")
lz4.frame.decompress(payload)
```

The package is installed into the browser's in-memory Emscripten filesystem.

```{dropdown} If the command says conda-wasm is still loading
The runtime starts in the background when `conda_wasm` is imported. Re-run the
cell after a moment. The message means setup has not finished yet; it is not an
installation failure.
```

## Inspect the Environment

Run regular conda commands:

::::{tab-set}

:::{tab-item} List packages
```python
%conda list
```
:::

:::{tab-item} Runtime info
```python
%conda info
```
:::

:::{tab-item} Search
```python
%conda search lz4
```
:::
::::

These commands still run through conda. The browser-specific pieces are the
runtime, solver backend, extraction path, and filesystem/network patches needed
to make conda operate under Emscripten.

## What to Notice

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} Local kernel
The kernel runs in the browser tab, not on a notebook server.
:::

:::{grid-item-card} Volatile installs
Installed files live in MEMFS and disappear when the page reloads.
:::

:::{grid-item-card} Compatible channels
Packages are downloaded from Emscripten-compatible conda channels.
:::

:::{grid-item-card} C extensions
C extension packages can work when they are available for `emscripten-wasm32`.
conda-wasm loads newly installed `.so` files after mutating conda commands.
:::
::::

Next, read {doc}`../how-to/use-conda-in-notebook` for practical notebook
commands or {doc}`../explanation/architecture` for the execution model.
