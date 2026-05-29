from __future__ import annotations

import logging
import sys
from email.parser import Parser

log = logging.getLogger(__name__)

IGNORED_REQUEST_HEADERS = {"user-agent"}


def patch_urllib3() -> None:
    """Route urllib3's Emscripten transport through synchronous XMLHttpRequest."""
    if sys.platform != "emscripten":
        return
    try:
        import urllib3.contrib.emscripten.fetch  # noqa: F401
    except ImportError:
        return

    import js
    import pyjs
    import urllib3.contrib.emscripten.connection as connection
    import urllib3.contrib.emscripten.fetch as fetch
    from urllib3.contrib.emscripten.response import EmscriptenResponse

    def send_request(request):
        headers = {
            key: value
            for key, value in request.headers.items()
            if key.lower() not in IGNORED_REQUEST_HEADERS
        }
        body = request.body
        if isinstance(body, bytes):
            body = body.decode("latin-1")

        xhr = js.XMLHttpRequest.new()
        xhr.open(request.method, request.url, False)
        xhr.responseType = "arraybuffer"
        for key, value in headers.items():
            xhr.setRequestHeader(key, value)
        xhr.send(body)

        return EmscriptenResponse(
            status_code=int(str(xhr.status)),
            headers=dict(Parser().parsestr(str(xhr.getAllResponseHeaders()))),
            body=bytes(pyjs.to_py(js.Uint8Array.new(xhr.response))),
            request=request,
        )

    fetch.send_request = send_request
    connection.send_request = send_request
    log.debug("conda-wasm: urllib3 patched (sync XHR)")
