# GradLens — AI Resume Parser & Graduate Application Analyzer

**Turn a resume into a clear, evidence-based application improvement plan.** GradLens extracts structured information from PDF, DOCX, or plain text resumes, evaluates document quality with transparent heuristics, and compares the evidence in a candidate profile with a program description. It is designed as a practical, privacy-first portfolio project for graduate applicants.

> GradLens is an advising aid, not an admissions predictor. It does not estimate the chance of admission, rank applicants, infer protected traits, or replace a university's published requirements or a human adviser. Its scores describe resume evidence and document readiness only.

## What it does

- Parses contact details, education, experience, projects, skills, publications, awards, and dates into a normalized profile.
- Reads `.txt` out of the box; PDF and DOCX support are optional extras.
- Scores resume completeness, evidence, impact, and readability using visible, configurable rules.
- Matches profile evidence to a user-provided program description and labels each match with supporting resume evidence.
- Produces a privacy-conscious Markdown report and machine-readable JSON.
- Runs locally; no account, API key, cloud upload, or LLM is required.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -e .
python -m gradlens --help
```

For PDFs and Word documents, install the corresponding extra:

```bash
python -m pip install -e ".[all]"
```

Analyze a resume and compare it with a program description:

```bash
gradlens analyze examples/sample_resume.txt \
  --program examples/program_description.txt \
  --out reports
```

The command writes `reports/analysis.md` and `reports/profile.json`. Reports are ignored by Git by default so personal data is not accidentally committed. Use `--no-redact` only when you intentionally want contact information in a local report.

Extract just the normalized profile:

```bash
gradlens parse examples/sample_resume.txt --out profile.json
```

Run without installation:

```bash
python -m gradlens analyze examples/sample_resume.txt --program examples/program_description.txt --out reports
```

## Example

The `examples/` directory contains an entirely fictional resume and a sample graduate program description. Try the quick-start command to see the report format. The included example is illustrative and is not an admissions evaluation.

## How the analysis works

1. **Ingestion:** extension-aware readers extract text locally. Scanned PDFs need OCR before GradLens can process them.
2. **Structuring:** section headers, dates, email, phone, and skill phrases are extracted with deterministic rules. Extraction is intentionally inspectable and may need human correction.
3. **Resume review:** four 0–100 subscores reflect completeness, quantified evidence, impact language, and length/readability. The overall score is their weighted average. This is a writing checklist, not a measure of applicant quality.
4. **Program alignment:** program-description terms are compared against resume text and skills. Each matched term links to a section or skill as evidence. Missing terms are prompts to review, not claims that the applicant lacks a qualification.
5. **Reporting:** a Markdown report provides actionable edits; JSON supports downstream workflows.

No model is called in this version. The name “AI” describes the project category and extension path, not a claim that this baseline runs a generative model. This keeps the default explainable, reproducible, and private; a future optional model adapter should require explicit opt-in, disclose data handling, and preserve evidence citations.

## Project layout

```text
src/gradlens/
  cli.py          Command-line interface
  parser.py       File readers and resume section extraction
  analyzer.py     Transparent scoring and program alignment
  models.py       Typed profile and analysis data structures
  report.py       Markdown and JSON serialization
examples/         Fictional input documents
```

## Limitations and responsible use

- PDF text extraction cannot read image-only/scanned PDFs; OCR is outside this baseline.
- Resume layouts vary. Review every parsed field before relying on it.
- Program descriptions can contain ambiguous or broad terms; keyword coverage is not academic fit.
- Scores are not calibrated against admissions outcomes and must not be used to rank, screen, or make decisions about people.
- Do not upload sensitive documents to services you have not reviewed. Keep generated reports out of version control.
- Do not use the tool to fabricate credentials or add keywords unsupported by your actual experience.

## Roadmap

- [ ] Editable field-level review workflow
- [ ] Additional international date, degree, and CV conventions
- [ ] Optional, opt-in semantic matching adapter with evidence citations
- [ ] OCR plugin with explicit local processing controls
- [ ] Configurable rubrics for research, course-based, and professional programs

## Development

```bash
python -m pip install -e ".[dev,all]"
ruff check src
python -m gradlens analyze examples/sample_resume.txt --program examples/program_description.txt --out reports
```

## License

MIT. See [LICENSE](LICENSE).
