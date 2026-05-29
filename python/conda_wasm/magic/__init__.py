from __future__ import annotations

import logging

from .command import run_conda_magic
from .prefix import bootstrap_prefix

log = logging.getLogger(__name__)

__all__ = ["bootstrap_prefix", "conda_wasm_magic", "register"]


def conda_wasm_magic(line: str) -> None:
    """IPython line magic: ``%conda install zlib`` or ``%conda_wasm install zlib``."""
    run_conda_magic(line)


def register(ip=None) -> None:
    """Register ``%conda_wasm`` and ``%conda`` with the active IPython instance."""
    if ip is None:
        try:
            ip = get_ipython()  # type: ignore[name-defined]  # noqa: F821
        except NameError:
            return
    if ip is None:
        return
    ip.register_magic_function(conda_wasm_magic, magic_kind="line", magic_name="conda")
    ip.register_magic_function(
        conda_wasm_magic, magic_kind="line", magic_name="conda_wasm"
    )
    log.debug("conda-wasm: %%conda_wasm and %%conda magics registered")
