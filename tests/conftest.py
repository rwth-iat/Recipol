"""Shared dependency stubs for backend tests in minimal environments."""

import importlib.machinery
import importlib.util
import sys
from types import ModuleType, SimpleNamespace


if importlib.util.find_spec("asyncua") is None:
    asyncua = ModuleType("asyncua")
    asyncua.__spec__ = importlib.machinery.ModuleSpec("asyncua", loader=None)
    asyncua.Client = object
    asyncua.ua = SimpleNamespace(
        VariantType=SimpleNamespace(),
        DataValue=object,
        Variant=object,
    )
    sys.modules["asyncua"] = asyncua

if importlib.util.find_spec("xmlschema") is None:
    xmlschema = ModuleType("xmlschema")
    xmlschema.__spec__ = importlib.machinery.ModuleSpec("xmlschema", loader=None)
    xmlschema.validate = lambda *args, **kwargs: None
    sys.modules["xmlschema"] = xmlschema
