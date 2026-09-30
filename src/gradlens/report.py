"""Privacy-aware serialization and human-readable report rendering."""

from __future__ import annotations

import json
import re

from .models import ResumeAnalysis, ResumeProfile


def _redact(value: str | None, redact: bool) -> str | None:
    if value is None or not redact:
        return value
    if "@" in value:
        local, _, domain = value.partition("@")
        return f"{local[:1]}***@{domain}"
    digits = re.sub(r"\D", "", value)
    return "***" + digits[-4:] if digits else "[redacted]"


def profile_dict(profile: ResumeProfile, redact: bool = True) -> dict:
    data = profile.to_dict()
    data["email"] = _redact(profile.email, redact)
    data["phone"] = _redact(profile.phone, redact)
    return data


def render_markdown(profile: ResumeProfile, analysis: ResumeAnalysis, redact: bool = True) -> str:
    email = _redact(profile.email, redact) or "Not detected"
    phone = _redact(profile.phone, redact) or "Not detected"
    lines = [
        "# GradLens Resume Review", "",
        f"**Candidate:** {profile.name or 'Not detected'}  ",
        f"**Contact:** {email} · {phone}  ",
        f"**Source:** {profile.source_file or 'Text input'}  ",
        f"**Overall document score:** {analysis.overall_score}/100", "",
        "> " + analysis.disclaimer, "", "## Review dimensions", "",
        "| Dimension | Score | What was detected |", "|---|---:|---|",
    ]
    for score in analysis.scores:
        lines.append(f"| {score.name.title()} | {score.value}/100 | {score.rationale} |")
    lines.extend(["", "## Suggested edits", ""])
    for item in analysis.recommendations:
        lines.append(f"- {item}")
    for score in analysis.scores:
        for suggestion in score.suggestions:
            lines.append(f"- **{score.name.title()}:** {suggestion}")
    if analysis.program_matches:
        lines.extend(["", "## Program description coverage", "", "| Term | Resume evidence found? | Evidence location |", "|---|---|---|"])
        for item in analysis.program_matches:
            lines.append(f"| {item.term} | {'Yes' if item.matched else 'Review'} | {item.evidence or 'No matching text detected'} |")
        lines.extend(["", "Coverage is a keyword-based review aid, not a measure of academic fit or eligibility."])
    if profile.warnings:
        lines.extend(["", "## Parsing notes", ""])
        lines.extend(f"- {warning}" for warning in profile.warnings)
    lines.extend(["", "---", "Generated locally by GradLens. Verify extracted details before using this report.", ""])
    return "\n".join(lines)


def json_payload(profile: ResumeProfile, analysis: ResumeAnalysis, redact: bool = True) -> str:
    return json.dumps({"profile": profile_dict(profile, redact), "analysis": analysis.to_dict()}, indent=2, ensure_ascii=False)
