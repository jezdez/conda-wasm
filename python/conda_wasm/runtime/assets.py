from __future__ import annotations

from pathlib import Path


def runtime_asset_paths() -> tuple[Path, Path]:
    """Return ``(js_path, wasm_path)`` for packaged runtime assets."""
    package_dir = Path(__file__).resolve().parents[1]
    assets_dir = package_dir / "runtime_assets"
    js_path = assets_dir / "conda_wasm.js"
    wasm_path = assets_dir / "conda_wasm_bg.wasm"

    missing = [path for path in (js_path, wasm_path) if not path.exists()]
    if missing:
        missing_list = "\n".join(f"- {path}" for path in missing)
        raise FileNotFoundError(
            "conda-wasm runtime assets are missing:\n"
            f"{missing_list}\n"
            "Is conda-wasm installed with runtime assets? "
            "Rebuild with: pixi run -e demo demo-build-local"
        )

    return js_path, wasm_path
