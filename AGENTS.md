# AGENTS.md - conda-wasm coding guidelines

## Project Structure

- `conda-wasm` is a browser/WebAssembly stack for running real conda in
  JupyterLite and other Emscripten-hosted Python environments. The repository
  contains the Rust WASM module, the Python runtime and conda plugin, the
  JupyterLite frontend extension, demo site assets, docs, and conda recipes.

- The Rust crate lives in `crates/conda-wasm/`. Keep Rust code split by
  responsibility: `bootstrap.rs` for startup/bootstrap helpers, `solve.rs` for
  solver entry points, `extract.rs` for package extraction, `sharded.rs` for
  sharded repodata handling, `gateway.rs` for fetch/decode plumbing, and
  `error.rs` for shared error conversion. Public WASM exports belong in
  `lib.rs`; substantial logic belongs in the focused modules.

- The Python package lives in `python/conda_wasm/`. Keep the public API
  packages small:
  `runtime/__init__.py` owns browser runtime setup, with runtime helpers in
  `runtime/assets.py`, `runtime/loader.py`, `runtime/globals.py`,
  `runtime/prefetch.py`, and `runtime/state.py`.
  `magic/__init__.py` owns IPython magic registration, with command, prefix,
  and shared-library helpers in `magic/command.py`, `magic/prefix.py`, and
  `magic/shared_libs.py`.
  `plugin/__init__.py` owns conda hook registration,
  `plugin/solver.py` owns the conda solver backend,
  `plugin/extractor.py` owns package extraction helpers, and
  `plugin/patches.py` is the runtime patch facade.

- Do not introduce generic `_support` packages or underscore module packages.
  Prefer concrete package names that are already part of the public import
  surface, such as `runtime/`, `magic/`, and `plugin/compat/`. Avoid "bridge",
  `cx`, and `conda-express` terminology in new code.

- `plugin/compat/` contains focused compatibility patches for conda under
  Emscripten. Keep each patch in the module named for the thing being patched
  (`download.py`, `extract.py`, `repodata.py`, `subprocess.py`, `urllib3.py`,
  etc.). `plugin/patches.py` should stay a small coordinator.

- The JupyterLite extension lives in `jupyterlite/`. TypeScript source belongs
  in `jupyterlite/src/`, built output in `jupyterlite/lib/` and
  `jupyterlite/labextension/` is generated and should not be hand-edited.

- The demo site lives in `demo/`. Demo notebooks and JupyterLite config should
  demonstrate the real browser workflow, not duplicate runtime implementation
  logic.

- Recipes live in `recipes/`. `recipes/conda/` is the patched conda recipe for
  Emscripten, and `recipes/conda-wasm/` packages the Python runtime plus WASM
  assets copied from `crates/conda-wasm/pkg/`.

- Documentation lives in `docs/` and uses Sphinx with `conda-sphinx-theme`,
  `myst-parser`, `sphinx-design`, `sphinx-copybutton`, `sphinx-reredirects`,
  and `sphinx-sitemap`.

## Naming

- Prefer direct, descriptive names over private-by-default names. A leading
  underscore is appropriate for Python protocol hooks, third-party API
  contracts, or a genuinely local implementation variable, but not as a general
  way to organize modules.

- Keep public imports stable for users: `conda_wasm.runtime`,
  `conda_wasm.magic`, and `conda_wasm.plugin.patches` are public surfaces.
  Move complexity behind them without changing their import paths.

- Use `conda-wasm` for the project/package/crate and `conda_wasm` for Python
  import paths. Do not reintroduce `cx-wasm`, `cx-jupyterlite`,
  `conda-emscripten-plugin`, or `conda-express` names.

## Imports

- Use relative imports for intra-package Python references when practical
  (`from .loader import load_conda_wasm`,
  `from ..extractor import extract_wasm`). Absolute `conda_wasm.*` imports are
  acceptable from support code that is intentionally crossing package
  boundaries or avoiding circular imports.

- Inline imports are reserved for platform-specific or optional runtime
  dependencies. Acceptable cases include `js`/`pyjs`, conda internals that may
  not be installed in native smoke tests, plugin hook bodies loaded by conda,
  and browser-only paths. Everywhere else, imports belong at the top of the
  module.

