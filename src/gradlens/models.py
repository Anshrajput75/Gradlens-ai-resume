"""Typed data models shared by extraction, analysis, and reporting."""

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ResumeProfile:
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    sections: dict[str, list[str]] = field(default_factory=dict)
    skills: list[str] = field(default_factory=list)
    dates: list[str] = field(default_factory=list)
    word_count: int = 0
    source_file: str | None = None
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Score:
    name: str
    value: int
    rationale: str
    suggestions: list[str] = field(default_factory=list)


@dataclass
class ProgramMatch:
    term: str
    matched: bool
    evidence: str | None = None


@dataclass
class ResumeAnalysis:
    overall_score: int
    scores: list[Score]
    program_matches: list[ProgramMatch] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    disclaimer: str = (
        "This report evaluates resume evidence and document quality only. "
        "It does not predict admission or measure a person's potential."
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
