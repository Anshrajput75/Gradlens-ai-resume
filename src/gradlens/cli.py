"""Command-line interface for GradLens."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .analyzer import analyze
from .parser import parse_file
from .report import json_payload, profile_dict, render_markdown


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gradlens", description="Parse a resume and create an explainable graduate application review.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    parse_cmd = subparsers.add_parser("parse", help="Extract a normalized profile")
    parse_cmd.add_argument("resume", type=Path)
    parse_cmd.add_argument("--out", type=Path, help="Output JSON file (defaults to stdout)")
    parse_cmd.add_argument("--no-redact", action="store_true", help="Include contact information in local output")
    analyze_cmd = subparsers.add_parser("analyze", help="Analyze resume evidence and optional program alignment")
    analyze_cmd.add_argument("resume", type=Path)
    analyze_cmd.add_argument("--program", type=Path, help="Plain-text program description")
    analyze_cmd.add_argument("--out", type=Path, default=Path("reports"), help="Output directory (default: reports)")
    analyze_cmd.add_argument("--no-redact", action="store_true", help="Include contact information in local reports")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        profile = parse_file(args.resume)
        redact = not args.no_redact
        if args.command == "parse":
            output = __import__("json").dumps(profile_dict(profile, redact), indent=2, ensure_ascii=False)
            if args.out:
                args.out.parent.mkdir(parents=True, exist_ok=True)
                args.out.write_text(output + "\n", encoding="utf-8")
                print(f"Profile saved to {args.out}")
            else:
                print(output)
            return 0

        program_text = None
        if args.program:
            if not args.program.is_file():
                raise FileNotFoundError(f"Program description not found: {args.program}")
            program_text = args.program.read_text(encoding="utf-8-sig")
        analysis = analyze(profile, program_text)
        args.out.mkdir(parents=True, exist_ok=True)
        md_path = args.out / "analysis.md"
        json_path = args.out / "profile.json"
        md_path.write_text(render_markdown(profile, analysis, redact), encoding="utf-8")
        json_path.write_text(json_payload(profile, analysis, redact) + "\n", encoding="utf-8")
        print(f"Analysis saved to {md_path}\nStructured profile saved to {json_path}")
        return 0
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"gradlens: error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
