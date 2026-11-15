"""Render an Assessment as a Markdown memo or a self-contained HTML page."""

from __future__ import annotations

import html
from datetime import date

from . import __version__, doctrine
from .engine import Assessment
from .questions import BY_ID

DISCLAIMER = ("Structured research aid, not legal advice. Each conclusion depends on the inputs and on interpretive "
              "questions that WTO adjudicators decide case by case. Verify every citation against the original reports.")


def _authorities(a: Assessment) -> list[doctrine.Case]:
    seen, out = set(), []
    for s in a.steps:
        if s.status in ("skipped", "not_applicable"):
            continue
        for c in s.cases:
            if c not in seen:
                seen.add(c)
                out.append(doctrine.case(c))
    return out


def markdown(a: Assessment) -> str:
    m = a.measure
    lines = [f"# GATS analysis: {m.get('name') or 'Unnamed measure'}", ""]
    meta = [("Member", m.get("member")), ("Sector", m.get("sector")), ("Modes", ", ".join(m.get("modes", [])))]
    lines += [f"**{k}:** {v}  " for k, v in meta if v]
    if m.get("description"):
        lines += ["", m["description"]]
    lines += ["", "## Conclusion", "", f"**Risk of inconsistency: {a.risk}** · input completeness {a.completeness:.0%}", "",
              a.conclusion, ""]
    lines += ["## Step-by-step analysis", ""]
    for s in a.steps:
        lines.append(f"### {s.title} — {s.status_label}")
        lines += [f"- {f}" for f in s.findings]
        if s.status not in ("skipped", "not_applicable") and s.cases:
            lines.append("- *Authorities:* " + "; ".join(doctrine.case(c).cite(s.step) for c in s.cases))
        for q in s.missing:
            if q in BY_ID:
                lines.append(f"- *Missing:* {BY_ID[q].text}")
        note_ids = [q.id for q in BY_ID.values() if q.step == s.step and q.id in a.notes]
        for q in note_ids:
            lines.append(f"- *Note ({q}):* {a.notes[q]}")
        lines.append("")
    if a.open_questions:
        lines += ["## Open questions", ""] + [f"{i}. {q['question']} ({q['step']})" for i, q in enumerate(a.open_questions, 1)] + [""]
    if a.counterarguments:
        lines += ["## Likely counterarguments", ""] + [f"- {c}" for c in a.counterarguments] + [""]
    if a.notes.get("_scenario"):
        lines += ["## About these inputs", "", a.notes["_scenario"], ""]
    auth = _authorities(a)
    if auth:
        lines += ["## Authorities", ""] + [f"- [{c.cite()}]({c.url}): {c.holding}" for c in auth] + [""]
    if a.sources:
        lines += ["## Sources", ""] + [f"- [{s['label']}]({s['url']})" for s in a.sources] + [""]
    lines += ["---", f"*{DISCLAIMER}* Generated {date.today().isoformat()} with WTO–GATS Reasoning Engine {__version__}."]
    return "\n".join(lines)


RISK_COLORS = {"Low": "#1f7a3a", "Medium": "#8a5a00", "High": "#b42f2f"}
STATUS_CLASS = {"concern": "bad", "not_satisfied": "bad", "satisfied": "good", "no_concern": "good",
                "incomplete": "warn", "excluded": "muted", "not_applicable": "muted", "skipped": "muted", "info": "muted"}


