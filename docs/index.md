# conda-wasm

Browser and WebAssembly tooling for conda.
{bdg-primary}`browser` {bdg-secondary}`WebAssembly` {bdg-info}`JupyterLite` {bdg-light}`Emscripten`

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

Use these docs by goal.

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} Try conda in the browser
:link: tutorials/try-browser-demo
:link-type: doc
:class-card: sd-shadow-sm sd-card-hover

Open the live JupyterLite demo, load `conda_wasm`, install a package, and see
where the browser runtime fits.
:::

:::{grid-item-card} Use conda in a notebook
:link: how-to/use-conda-in-notebook
:link-type: doc
:class-card: sd-shadow-sm sd-card-hover

Run `%conda`, understand runtime readiness, enable timing output, and account
for MEMFS persistence.
:::

:::{grid-item-card} Build the local demo
:link: how-to/build-local-demo
:link-type: doc
:class-card: sd-shadow-sm sd-card-hover

Build the Rust WASM module, recipes, lockfile, and static JupyterLite site from
this checkout.
:::

:::{grid-item-card} Read the architecture
:link: explanation/architecture
:link-type: doc
:class-card: sd-shadow-sm sd-card-hover

Follow how the IPython magic, conda plugin, Rust WASM module, and browser
filesystem cooperate.
:::
::::

## Project Map

::::{grid} 1 1 2 3
:gutter: 3

:::{grid-item-card} Rust WASM module
:class-card: conda-component-card
`crates/conda-wasm/`
^^^
Solver, extractor, sharded repodata helpers, and browser fetch/decode glue
compiled to WebAssembly.
:::

:::{grid-item-card} Python runtime package
:class-card: conda-component-card
`python/conda_wasm/`
^^^
Runtime loader, conda plugin, IPython magic package, Emscripten patches, and
packaged WASM assets.
:::

:::{grid-item-card} JupyterLite extension
:class-card: conda-component-card
`jupyterlite/`
^^^
Routes notebook-level conda commands into the browser kernel workflow.
:::

:::{grid-item-card} Demo site
:class-card: conda-component-card
`demo/`
^^^
Static JupyterLite site and notebooks for trying the browser workflow.
:::

:::{grid-item-card} Patched conda recipe
:class-card: conda-component-card
`recipes/conda/`
^^^
Emscripten-oriented conda recipe with browser filesystem and subprocess
patches.
:::

:::{grid-item-card} conda-wasm recipe
:class-card: conda-component-card
`recipes/conda-wasm/`
^^^
Packages the Python runtime and copied WASM artifacts.
:::
::::

See {doc}`reference/repository-layout` for the full file-by-file map.

## Try it

The GitHub Pages workflow publishes documentation at the repository root and
the JupyterLite demo under `/demo/`:

```{button-link} https://jezdez.github.io/conda-wasm/demo/lab/index.html
:color: primary
:shadow:

Open the live JupyterLite demo
```

## Repository Boundaries

::::{grid} 1 1 3 3
:gutter: 3

:::{grid-item-card} conda-wasm
:class-card: sd-shadow-sm
{bdg-primary}`browser`
^^^
Browser conda, WebAssembly, Emscripten recipes, JupyterLite integration, and
runtime package behavior.
:::

:::{grid-item-card} pronto
:class-card: sd-shadow-sm
{bdg-secondary}`native builder`
^^^
Generic native bootstrap binary construction and artifact layouts.
:::

:::{grid-item-card} conda-express
:class-card: sd-shadow-sm
{bdg-info}`cx distribution`
^^^
The opinionated native `cx` and `cxz` product distribution built with Pronto.
:::
::::

Read {doc}`explanation/project-scope` when deciding where a change belongs.

```{toctree}
:caption: Tutorials
:maxdepth: 1
:hidden:

tutorials/try-browser-demo
```

```{toctree}
:caption: How-To Guides
:maxdepth: 1
:hidden:

how-to/use-conda-in-notebook
how-to/build-local-demo
```

```{toctree}
:caption: Reference
:maxdepth: 1
:hidden:

reference/repository-layout
reference/python-runtime-package
reference/browser-runtime
reference/conda-plugin
```

```{toctree}
:caption: Explanation
:maxdepth: 1
:hidden:

explanation/project-scope
explanation/architecture
guides/browser
```

```{toctree}
:caption: Project
:maxdepth: 1
:hidden:

changelog
```
