"""Shared test fixtures for the build projects.

Each project's solution module doesn't exist until the learner writes it, so we
load it lazily by file path (no package imports, no __init__.py needed). A test
module opts in by declaring a module-level ``SOLUTION = "<file>.py"`` and taking
the ``solution`` fixture.
"""

import importlib.util
from pathlib import Path

import pytest


@pytest.fixture
def solution(request):
    """Load and return the solution module declared by the test module's SOLUTION."""
    filename = getattr(request.module, "SOLUTION", None)
    if filename is None:
        raise RuntimeError(
            f"{request.module.__name__} must declare SOLUTION = '<file>.py' "
            "to use the `solution` fixture."
        )

    path = Path(request.module.__file__).parent / filename
    if not path.exists():
        pytest.fail(f"Not implemented yet — create {filename} (see README.md)")

    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module