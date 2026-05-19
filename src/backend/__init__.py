"""Backend package public API."""

from importlib import import_module
from typing import Any

__all__ = ["getMtps", "getProcedure", "control"]


def __getattr__(name: str) -> Any:
    if name == "getMtps":
        from .mtpparser import getMtps

        globals()[name] = getMtps
        return getMtps

    if name == "getProcedure":
        from .orchestration import getProcedure

        globals()[name] = getProcedure
        return getProcedure

    if name == "control":
        module = import_module(".control", __name__)
        globals()[name] = module
        return module

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
