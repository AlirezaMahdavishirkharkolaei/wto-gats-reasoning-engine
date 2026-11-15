"""Build the browser app into web/dist/ (static files; runs the engine with Pyodide).

    python scripts/build_web.py
    python -m http.server -d web/dist 8000
"""

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB, DIST = ROOT / "web", ROOT / "web" / "dist"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(WEB))

from gats_engine import __version__, questions  # noqa: E402
from gats_engine.cli import load_scenario, scenario_names  # noqa: E402
import bridge  # noqa: E402


def main() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    bundle = {}
    for f in sorted((ROOT / "gats_engine").rglob("*")):
        if f.is_file() and f.suffix in (".py", ".json") and "__pycache__" not in f.parts:
            bundle[str(f.relative_to(ROOT))] = f.read_text(encoding="utf-8")
    bundle["bridge.py"] = (WEB / "bridge.py").read_text(encoding="utf-8")
    examples = []
    for n in scenario_names():
        sc = load_scenario(n)
        examples.append({"id": n, "title": sc.get("title", n), "scenario": sc,
                         "result": json.loads(bridge.run(json.dumps(sc)))})
    data = {"version": __version__, "questions": questions.as_dict(), "steps": questions.STEPS,
            "examples": examples, "template": questions.template()}
    (DIST / "bundle.json").write_text(json.dumps(bundle), encoding="utf-8")
    (DIST / "data.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    shutil.copy2(WEB / "index.html", DIST / "index.html")
    size = sum(p.stat().st_size for p in DIST.iterdir())
    print(f"Built {DIST}: {len(bundle)} code files, {len(examples)} examples, {size / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
