"""Browser bridge (Pyodide): JSON in, JSON out."""

import json

from gats_engine import assess
from gats_engine.report import html_page, markdown


def run(scenario_json: str) -> str:
    scenario = json.loads(scenario_json)
    result = assess(scenario)
    d = result.to_dict()
    d["memo_html"] = html_page(result)
    d["memo_md"] = markdown(result)
    return json.dumps(d, ensure_ascii=False)
