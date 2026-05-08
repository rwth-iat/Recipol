"""Backward-compatible public API for MTP parsing."""

from .mtp_models import (
    HMI,
    Instance,
    Junction,
    Line,
    Pea,
    Pipe,
    Port,
    Procedure,
    Service,
    Sink,
    Source,
    VisualObject,
)
from .mtp_parser import NAMESPACE, TESTMTP1, TESTMTP2, TESTMTPS, getMtps
from .mtp_units import UNIT_MAP, getUnit

__all__ = [
    "Instance",
    "Procedure",
    "Service",
    "Port",
    "VisualObject",
    "Junction",
    "Source",
    "Sink",
    "Pipe",
    "Line",
    "HMI",
    "Pea",
    "UNIT_MAP",
    "getUnit",
    "NAMESPACE",
    "TESTMTP1",
    "TESTMTP2",
    "TESTMTPS",
    "getMtps",
]
