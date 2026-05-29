from __future__ import annotations

import os


def timing_enabled() -> bool:
    """Return True when runtime timing diagnostics should be printed."""
    value = os.environ.get("CONDA_WASM_TIMING", "")
    return value.lower() in {"1", "true", "yes", "on"}


def emit_timing(label: str, elapsed: float, detail: str | None = None) -> None:
    """Print a timing line when ``CONDA_WASM_TIMING`` is enabled."""
    if not timing_enabled():
        return

    suffix = f" ({detail})" if detail else ""
    print(f"[conda-wasm-timing] {label:<14} {elapsed:.2f}s{suffix}")
