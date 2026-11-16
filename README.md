# WTO–GATS Reasoning Engine

[![tests](https://github.com/AlirezaMahdavishirkharkolaei/wto-gats-reasoning-engine/actions/workflows/tests.yml/badge.svg)](https://github.com/AlirezaMahdavishirkharkolaei/wto-gats-reasoning-engine/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**An open, explainable tool for structuring legal analysis under the WTO General Agreement on Trade in Services (GATS).**

You describe a regulatory measure by answering a questionnaire. The engine walks it through the analytical sequence developed in WTO jurisprudence and returns a reasoning trace with the provisions and disputes behind each step. It also reports the facts you still need to establish and the arguments the other side is likely to raise.

It is a research and teaching aid. It does not automate legal conclusions. Unanswered questions are reported as information gaps, never guessed.

## The analysis

| Step | What the engine checks |
|---|---|
| 1. Scope (Art. I) | Measure by a Member affecting trade in services; modes of supply; the governmental-authority exclusion |
| 2. MFN (Art. II) | Less favourable treatment between foreign Members, de jure or de facto; Art. II exemptions; Art. V |
| 3. Commitments | Whether the sector and mode are committed, "Unbound" entries, inscribed limitations |
| 4. Market access (Art. XVI) | The exhaustive six measure types of XVI:2, including the "zero quota" (*US – Gambling*) |
| 5. National treatment (Art. XVII) | Likeness (presumed for origin-based distinctions) and modification of the conditions of competition (*Argentina – Financial Services*) |
| 6. Domestic regulation (Art. VI) | Licensing, qualification and technical standards; the 2021 Reference Paper |
| 7. General exceptions (Art. XIV) | The closed list of paragraphs (a)–(e); public-order footnote 5; GATS-consistent laws under (c); design; necessity as weighing and balancing, including a reasonably available alternative |
| 8. Chapeau | Arbitrary or unjustifiable discrimination; disguised restriction |
| 9. Security (Art. XIV bis) | The XIV bis:1(b) categories and the good-faith plausibility review (*Russia – Traffic in Transit*, by analogy) |
| 10. Prudential carve-out | Annex on Financial Services, para. 2(a) |

The engine gives each step a status: *issue indicated*, *no issue*, *not applicable*, *information missing*, *requirement met / not met*, or *not reached*. The overall **risk of inconsistency** works as follows:

* **Low:** no prima facie inconsistency, or one with a defence that appears available.
* **Medium:** the outcome depends on missing facts.
* **High:** a prima facie inconsistency and no available defence.

## Try it

**In the browser (no installation):** the web app in `web/` runs the same Python engine with Pyodide. Your inputs never leave your browser.

* Build it locally with `python scripts/build_web.py`.
* Once GitHub Pages is enabled it is published at `https://alirezamahdavishirkharkolaei.github.io/wto-gats-reasoning-engine/`.

**On the command line** (Python 3.10+, no dependencies):

```bash
pip install git+https://github.com/AlirezaMahdavishirkharkolaei/wto-gats-reasoning-engine
gats-engine examples                                   # bundled scenarios
gats-engine assess eu_data_act_art5_gatekeepers        # Markdown memo
gats-engine assess us_gambling_remote_betting --format html --out memo.html
gats-engine template > my_measure.json                 # blank questionnaire to fill in
gats-engine interview --out my_measure.json            # or answer question by question
gats-engine assess my_measure.json --format json
```

**From Python:**

```python
from gats_engine import assess
result = assess({"answers": {"s_measure": "yes", "s_affects": "yes", "c_committed": "yes", "ma_types": ["f"], ...}})
print(result.risk, result.conclusion)
for step in result.steps:
    print(step.title, step.status_label, step.findings)
```

## Bundled scenarios

| Scenario | Purpose |
|---|---|
| `us_gambling_remote_betting` | **Validation.** Reproduces the outcome of *US – Gambling* (DS285): XVI violation, provisional justification under XIV(a), failure of the chapeau |
| `data_localisation_cloud` | Hypothetical data-localisation requirement for cloud services |
| `telecom_foreign_equity_cap` | Hypothetical 49% foreign-equity cap (XVI:2(f)) |
| `eu_data_act_art5_gatekeepers` | EU Data Act Art. 5(3): DMA gatekeepers excluded as eligible third parties (de facto national treatment) |
| `eu_data_act_art32_governmental_access` | EU Data Act Art. 32: safeguards against third-country governmental access to non-personal data |
| `eu_data_act_art35_interoperability` | EU Data Act Art. 35: interoperability requirements as technical standards (Art. VI) |

The Data Act scenarios are **illustrative inputs for research discussion**. Each answer carries a note explaining the assumption behind it, and assumed Schedule entries must be checked against the EU's consolidated schedule. They are based on Regulation (EU) 2023/2854 as adopted. Amendments have since been proposed, so check the current text.

## Research context

The tool relates to a doctoral research proposal and a research article by the author on the compatibility of EU digital regulation, in particular the Data Act, with the GATS. It makes that analytical pathway explicit and testable:

* Which assumptions decide the outcome? For Art. 5(3), likeness of gatekeepers and other data-service providers.
* Which Article XIV paragraph, if any, can carry the EU's objectives?
* Where does the burden of proof shift between the parties?

## Design choices

* **Doctrine as data:** provisions and authorities live in [`doctrine.py`](gats_engine/doctrine.py), and the questions in [`questions.py`](gats_engine/questions.py). The CLI, the web form and the JSON template are all generated from these files.
* **No guessing:** "unknown" is a first-class answer. It produces *information missing* and an open question, never a silent default.
* **Validated against a real dispute:** the *US – Gambling* scenario is a test case.
* **Citations:** pinpoint paragraphs are given only where checked. All dispute links point to the WTO's case pages.

See [docs/methodology.md](docs/methodology.md) for the decision rules of every step.

## Limitations

* The questions are simplified proxies. Likeness, necessity and the chapeau are holistic, case-specific assessments, so the engine structures them but does not decide them.
* Several authorities are GATT Article XX/XXI reports applied by analogy, as is common in GATS analysis.
* Whether a sector is committed depends on scheduling and classification questions (W/120, CPC, technological neutrality) that the engine records but does not resolve.
* Not legal advice.

## Collaboration

**Mohammad Amir Modami** collaborated on the legal analysis and research behind this project.

## Citation

Use GitHub's "Cite this repository" button, which reads [CITATION.cff](CITATION.cff).

## License

[MIT](LICENSE)
