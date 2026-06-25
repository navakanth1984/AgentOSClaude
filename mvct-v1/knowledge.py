"""Knowledge seam. The interface survives for future graph/ontology/retrieval
providers; the V1 implementation is static.

The leak_blocklist deliberately includes the detector's MIMICRY_KEYWORDS plant
terms (water, soil, light, ...). Blocking the tutor from naming these while locked
ALSO protects the detector's self-initiated-decomposition signal from contamination.
"""
from typing import Protocol


class KnowledgeProvider(Protocol):
    def scenario_prompt(self) -> str: ...
    def canonical_answer(self) -> str: ...
    def canonical_independent_variables(self) -> list[str]: ...
    def leak_blocklist(self) -> list[str]: ...


class HouseplantKnowledgeProvider:
    """Static V1 provider. Domain is MANDATORY (in-distribution constraint for the
    validated detector), not a default — see spec section 2.2. Do not swap the topic."""

    _VARIABLES = [
        "water", "moisture", "overwatering", "underwatering",
        "light", "sun", "shade",
        "soil", "drainage", "pot", "roots", "root rot",
        "nutrients", "fertilizer",
        "pests", "disease",
        "temperature", "humidity",
    ]

    def scenario_prompt(self) -> str:
        return (
            "Your houseplant is wilting and its leaves are yellowing. "
            "Figure out why your houseplant is dying."
        )

    def canonical_answer(self) -> str:
        return (
            "The likely cause is overwatering leading to root rot: soggy soil with poor "
            "drainage starves the roots of oxygen. Let the soil dry out, check drainage, "
            "and inspect the roots for rot."
        )

    def canonical_independent_variables(self) -> list[str]:
        return list(self._VARIABLES)

    def leak_blocklist(self) -> list[str]:
        return self._VARIABLES + ["root rot", "overwatering", "poor drainage"]
