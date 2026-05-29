from __future__ import annotations

import logging

log = logging.getLogger(__name__)


def patch_subprocess() -> None:
    """Skip conda post-link subprocesses, which are unavailable in the browser."""
    import conda.gateways.subprocess as subprocess_gateway

    def any_subprocess(args, prefix, env=None, cwd=None):
        log.debug("conda-wasm: skipping subprocess: %s", args)
        return "", "", 0

    def subprocess_call(
        command,
        env=None,
        path=None,
        stdin=None,
        raise_on_error=True,
        capture_output=True,
    ):
        log.debug("conda-wasm: skipping subprocess_call: %s", command)
        return subprocess_gateway.Response("", "", 0)

    subprocess_gateway.any_subprocess = any_subprocess
    subprocess_gateway.subprocess_call = subprocess_call
    log.debug("conda-wasm: subprocess patched (no-op)")