- All Python modules should use `from __future__ import annotations`.

## Dependencies

- Minimize the dependency graph. Prefer stdlib, conda APIs, Rust crates already
  in use, or JupyterLite/JupyterLab packages already required by the extension
  over adding new dependencies.

- Pin minimum supported versions in manifests and recipes, not exact versions,
  unless an exact pin is required for a known compatibility constraint.

- After changing `pixi.toml`, always run `pixi lock --check` first. If the
  lockfile is out of date, run `pixi lock` and keep the `pixi.lock` update with
  the manifest change.

## Python and Conda Plugin Code

- Use modern type annotations (`str | None`, `list[str]`, `dict[str, Any]`).

- Use conda's own APIs where available (`conda.base.context.context`,
  `conda.plugins.types`, `conda.models.records`, `conda.gateways.*`) instead of
  reimplementing conda behavior.

- Keep conda plugin import overhead low. `conda_wasm.plugin` is discovered by
  conda through `[project.entry-points.conda]`, so avoid importing heavy solver,
  runtime, browser, or extraction code at module import time.

- Runtime patches should be idempotent. A patch function should be safe to call
  from both the `%conda` magic path and conda's `conda_pre_commands` hook.

- Browser-only code must guard native execution. Use `sys.platform ==
  "emscripten"` checks where importing or calling JS/browser APIs would fail on
  native Python.

- Timing and diagnostic output should be opt-in unless it is essential user
  feedback. Use `CONDA_WASM_TIMING=1` for timing details.

## Rust Code

- Keep WASM exports thin. Parse inputs, call focused helpers, and convert
  errors at the boundary.

- Prefer typed request/response structs with `serde` over ad hoc JSON access.

- Use `wasm-bindgen` and `web-sys` APIs deliberately. When a function must work
  in the browser worker context, avoid APIs that only exist on the main thread.

- Run `pixi run wasm-test` after changing Rust logic. Run
  `pixi run -e web wasm-build` when changes affect exported WASM artifacts.

## JupyterLite Extension

- Keep TypeScript changes scoped to the extension behavior in
  `jupyterlite/src/`. Do not edit generated `lib/` or `labextension/` output by
  hand.

- Run `pixi run -e demo demo-build` or `pixi run -e demo demo-build-local`
  after changes that affect the demo or extension integration. Use the local
  build when validating locally built `conda-wasm` packages.

## Testing and Verification

- For Python-only changes, at minimum run:
  `python3 -m compileall -q python demo/build.py`.

- For import-surface changes, run a native import smoke test with
  `sys.path.insert(0, "python")` and import `conda_wasm.runtime`,
  `conda_wasm.magic`, and the relevant plugin modules.

- For package changes, build the recipe with a temporary output directory to
  avoid local `output/` cleanup noise:
  `pixi run -e recipes rattler-build build --recipe recipes/conda-wasm/recipe.yaml -c conda-forge --output-dir /private/tmp/conda-wasm-output`.

- For docs changes, run `pixi run -e docs docs`.

- For recipe changes, run the relevant recipe task from the `recipes`
  environment. Use `pixi run -e recipes build-conda-wasm` for the Python/WASM
  package and `pixi run -e recipes build-conda` for the patched conda recipe.

- Always run `git diff --check` before considering the work done.

## Documentation

- Follow Diataxis structure where the docs grow: tutorials for learning paths,
  how-to guides for task-oriented workflows, reference for exact behavior, and
  explanation for design tradeoffs.

- Keep browser workflow docs concrete. Show how the Rust WASM module, Python
  runtime, conda plugin, patched conda recipe, and JupyterLite demo fit
  together.

- Avoid excessive bold and italic in prose, list items, and headings. Let the
  text carry the emphasis.

- Keep `sphinx-design` tab labels short to avoid overflow on narrow viewports.

## Generated Files and Cleanup

- Do not hand-edit generated outputs: Rust `target/`, `crates/conda-wasm/pkg/`,
  JupyterLite `lib/`, JupyterLite `labextension/`, docs `_build/`, demo
  `_output/`, demo `_env/`, Python `__pycache__/`, and recipe `output/`.

- Remove `.DS_Store`, `__pycache__/`, and temporary build output before final
  status checks.
