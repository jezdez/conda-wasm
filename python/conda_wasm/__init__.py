"""conda-wasm browser runtime and conda plugins."""

__version__ = "0.1.0"

import logging
import sys
import warnings
from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)

if sys.platform == "emscripten":
    # Emscripten can't start threads; silence tqdm's monitor warning.
    warnings.filterwarnings(
        "ignore", message="tqdm:disabling monitor", category=FutureWarning
    )
    warnings.filterwarnings(
        "ignore", message="tqdm:disabling monitor", category=UserWarning
    )
    try:
        from tqdm import TqdmMonitorWarning

        warnings.filterwarnings("ignore", category=TqdmMonitorWarning)
    except ImportError:
        pass

    # urllib3 DEBUG-level connection logs are noisy in the browser console.
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def load_ipython_extension(ip):
    """IPython extension entry point: ``%load_ext conda_wasm``.

    Registers the ``%conda_wasm`` and ``%conda`` line magics and kicks off background
    WASM loading so that ``%conda_wasm install <pkg>`` works immediately.
    """
    from .magic import register

    register(ip)

    try:
        import conda_wasm.runtime  # noqa: F401  # import triggers background WASM load

        print("%conda_wasm / %conda magic ready - WASM runtime loading in background")
    except ImportError:
        print(
            "%conda_wasm / %conda magic registered, but the conda-wasm runtime is not installed.\n"
            "Rebuild with: pixi run -e recipes build-conda-wasm"
        )
