# conda-wasm

Browser and WebAssembly tooling for conda.

`conda-wasm` is the browser-specific conda stack. It makes real conda run in an
Emscripten Python runtime, using WebAssembly where native conda depends on
capabilities that are unavailable or too slow in the browser.

It is intentionally scoped to browser and WebAssembly work: the Rust WASM
module, the Python runtime package, conda plugin hooks, IPython magics,
JupyterLite integration, demo site, and recipes for Emscripten-hosted conda.
Native single-binary bootstrap distributions are handled elsewhere: `pronto`
builds generic native bootstrap binaries, and `conda-express` publishes the
opinionated `cx` and `cxz` distribution built with Pronto.

## Start Here

Use these docs by goal:

- Try the live browser demo if you want to see conda install packages in a
  notebook with no server.
- Use the how-to guides when you already know the task you need to perform.
- Use reference pages for exact repository layout and runtime/plugin behavior.
- Read explanation pages for scope, architecture, and how this project relates
  to `pronto` and `conda-express`.

## Project Map

| Component | Location | Role |
|---|---|---|
| Rust WASM module | `crates/conda-wasm/` | Solver, extractor, sharded repodata helpers, and browser fetch/decode glue compiled to WebAssembly |
| Python runtime package | `python/conda_wasm/` | Runtime loader, conda plugin, IPython magic package, Emscripten patches, and packaged WASM assets |
| JupyterLite extension | `jupyterlite/` | Routes notebook-level conda commands into the browser kernel workflow |
| Demo site | `demo/` | Static JupyterLite site and notebooks for trying the browser workflow |
| Patched conda recipe | `recipes/conda/` | Emscripten-oriented conda recipe with browser filesystem and subprocess patches |
| conda-wasm recipe | `recipes/conda-wasm/` | Packages the Python runtime and copied WASM artifacts |

## Try it

The GitHub Pages workflow publishes documentation at the repository root and
the JupyterLite demo under `/demo/`:

```text
https://jezdez.github.io/conda-wasm/demo/lab/index.html
```

```{toctree}
:caption: Tutorials
:maxdepth: 1

tutorials/try-browser-demo
```

```{toctree}
:caption: How-To Guides
:maxdepth: 1

how-to/use-conda-in-notebook
how-to/build-local-demo
```

```{toctree}
:caption: Reference
:maxdepth: 1

reference/repository-layout
reference/python-runtime-package
reference/browser-runtime
reference/conda-plugin
```

```{toctree}
:caption: Explanation
:maxdepth: 1

explanation/project-scope
explanation/architecture
guides/browser
```

```{toctree}
:caption: Project
:maxdepth: 1

changelog
```
