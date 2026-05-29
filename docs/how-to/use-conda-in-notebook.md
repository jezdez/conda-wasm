# Use conda in a Notebook

Use this guide when you already have a JupyterLite or xeus-python browser
environment that includes `conda-wasm` and patched conda.

## Register the Magics

Load the extension in a notebook:

```python
%load_ext conda_wasm
```

This registers `%conda` and `%conda_wasm`. Both call into
`conda_wasm.magic`.

Use `%conda` for normal work:

```python
%conda install zlib
%conda list
%conda info
```

Use `%conda_wasm` when a notebook should make the browser-specific execution
path explicit:

```python
%conda_wasm install lz4
```

## Install Packages

For mutating commands such as `install`, `update`, `remove`, and `create`, the
magic injects `--yes` when neither `--yes` nor `-y` is present. That avoids
interactive prompts, which do not fit notebook execution well.

```python
%conda install pillow scipy
```

After conda finishes, conda-wasm scans the prefix for new shared libraries and
loads them with `ctypes.CDLL(..., mode=ctypes.RTLD_GLOBAL)`. That step is what
allows newly installed C extension packages to be imported immediately in the
same kernel session.

## Wait for Runtime Setup

The runtime starts loading when `conda_wasm.runtime` is imported in an
Emscripten environment. If you run a conda command before the runtime is ready,
the magic prints:

```text
conda-wasm is still loading - please run the cell again in a moment
```

Run the cell again after the runtime finishes loading. In code that controls
startup explicitly, you can call:

```python
import conda_wasm.runtime as runtime

await runtime.setup()
```

## Enable Timing Output

Timing output is opt-in:

```python
import os

os.environ["CONDA_WASM_TIMING"] = "1"
```

Then run:

```python
%conda install lz4
```

The magic and compatibility patches print phase timing lines for patching,
solving, download/extract, transaction, shared-library loading, and totals.

## Understand Persistence

The browser environment uses Emscripten MEMFS. Installed packages are available
for the current page session, but they do not persist after reload unless the
hosting application adds a persistent filesystem layer.

For reproducible demos, keep important packages in the prebuilt JupyterLite
environment and use runtime `%conda install` for interactive examples.
