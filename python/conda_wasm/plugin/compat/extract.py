from __future__ import annotations

import json
import logging
import time
from os.path import basename, getsize, join, lexists

from conda_wasm.diagnostics import emit_timing

from ..extractor import extract_wasm

log = logging.getLogger(__name__)


def patch_extraction() -> None:
    """Patch conda package extraction to use conda-wasm's streaming extractor."""
    from conda.core.path_actions import ExtractPackageAction

    def execute(self, progress_update_callback=None):
        start = time.perf_counter()
        extract_package_action(self)
        emit_timing("extract:", time.perf_counter() - start, basename(self.source_full_path))

    ExtractPackageAction.execute = execute
    log.debug("conda-wasm: ExtractPackageAction.execute patched (WASM extractor)")


def extract_package_action(action) -> None:
    """Execute conda's package extraction bookkeeping around the WASM extractor."""
    from conda.base.context import context
    from conda.common.url import has_platform
    from conda.core.package_cache_data import PackageCacheData
    from conda.gateways.disk.create import write_as_json_to_file
    from conda.gateways.disk.delete import rm_rf
    from conda.gateways.disk.read import compute_sum, read_index_json
    from conda.models.channel import Channel
    from conda.models.match_spec import MatchSpec
    from conda.models.records import PackageCacheRecord, PackageRecord

    log.debug(
        "conda-wasm: extracting %s -> %s (WASM)",
        action.source_full_path,
        action.target_full_path,
    )
    if lexists(action.target_full_path):
        rm_rf(action.target_full_path)

    extract_wasm(action.source_full_path, action.target_full_path)

    try:
        raw_index_json = read_index_json(action.target_full_path)
    except (OSError, json.JSONDecodeError, FileNotFoundError):
        print(f"ERROR: corrupt package tarball at {action.source_full_path}.")
        return

    if isinstance(action.record_or_spec, MatchSpec):
        url = action.record_or_spec.get_raw_value("url")
        if not url:
            raise ValueError("URL cannot be empty.")
        channel = Channel(url) if has_platform(url, context.known_subdirs) else Channel(None)
        repodata_record = PackageRecord.from_objects(
            raw_index_json,
            url=url,
            channel=channel,
            fn=basename(url),
            sha256=action.sha256 or compute_sum(action.source_full_path, "sha256"),
            size=getsize(action.source_full_path),
            md5=action.md5 or compute_sum(action.source_full_path, "md5"),
        )
    else:
        repodata_record = PackageRecord.from_objects(action.record_or_spec, raw_index_json)

    write_as_json_to_file(
        join(action.target_full_path, "info", "repodata_record.json"),
        repodata_record,
    )

    target_package_cache = PackageCacheData(action.target_pkgs_dir)
    package_cache_record = PackageCacheRecord.from_objects(
        repodata_record,
        package_tarball_full_path=action.source_full_path,
        extracted_package_dir=action.target_full_path,
    )
    target_package_cache.insert(package_cache_record)
