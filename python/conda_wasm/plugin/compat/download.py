from __future__ import annotations

import hashlib
import logging
import time
from pathlib import Path

from conda_wasm.diagnostics import emit_timing

log = logging.getLogger(__name__)


def patch_download() -> None:
    """Patch conda downloads to avoid file seeking on Emscripten MEMFS."""
    import conda.gateways.connection.download as download
    from conda.base.context import context

    def download_inner(url, target_full_path, md5, sha256, size, progress_update_callback):
        start = time.perf_counter()
        session = download.get_session(url)
        response = session.get(
            url,
            proxies=session.proxies,
            timeout=(context.remote_connect_timeout_secs, context.remote_read_timeout_secs),
        )
        if log.isEnabledFor(logging.DEBUG):
            log.debug(download.stringify(response, content_max_len=256))
        response.raise_for_status()

        data = response.content
        verify_checksum(url, target_full_path, data, md5=md5, sha256=sha256)

        target = Path(target_full_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        emit_timing("download:", time.perf_counter() - start, url.rsplit("/", 1)[-1])

    download.download_inner = download_inner
    log.debug("conda-wasm: download_inner patched (no seek)")


def verify_checksum(url, target_full_path, data: bytes, *, md5, sha256) -> None:
    """Validate package bytes against the available conda checksum."""
    if not (sha256 or md5):
        from conda.exceptions import CondaError

        raise CondaError(
            f"Refusing unverified download without SHA256 or MD5 metadata: {url}"
        )

    checksum_type = "sha256" if sha256 else "md5"
    expected = sha256 if sha256 else md5
    actual = hashlib.new(checksum_type, data).hexdigest()
    if actual == expected:
        return

    from conda.exceptions import ChecksumMismatchError

    raise ChecksumMismatchError(
        url,
        str(target_full_path),
        checksum_type,
        expected,
        actual,
    )