def html_page(a: Assessment) -> str:
    e = html.escape
    m = a.measure
    meta = "".join(f"<div><dt>{k}</dt><dd>{e(v)}</dd></div>" for k, v in
                   [("Member", m.get("member")), ("Sector", m.get("sector")), ("Modes", ", ".join(m.get("modes", [])))] if v)
    steps = []
    for s in a.steps:
        items = "".join(f"<li>{e(f)}</li>" for f in s.findings)
        if s.status not in ("skipped", "not_applicable") and s.cases:
            items += "<li class=auth>Authorities: " + "; ".join(
                f'<a href="{e(doctrine.case(c).url)}">{e(doctrine.case(c).cite(s.step))}</a>' for c in s.cases) + "</li>"
        items += "".join(f"<li class=miss>Missing: {e(BY_ID[q].text)}</li>" for q in s.missing if q in BY_ID)
        items += "".join(f"<li class=note>Note: {e(a.notes[q.id])}</li>" for q in BY_ID.values()
                         if q.step == s.step and q.id in a.notes)
        steps.append(f"<section class='step {STATUS_CLASS.get(s.status, '')}'><h3>{e(s.title)}"
                     f"<span class=status>{e(s.status_label)}</span></h3><ul>{items}</ul></section>")
    openq = "".join(f"<li>{e(q['question'])} <span class=muted>({e(q['step'])})</span></li>" for q in a.open_questions)
    counter = "".join(f"<li>{e(c)}</li>" for c in a.counterarguments)
    auth = "".join(f'<li><a href="{e(c.url)}">{e(c.cite())}</a>: {e(c.holding)}</li>' for c in _authorities(a))
    sources = "".join(f'<li><a href="{e(s["url"])}">{e(s["label"])}</a></li>' for s in a.sources)
    about = f"<h2>About these inputs</h2><p>{e(a.notes['_scenario'])}</p>" if a.notes.get("_scenario") else ""
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>GATS analysis: {e(m.get('name') or 'measure')}</title>
<style>
:root{{--ink:#18202a;--muted:#5d6670;--line:#dfe2e6;--paper:#fbfbfa;--good:#1f7a3a;--bad:#b42f2f;--warn:#8a5a00}}
body{{margin:0;background:var(--paper);color:var(--ink);font:15px/1.6 Georgia,"Times New Roman",serif}}
main{{max-width:860px;margin:0 auto;padding:36px 20px 64px}} h1{{font-size:28px;line-height:1.2;margin:0 0 12px}}
h2{{font:600 18px system-ui,sans-serif;margin:32px 0 10px}} h3{{font:600 15px system-ui,sans-serif;margin:0 0 6px;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}}
dl{{display:grid;gap:4px;margin:0 0 12px;font:14px system-ui,sans-serif}} dl div{{display:flex;gap:8px}} dt{{color:var(--muted);min-width:70px}} dd{{margin:0}}
.conclusion{{border:1px solid var(--line);border-left:5px solid {RISK_COLORS[a.risk]};border-radius:8px;padding:14px 18px;background:#fff}}
.risk{{font:700 14px system-ui,sans-serif;color:{RISK_COLORS[a.risk]};text-transform:uppercase;letter-spacing:.05em}}
.step{{border:1px solid var(--line);border-left:4px solid var(--line);border-radius:8px;padding:12px 16px;margin:10px 0;background:#fff}}
.step.bad{{border-left-color:var(--bad)}} .step.good{{border-left-color:var(--good)}} .step.warn{{border-left-color:var(--warn)}}
.step.muted{{opacity:.75}} .status{{font-weight:500;font-size:13px;color:var(--muted)}}
.step.bad .status{{color:var(--bad)}} .step.good .status{{color:var(--good)}} .step.warn .status{{color:var(--warn)}}
ul{{margin:4px 0 0;padding-left:20px}} li{{margin:4px 0}} .auth,.note,.muted{{color:var(--muted);font-size:14px}} .miss{{color:var(--warn);font-size:14px}}
a{{color:#1d5fa8}} footer{{margin-top:36px;font-size:13px;color:var(--muted);border-top:1px solid var(--line);padding-top:12px}}
@media print{{.step{{break-inside:avoid}}}}
</style></head><body><main>
<h1>GATS analysis: {e(m.get('name') or 'Unnamed measure')}</h1>
<dl>{meta}</dl>{f"<p>{e(m['description'])}</p>" if m.get('description') else ""}
<div class=conclusion><div class=risk>Risk of inconsistency: {a.risk}</div><p>{e(a.conclusion)}</p>
<p class=muted>Input completeness {a.completeness:.0%}</p></div>
<h2>Step-by-step analysis</h2>{''.join(steps)}
{f"<h2>Open questions</h2><ol>{openq}</ol>" if openq else ""}
{f"<h2>Likely counterarguments</h2><ul>{counter}</ul>" if counter else ""}
{about}
{f"<h2>Authorities</h2><ul>{auth}</ul>" if auth else ""}
{f"<h2>Sources</h2><ul>{sources}</ul>" if sources else ""}
<footer>{e(DISCLAIMER)} Generated {date.today().isoformat()} with WTO–GATS Reasoning Engine {__version__}.</footer>
</main></body></html>"""
