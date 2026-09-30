"""Explainable resume quality and program-evidence analysis."""

from __future__ import annotations

import re

from .models import ProgramMatch, ResumeAnalysis, ResumeProfile, Score

_ACTION_VERBS = re.compile(
    r"\b(achieved|analyzed|analysed|built|conducted|created|designed|developed|"
    r"improved|implemented|launched|led|mentored|published|reduced|researched|"
    r"streamlined|validated|wrote)\b",
    re.I,
)
_NUMBER = re.compile(r"(?:\b\d+(?:\.\d+)?%?\b|\$\s?\d+|\b\d+x\b)", re.I)
_STOPWORDS = {
    "about", "after", "also", "among", "and", "are", "for", "from", "have", "into",
    "its", "more", "our", "program", "students", "that", "the", "their", "this", "through",
    "with", "will", "your", "you", "such", "which", "who", "while", "using", "based",
    "across", "including", "work", "experience", "research", "study", "degree", "course",
    "applicant", "applicants", "application", "applications", "artificial", "combine",
    "combines", "programs", "program", "students", "student", "university", "universities",
}
_WEIGHTS = {"completeness": 0.30, "evidence": 0.30, "impact": 0.25, "readability": 0.15}


def _score(name: str, value: float, rationale: str, suggestions: list[str]) -> Score:
    return Score(name=name, value=max(0, min(100, round(value))), rationale=rationale, suggestions=suggestions)


def _program_terms(description: str) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9+#.-]{2,}", description.lower())
    counts: dict[str, int] = {}
    for word in words:
        if word not in _STOPWORDS and not word.isdigit():
            counts[word] = counts.get(word, 0) + 1
    return [term for term, _ in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:20]]


def analyze(profile: ResumeProfile, program_description: str | None = None) -> ResumeAnalysis:
    content = "\n".join(line for rows in profile.sections.values() for line in rows)
    all_text = " ".join([profile.name or "", content, " ".join(profile.skills)])
    bullet_count = sum(len(rows) for rows in profile.sections.values())
    quantified = len(_NUMBER.findall(content))
    verbs = len(_ACTION_VERBS.findall(content))
    populated = sum(bool(profile.sections.get(section)) for section in ("education", "experience", "research", "projects", "skills", "publications", "awards"))

    completeness = _score(
        "completeness", populated / 7 * 100,
        f"{populated} of 7 commonly useful graduate CV sections were detected.",
        ["Add only sections relevant to your background: education, research/experience, projects, skills, publications, and awards."],
    )
    evidence = _score(
        "evidence", min(100, quantified * 18 + min(bullet_count, 8) * 4),
        f"Detected {quantified} numeric detail(s) across {bullet_count} content line(s).",
        ["Where accurate, state scale, method, output, or result so readers can assess the work."],
    )
    impact = _score(
        "impact", min(100, verbs * 12 + min(bullet_count, 8) * 3),
        f"Found {verbs} action-verb signal(s) in the resume text.",
        ["Start experience bullets with a precise action and explain your contribution; avoid claiming outcomes you cannot support."],
    )
    if profile.word_count < 250:
        readability_value, readability_note = 55, "Short resumes can be appropriate; confirm relevant evidence was not omitted."
    elif profile.word_count <= 1200:
        readability_value, readability_note = 90, "The extracted length is within a practical review range; visual layout is not evaluated."
    else:
        readability_value, readability_note = 65, "The extracted text is lengthy; check focus and repetition against program expectations."
    readability = _score("readability", readability_value, f"{profile.word_count} words. {readability_note}", [])
    scores = [completeness, evidence, impact, readability]
    overall = round(sum(score.value * _WEIGHTS[score.name] for score in scores))

    matches = []
    if program_description:
        searchable = all_text.lower()
        section_names = [key for key, rows in profile.sections.items() if rows]
        for term in _program_terms(program_description):
            found = term in searchable
            evidence_label = None
            if found:
                evidence_label = next((section for section in section_names if term in " ".join(profile.sections[section]).lower()), None)
                evidence_label = evidence_label or ("skills" if term in " ".join(profile.skills).lower() else "profile text")
            matches.append(ProgramMatch(term=term, matched=found, evidence=evidence_label))

    recommendations = []
    if not profile.sections.get("education"):
        recommendations.append("Add or verify an Education section with degree, institution, dates, and relevant academic distinctions.")
    if not (profile.sections.get("research") or profile.sections.get("experience")):
        recommendations.append("Add relevant research, employment, or academic experience when applicable.")
    if quantified == 0:
        recommendations.append("Review bullets for places where accurate counts, scope, methods, or outcomes would make the work clearer.")
    if program_description and matches:
        unmatched = [item.term for item in matches if not item.matched]
        if unmatched:
            recommendations.append("Review program terms not visible in the resume and add supporting evidence only where it reflects real experience: " + ", ".join(unmatched[:6]) + ".")
    recommendations.append("Tailor emphasis to the program's published priorities, then verify every parsed detail and requirement yourself.")
    return ResumeAnalysis(overall_score=overall, scores=scores, program_matches=matches, recommendations=recommendations)
