# conda-wasm

Browser and WebAssembly tooling for conda.

`conda-wasm` contains the JupyterLite pipeline that was split out of
`conda-express`: the Rust/WASM solver and extractor, the Emscripten conda
plugin, the JupyterLite extension, the demo site, and the recipes needed to
package the browser runtime.

## Components

| Component | Location | Role |
|---|---|---|
| cx-wasm | `crates/cx-wasm/` | Rust solver, extractor, and shard decoder compiled to WebAssembly |
| conda-emscripten | `conda-emscripten/` | conda plugin for Emscripten environments |
| cx-jupyterlite | `cx-jupyterlite/` | JupyterLite extension that routes conda commands through the browser kernel |
| cx-wasm-kernel | `recipes/cx-wasm-kernel/` | WASM bridge package for xeus-python |
| Demo site | `lite/` | Static JupyterLite site and notebooks |

## Try it

The GitHub Pages workflow publishes documentation at the repository root and
the JupyterLite demo under `/demo/`:

```text
https://jezdez.github.io/conda-wasm/demo/lab/index.html
```

```{toctree}
:hidden:
:caption: Guides

guides/browser
```

```{toctree}
:hidden:
:caption: Project

changelog
```
