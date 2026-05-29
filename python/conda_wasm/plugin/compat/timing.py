from __future__ import annotations

import logging
import time

from conda_wasm.diagnostics import emit_timing, timing_enabled

log = logging.getLogger(__name__)


def patch_timing() -> None:
    """Install optional conda phase timing wrappers."""
    if not timing_enabled():
        return

    from conda.core.link import UnlinkLinkTransaction

    from ..solver import CondaWasmSolver

    original_solve = CondaWasmSolver.solve_final_state
    original_transaction_execute = UnlinkLinkTransaction.execute

    def solve_final_state(self, *args, **kwargs):
        start = time.perf_counter()
        result = original_solve(self, *args, **kwargs)
        emit_timing("solve:", time.perf_counter() - start)
        return result

    def execute_transaction(self):
        start = time.perf_counter()
        result = original_transaction_execute(self)
        emit_timing("transaction:", time.perf_counter() - start)
        return result

    CondaWasmSolver.solve_final_state = solve_final_state
    UnlinkLinkTransaction.execute = execute_transaction
    log.debug("conda-wasm: timing wrappers installed")
