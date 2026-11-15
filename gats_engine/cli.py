"""Command line.

    gats-engine examples                         # list bundled scenarios
    gats-engine assess eu_data_act_art5_gatekeepers
    gats-engine assess my_measure.json --format html --out memo.html
    gats-engine template > my_measure.json       # blank questionnaire
    gats-engine interview --out my_measure.json  # answer the questions one by one
"""

from __future__ import annotations

import argparse
import json
import sys
from importlib import resources
from pathlib import Path

from . import __version__
from .engine import assess
from .questions import QUESTIONS, STEPS, template
from .report import html_page, markdown


def scenario_names() -> list[str]:
    return sorted(p.name[:-5] for p in resources.files("gats_engine").joinpath("scenarios").iterdir()
                  if p.name.endswith(".json"))


def load_scenario(ref: str) -> dict:
    p = Path(ref)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    if ref in scenario_names():
        return json.loads(resources.files("gats_engine").joinpath("scenarios", f"{ref}.json").read_text(encoding="utf-8"))
    raise FileNotFoundError(f"No file or bundled scenario named '{ref}'. Try: gats-engine examples")


def _cmd_examples(a) -> int:
    for n in scenario_names():
        print(f"{n:<40} {load_scenario(n).get('title', '')}")
    return 0


def _cmd_assess(a) -> int:
    result = assess(load_scenario(a.scenario))
    if a.format == "json":
        text = json.dumps(result.to_dict(), indent=2, ensure_ascii=False)
    elif a.format == "html":
        text = html_page(result)
    else:
        text = markdown(result)
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
        print(f"{result.risk}: {result.conclusion}\nWritten to {a.out}")
    else:
        print(text)
    return 0


def _ask(q) -> object:
    print(f"\n{q.text}")
    if q.help:
        print(f"  ({q.help})")
    if q.kind == "text":
        return input("  > ").strip()
    if q.kind in ("choice", "multi"):
        for i, (key, label) in enumerate(q.options, 1):
            print(f"  {i}. {label}")
        raw = input("  number(s), comma-separated, empty = unknown > " if q.kind == "multi" else "  number, empty = unknown > ").strip()
        picks = [q.options[int(x) - 1][0] for x in raw.split(",") if x.strip().isdigit() and 0 < int(x) <= len(q.options)]
        return picks if q.kind == "multi" else (picks[0] if picks else "")
    raw = input("  [y]es / [n]o / [u]nknown > ").strip().lower()
    return {"y": "yes", "yes": "yes", "n": "no", "no": "no"}.get(raw, "unknown")


def _cmd_interview(a) -> int:
    scenario = template()
    current = None
    for q in QUESTIONS:
        if q.step != current:
            current = q.step
            print(f"\n=== {STEPS[q.step]} ===")
        scenario["answers"][q.id] = _ask(q)
    Path(a.out).write_text(json.dumps(scenario, indent=2, ensure_ascii=False), encoding="utf-8")
    result = assess(scenario)
    print(f"\n{result.risk}: {result.conclusion}\nSaved answers to {a.out}. Run: gats-engine assess {a.out} --format html --out memo.html")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="gats-engine", description="Structured GATS analysis of measures affecting trade in services.")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("examples", help="list bundled scenarios").set_defaults(func=_cmd_examples)
    pa = sub.add_parser("assess", help="analyse a scenario (JSON file or bundled name)")
    pa.add_argument("scenario")
    pa.add_argument("--format", choices=["md", "html", "json"], default="md")
    pa.add_argument("--out")
    pa.set_defaults(func=_cmd_assess)
    pt = sub.add_parser("template", help="print a blank questionnaire")
    pt.set_defaults(func=lambda a: (print(json.dumps(template(), indent=2)), 0)[1])
    pi = sub.add_parser("interview", help="answer the questionnaire interactively")
    pi.add_argument("--out", default="measure.json")
    pi.set_defaults(func=_cmd_interview)
    a = p.parse_args(argv)
    try:
        return a.func(a)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
