"""Runtime compatibility patches applied inside browser-hosted conda."""

from __future__ import annotations

import logging
import sys

from .compat.download import patch_download
from .compat.extract import patch_extraction
from .compat.notices import disable_outdated_conda_notice
from .compat.repodata import patch_repodata_cache
from .compat.subprocess import patch_subprocess
from .compat.timing import patch_timing
from .compat.urllib3 import patch_urllib3

log = logging.getLogger(__name__)

__all__ = ["patch_conda_internals", "patch_urllib3"]

conda_internals_patched = False


def patch_conda_internals() -> None:
    """Apply conda compatibility patches once when running under Emscripten."""
    global conda_internals_patched

    if sys.platform != "emscripten" or conda_internals_patched:
        return

    try:
        disable_outdated_conda_notice()
        patch_repodata_cache()
        patch_download()
        patch_extraction()
        patch_timing()
        patch_subprocess()
    except ImportError:
        log.debug("conda-wasm: conda internals not available to patch", exc_info=True)
        return

    conda_internals_patched = True
