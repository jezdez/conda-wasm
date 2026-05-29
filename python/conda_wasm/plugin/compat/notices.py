from __future__ import annotations


def disable_outdated_conda_notice() -> None:
    """Disable conda's outdated-version notification in browser environments."""
    from conda.core import solve

    solve.Solver._notify_conda_outdated = lambda self, link_precs: None
