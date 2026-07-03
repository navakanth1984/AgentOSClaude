import json
from dataclasses import dataclass
from typing import Protocol, TypeVar, Any

T = TypeVar("T", contravariant=True)
U = TypeVar("U", covariant=True)

class CompilerError(Exception):
    """Base exception for all compilation failures."""
    pass

class ParserError(CompilerError):
    """Parser syntax failure (IR:PAR_001)."""
    pass

class CompilerStage(Protocol[T, U]):
    """Standard protocol contract that every compiler pipeline phase must implement."""
    def execute(self, input: T) -> U:
        ...

@dataclass(frozen=True, slots=True)
class ParsedIR:
    data: dict
    raw_source: str

class ParserStage(CompilerStage[str, ParsedIR]):
    def execute(self, input: str) -> ParsedIR:
        """Parse raw JSON string into a ParsedIR dataclass.
        
        Raises ParserError if the JSON layout is syntactically invalid.
        """
        try:
            data = json.loads(input)
            if not isinstance(data, dict):
                raise ParserError("Root of IR must be a JSON object.")
            return ParsedIR(data=data, raw_source=input)
        except json.JSONDecodeError as exc:
            raise ParserError(f"Malformed JSON layout: {exc}") from exc
