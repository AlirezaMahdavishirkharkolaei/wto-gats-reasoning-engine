"""The questionnaire: every fact the engine can reason with.

Questions are data, so the command line, the web form and the JSON template
are all generated from this one list. Answers are "yes", "no" or "unknown"
(``kind="ynu"``), one option (``"choice"``), several options (``"multi"``) or
free text (``"text"``). Anything left unanswered counts as unknown, and
unknowns are reported as information gaps rather than guessed.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Question:
    id: str
    step: str
    text: str
    help: str = ""
    kind: str = "ynu"
    options: tuple[tuple[str, str], ...] = ()
    provision: str = ""
    cases: tuple[str, ...] = ()


STEPS = {
    "measure": "Measure",
    "scope": "1. Scope (Article I)",
    "mfn": "2. Most-favoured-nation treatment (Article II)",
    "commitments": "3. Specific commitments (Schedule)",
    "market_access": "4. Market access (Article XVI)",
    "national_treatment": "5. National treatment (Article XVII)",
    "domestic_regulation": "6. Domestic regulation (Article VI)",
    "exceptions": "7. General exceptions (Article XIV)",
    "chapeau": "8. Chapeau of Article XIV",
    "security": "9. Security exceptions (Article XIV bis)",
    "prudential": "10. Prudential carve-out (financial services)",
}

MODES = (("mode1", "Mode 1 – cross-border supply"), ("mode2", "Mode 2 – consumption abroad"),
         ("mode3", "Mode 3 – commercial presence"), ("mode4", "Mode 4 – presence of natural persons"))

XVI2 = (("a", "(a) limits on the number of service suppliers (incl. monopolies, exclusive suppliers)"),
        ("b", "(b) limits on the total value of service transactions or assets"),
        ("c", "(c) limits on the total number of service operations or quantity of output"),
        ("d", "(d) limits on the total number of natural persons employed"),
        ("e", "(e) measures restricting or requiring specific types of legal entity or joint venture"),
        ("f", "(f) limits on the participation of foreign capital"))

XIV_PARAGRAPHS = (("a_morals", "(a) protect public morals"),
                  ("a_order", "(a) maintain public order"),
                  ("b", "(b) protect human, animal or plant life or health"),
                  ("c_fraud", "(c)(i) prevent deceptive and fraudulent practices / default on contracts"),
                  ("c_privacy", "(c)(ii) protect privacy of individuals (personal data, confidentiality of records)"),
                  ("c_safety", "(c)(iii) safety"),
                  ("c_other", "(c) secure compliance with other GATS-consistent laws or regulations"),
                  ("d", "(d) equitable or effective direct taxation (only Article XVII)"),
                  ("e", "(e) double taxation agreements (only Article II)"),
                  ("none", "None of these – the objective is not listed (e.g. industrial policy, innovation, competitiveness)"))

QUESTIONS: list[Question] = [
    # --- measure (descriptive) ---
    Question("name", "measure", "Name of the measure", kind="text"),
    Question("member", "measure", "WTO Member adopting the measure", kind="text"),
    Question("description", "measure", "Short description of what the measure requires or prohibits", kind="text"),
    Question("sector", "measure", "Service sector (with W/120 or CPC reference if known)", kind="text",
             help="e.g. 'Computer and related services (W/120 1.B; CPC 84)'"),
    Question("modes", "measure", "Modes of supply affected", kind="multi", options=MODES, provision="I"),

    # --- scope ---
    Question("s_measure", "scope", "Is it a measure by a WTO Member (any level of government, or a body exercising delegated governmental powers)?",
             provision="I"),
    Question("s_affects", "scope", "Does the measure affect trade in services (purchase, payment, use or access to services, or the presence of suppliers)?",
             help="'Affecting' is read broadly: the measure need not regulate services directly.",
             provision="I", cases=("EC-Bananas", "Canada-Autos")),
    Question("s_govauth", "scope", "Is the service supplied in the exercise of governmental authority, i.e. neither on a commercial basis nor in competition with other suppliers?",
             provision="I"),

    # --- MFN ---
    Question("mfn_differential", "mfn", "Does the measure treat services or suppliers of some foreign countries less favourably than like services or suppliers of other foreign countries, in law or in fact?",
             help="Compare foreign Members with each other (not with domestic suppliers). De facto effects count.",
             provision="II", cases=("EC-Bananas", "Canada-Autos", "Argentina-FS")),
    Question("mfn_exemption", "mfn", "Is the measure listed in the Member's Article II (MFN) exemptions?", provision="II"),
    Question("mfn_art5", "mfn", "Is the preference granted under an economic integration agreement that meets Article V?",
             help="Substantial sectoral coverage and elimination of substantially all discrimination among the parties.",
             provision="V"),

    # --- commitments ---
    Question("c_committed", "commitments", "Has the Member undertaken specific commitments in the relevant sector for the affected mode(s)?",
             help="Check the Member's Schedule of Specific Commitments (and later revisions). For the EU, the consolidated EU schedule.",
             provision="XVI", cases=("China-Publications", "China-EPS")),
    Question("c_ma_unbound", "commitments", "Is the market-access column 'Unbound' for the affected mode(s)?", provision="XVI"),
    Question("c_nt_unbound", "commitments", "Is the national-treatment column 'Unbound' for the affected mode(s)?", provision="XVII"),
    Question("c_limitation", "commitments", "Is the measure covered by a limitation or condition inscribed in the Schedule (sector-specific or horizontal)?",
             provision="XVI"),

    # --- market access ---
    Question("ma_types", "market_access", "Which Article XVI:2 measure types does the measure impose?", kind="multi", options=XVI2,
             help="Leave empty if none. Only these six types are market-access limitations; other burdens are assessed under Articles VI or XVII.",
             provision="XVI", cases=("US-Gambling", "China-EPS", "Mexico-Telecoms")),
    Question("ma_zero_quota", "market_access", "Does the measure prohibit supply of the service through a committed mode altogether (a 'zero quota')?",
             provision="XVI", cases=("US-Gambling",)),

    # --- national treatment ---
    Question("nt_origin", "national_treatment", "Is the difference in treatment based exclusively on the origin of the service or supplier?",
             help="If yes, likeness may be presumed.", provision="XVII", cases=("Argentina-FS",)),
    Question("nt_like", "national_treatment", "Are the foreign and domestic services and suppliers 'like' (in a competitive relationship)?",
             provision="XVII", cases=("Argentina-FS", "China-Publications")),
    Question("nt_lfv", "national_treatment", "Does the measure modify the conditions of competition in favour of domestic services or suppliers (formally or de facto)?",
             help="Formally neutral criteria (e.g. size thresholds or designations that in practice capture mainly foreign firms) can do this.",
             provision="XVII", cases=("Argentina-FS", "EC-Bananas")),

    # --- domestic regulation ---
    Question("dr_type", "domestic_regulation", "Is the measure a qualification requirement or procedure, a licensing requirement or procedure, or a technical standard?",
             provision="VI"),
    Question("dr_admin_ok", "domestic_regulation", "Is the measure administered in a reasonable, objective and impartial manner?", provision="VI"),
    Question("dr_burden_ok", "domestic_regulation", "Is it based on objective and transparent criteria and no more burdensome than necessary to ensure the quality of the service?",
             provision="VI"),
    Question("dr_reference_paper", "domestic_regulation", "Has the Member scheduled the 2021 Reference Paper on Services Domestic Regulation for this sector?",
             provision="VI"),

    # --- general exceptions ---
    Question("x_paragraph", "exceptions", "Which Article XIV paragraph does the objective fall under?", kind="choice", options=XIV_PARAGRAPHS,
             help="The list is closed. Objectives such as innovation, competitiveness or 'digital sovereignty' are not listed as such.",
             provision="XIV"),
    Question("x_order_threat", "exceptions", "(Public order only) Is there a genuine and sufficiently serious threat to a fundamental interest of society?",
             provision="XIV", cases=("US-Gambling",)),
    Question("x_laws_consistent", "exceptions", "(Paragraph (c) only) Are the laws or regulations whose compliance is secured themselves consistent with GATS?",
             provision="XIV", cases=("Mexico-Soft-Drinks", "Colombia-Textiles")),
    Question("x_design", "exceptions", "Is the measure designed to pursue that objective (not incapable of contributing to it)?",
             provision="XIV", cases=("Colombia-Textiles",)),
    Question("x_contribution", "exceptions", "Does the measure make a material contribution to the objective?",
             provision="XIV", cases=("Brazil-Tyres", "Korea-Beef")),
    Question("x_highly_restrictive", "exceptions", "Is the measure highly trade-restrictive (e.g. a ban or exclusion of a category of suppliers)?",
             provision="XIV", cases=("Brazil-Tyres",)),
    Question("x_alternative", "exceptions", "Has a reasonably available, less trade-restrictive alternative been identified that would achieve the Member's chosen level of protection?",
             help="Not merely theoretical and without undue burden such as prohibitive cost or substantial technical difficulty.",
             provision="XIV", cases=("US-Gambling", "Korea-Beef")),

    # --- chapeau ---
    Question("ch_discrimination", "chapeau", "Is the measure applied in a way that discriminates arbitrarily or unjustifiably between countries where like conditions prevail?",
             help="Includes uneven enforcement that favours domestic suppliers, and discrimination unrelated to the stated objective.",
             provision="XIV_chapeau", cases=("US-Gambling", "US-Shrimp", "EC-Seals")),
    Question("ch_disguised", "chapeau", "Is the measure applied as a disguised restriction on trade in services?",
             provision="XIV_chapeau", cases=("US-Shrimp",)),

    # --- security ---
    Question("sec_invoked", "security", "Does the Member invoke essential security interests?", provision="XIVbis"),
    Question("sec_category", "security", "Does the measure relate to provisioning a military establishment or fissionable/fusionable materials, or is it taken in time of war or other emergency in international relations?",
             provision="XIVbis", cases=("Russia-Transit",)),
    Question("sec_plausible", "security", "Is the measure minimally plausible as a means of protecting the security interests articulated (good faith)?",
             provision="XIVbis", cases=("Russia-Transit",)),

    # --- prudential ---
    Question("fs_sector", "prudential", "Is the service a financial service (Annex on Financial Services)?", provision="FS_2a"),
    Question("fs_prudential", "prudential", "Is the measure taken for prudential reasons and not used to avoid the Member's commitments?",
             provision="FS_2a", cases=("Argentina-FS",)),
]

BY_ID = {q.id: q for q in QUESTIONS}


def template() -> dict:
    """An empty scenario with every question, for users to fill in."""
    answers = {}
    for q in QUESTIONS:
        if q.kind == "multi":
            answers[q.id] = []
        elif q.kind in ("text", "choice"):
            answers[q.id] = ""
        else:
            answers[q.id] = "unknown"
    return {"answers": answers, "notes": {}, "sources": []}


def as_dict() -> list[dict]:
    return [
        {"id": q.id, "step": q.step, "step_title": STEPS[q.step], "text": q.text, "help": q.help, "kind": q.kind,
         "options": [list(o) for o in q.options], "provision": q.provision, "cases": list(q.cases)}
        for q in QUESTIONS
    ]
