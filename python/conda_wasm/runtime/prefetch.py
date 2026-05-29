from __future__ import annotations

import json
import os
import sys

DEFAULT_CHANNELS = [
    {
        "url": "https://repo.prefix.dev/emscripten-forge-4x",
        "subdirs": ["emscripten-wasm32", "noarch"],
    },
    {
        "url": "https://conda.anaconda.org/conda-forge",
        "subdirs": ["emscripten-wasm32", "noarch"],
    },
]


async def prefetch_installed() -> None:
    """Pre-warm sharded repodata for installed package dependencies."""
    import js  # noqa: PLC0415

    conda_meta = os.path.join(sys.prefix, "conda-meta")
    if not os.path.isdir(conda_meta):
        return

    seeds: set[str] = set()
    for filename in os.listdir(conda_meta):
        if not filename.endswith(".json"):
            continue
        try:
            with open(os.path.join(conda_meta, filename)) as f:
                data = json.load(f)
        except Exception:  # noqa: BLE001
            continue
        if name := data.get("name"):
            seeds.add(name)

    if not seeds:
        return

    try:
        print(f"[conda-wasm-prefetch] starting for {len(seeds)} installed packages")
        total_fetched = 0
        seen_names: set[str] = set()
        seen_urls: set[str] = set()
        queue = sorted(seeds)
        level = 0

        while queue:
            new_names = [name for name in queue if name not in seen_names]
            if not new_names:
                break
            seen_names.update(new_names)

            request = json.dumps({"channels": DEFAULT_CHANNELS, "seeds": new_names})
            urls_js = js.get_shard_urls(request)
            urls = json.loads(str(js.JSON.stringify(urls_js)))
            new_urls = [url for url in urls if url not in seen_urls]
            seen_urls.update(new_urls)
            if not new_urls:
                break

            print(f"[conda-wasm-prefetch] level {level}: {len(new_urls)} shards")
            await js.condaWasmPrefetchBatch(json.dumps(new_urls))
            total_fetched += len(new_urls)

            next_names: set[str] = set()
            for url in new_urls:
                shard_bytes = js.condaWasmPrefetchCache.get(url)
                if not shard_bytes:
                    continue
                deps_js = js.decode_shard_deps(shard_bytes)
                next_names.update(json.loads(str(js.JSON.stringify(deps_js))))

            queue = sorted(next_names - seen_names)
            level += 1

        print(f"[conda-wasm-prefetch] done: {total_fetched} shards across {level} levels")
    except Exception as exc:  # noqa: BLE001
        print(f"[conda-wasm-prefetch] FAILED: {type(exc).__name__}: {exc}")
        import traceback  # noqa: PLC0415

        traceback.print_exc()
