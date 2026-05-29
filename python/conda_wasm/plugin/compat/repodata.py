from __future__ import annotations


def patch_repodata_cache() -> None:
    """Ignore cache-save failures from Emscripten MEMFS edge cases."""
    from conda.gateways.repodata import RepodataCache

    original_save = RepodataCache.save

    def save_without_memfs_errors(self, raw_repodata):
        try:
            return original_save(self, raw_repodata)
        except (AttributeError, OSError):
            return None

    RepodataCache.save = save_without_memfs_errors
