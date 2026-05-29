from __future__ import annotations

import os
import sys

CONDARC = """\
solver: conda-wasm
subdir: emscripten-wasm32
auto_activate_base: false
notify_outdated_conda: false
show_channel_urls: true
channels:
  - https://repo.prefix.dev/emscripten-forge-4x
  - conda-forge
"""


def bootstrap_prefix() -> None:
    """Create the minimal conda prefix metadata expected by conda."""
    prefix = sys.prefix
    conda_meta = os.path.join(prefix, "conda-meta")
    os.makedirs(conda_meta, exist_ok=True)

    history = os.path.join(conda_meta, "history")
    if not os.path.exists(history):
        with open(history, "w") as f:
            f.write("")

    condarc = os.path.join(prefix, ".condarc")
    if not os.path.exists(condarc):
        with open(condarc, "w") as f:
            f.write(CONDARC)

    os.environ.setdefault("CONDA_ROOT_PREFIX", prefix)
    os.environ.setdefault("CONDA_PREFIX", prefix)
    os.environ.setdefault("CONDARC", condarc)
    if sys.platform == "emscripten":
        os.environ.setdefault("CONDA_SUBDIR", "emscripten-wasm32")
