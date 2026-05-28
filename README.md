# conda-wasm

Browser and WebAssembly tooling for conda.

This repository was split from `jezdez/conda-express` to house the WASM-specific
parts independently:

- `crates/cx-wasm`: Rust/WASM solver and package extraction support
- `conda-emscripten`: conda plugin for Emscripten environments
- `cx-jupyterlite`: JupyterLite integration
- `lite`: demo site
- `recipes`: Emscripten and WASM bridge conda recipes

The next migration step is to rename the remaining `cx-wasm` surfaces and add
first-class project documentation following the `conda-workspaces` /
`conda-exec` pattern.
