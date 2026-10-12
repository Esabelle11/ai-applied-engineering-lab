"""Advertised provider capabilities; do not silently downgrade."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProviderCapabilities:
    synchronous_generation: bool = True
    structured_output: bool = False
    streaming: bool = False
    tools: bool = False
