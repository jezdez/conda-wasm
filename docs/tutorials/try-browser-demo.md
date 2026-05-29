# Try conda in the Browser

This tutorial walks through the live JupyterLite demo. It shows the core promise
of `conda-wasm`: run real conda inside a browser tab and install a package into
the running kernel.

## Open the Demo

Open:

```text
https://jezdez.github.io/conda-wasm/demo/lab/index.html
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

## Inspect the Environment

Run regular conda commands:

```python
%conda list
%conda info
%conda search lz4
```

These commands still run through conda. The browser-specific pieces are the
runtime, solver backend, extraction path, and filesystem/network patches needed
to make conda operate under Emscripten.

## What to Notice

- The kernel is local to the browser tab.
- Installed files live in MEMFS and disappear when the page is reloaded.
- Packages are downloaded from Emscripten-compatible conda channels.
- C extension packages can work when they are available for
  `emscripten-wasm32`; conda-wasm loads newly installed `.so` files after a
  mutating conda command.

Next, read {doc}`../how-to/use-conda-in-notebook` for practical notebook
commands or {doc}`../explanation/architecture` for the execution model.
