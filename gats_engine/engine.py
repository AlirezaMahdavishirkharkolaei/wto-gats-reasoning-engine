"""The reasoning engine: walks a measure through the GATS analysis step by step.

The sequence follows WTO jurisprudence:

1. scope (Article I) ->
2. MFN (Article II, applies regardless of commitments) ->
3. specific commitments ->
4. market access (XVI) and 5. national treatment (XVII), only where committed ->
6. domestic regulation (VI) ->
7. general exceptions (XIV: paragraph, design, necessity) ->
8. chapeau ->
9. security exceptions (XIV bis) and 10. the prudential carve-out as alternative defences.

The engine never guesses: unanswered questions are reported as information
gaps, and the overall assessment says how far the inputs support it.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

from . import doctrine
from .questions import BY_ID, QUESTIONS, STEPS, XIV_PARAGRAPHS, XVI2

YES, NO, UNKNOWN = "yes", "no", "unknown"

STATUS_LABELS = {
    "concern": "Issue indicated",
    "no_concern": "No issue indicated",
    "not_applicable": "Not applicable",
    "incomplete": "Information missing",
    "satisfied": "Requirement met",
    "not_satisfied": "Requirement not met",
    "excluded": "Outside GATS",
    "skipped": "Not reached",
    "info": "Checked",
}


@dataclass
class StepResult:
    step: str
    title: str
    status: str
    findings: list[str] = field(default_factory=list)
    provisions: list[str] = field(default_factory=list)
    cases: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)

    @property
    def status_label(self) -> str:
        return STATUS_LABELS[self.status]


@dataclass
class Assessment:
    measure: dict
    steps: list[StepResult]
    inconsistencies: list[str]
    justification: str  # "not_needed" | "available" | "doubtful" | "unavailable"
    risk: str  # "Low" | "Medium" | "High"
    conclusion: str
    counterarguments: list[str]
    open_questions: list[dict]
    completeness: float
    notes: dict = field(default_factory=dict)
    sources: list = field(default_factory=list)

    def to_dict(self) -> dict:
        d = asdict(self)
        for s, step in zip(d["steps"], self.steps):
            s["status_label"] = step.status_label
            s["case_citations"] = [doctrine.case(c).cite(step.step) for c in step.cases]
            s["case_urls"] = [doctrine.case(c).url for c in step.cases]
            s["provision_titles"] = [doctrine.provision(p).title for p in step.provisions]
        return d


class Answers:
    """Normalised access to a scenario's answers."""

    def __init__(self, raw: dict):
        self.raw = raw or {}

    def get(self, qid: str) -> str:
        v = self.raw.get(qid)
        if isinstance(v, bool):
            return YES if v else NO
        if v is None:
            return UNKNOWN
        v = str(v).strip().lower()
        return {"true": YES, "y": YES, "false": NO, "n": NO, "": UNKNOWN}.get(v, v)

    def choice(self, qid: str) -> str:
        v = self.raw.get(qid) or ""
        return str(v).strip()

    def multi(self, qid: str) -> list[str]:
        v = self.raw.get(qid) or []
        if isinstance(v, str):
            v = [x.strip() for x in v.split(",") if x.strip()]
        return [str(x) for x in v]

    def text(self, qid: str) -> str:
        return str(self.raw.get(qid) or "").strip()


def _label(options, key):
    return dict(options).get(key, key)


def assess(scenario: dict) -> Assessment:
    a = Answers(scenario.get("answers", scenario))
    steps: list[StepResult] = []

    def need(step: StepResult, *qids: str) -> bool:
        """Record unknown answers; return True if all are known."""
        ok = True
        for q in qids:
            if a.get(q) == UNKNOWN:
                step.missing.append(q)
                ok = False
        return ok

    measure = {k: a.text(k) for k in ("name", "member", "description", "sector")}
    measure["modes"] = [dict(BY_ID["modes"].options).get(m, m) for m in a.multi("modes")]

    # ---------------------------------------------------------------- 1. scope
    s = StepResult("scope", STEPS["scope"], "no_concern", provisions=["I"], cases=["EC-Bananas"])
    need(s, "s_measure", "s_affects", "s_govauth")
    if a.get("s_measure") == NO or a.get("s_affects") == NO:
        s.status = "excluded"
        s.findings.append("On the inputs, this is not a measure by a Member affecting trade in services: GATS does not apply.")
    elif a.get("s_govauth") == YES:
        s.status = "excluded"
        s.findings.append("The service is supplied in the exercise of governmental authority (Article I:3(b)-(c)) and falls outside GATS.")
    else:
        s.findings.append("The measure appears to be a measure by a Member affecting trade in services; 'affecting' is read broadly.")
        if not measure["modes"]:
            s.missing.append("modes")
            s.findings.append("Identify the modes of supply concerned: the commitments analysis is mode-specific.")
        if s.missing:
            s.status = "incomplete"
    steps.append(s)
    if s.status == "excluded":
        return _finish(a, measure, steps, scenario, excluded=True)

    concerns: list[str] = []

    # ---------------------------------------------------------------- 2. MFN
    m = StepResult("mfn", STEPS["mfn"], "no_concern", provisions=["II"], cases=["Canada-Autos", "Argentina-FS"])
    diff = a.get("mfn_differential")
    if diff == YES:
        if a.get("mfn_exemption") == YES:
            m.findings.append("Differential treatment between foreign Members is indicated, but the measure is covered by an Article II exemption.")
        elif a.get("mfn_art5") == YES:
            m.provisions.append("V")
            m.findings.append("Differential treatment is indicated; the Member may rely on Article V (economic integration). "
                              "This defence requires substantial sectoral coverage and elimination of substantially all discrimination.")
            m.status = "concern"
            concerns.append("II")
        else:
            need(m, "mfn_exemption", "mfn_art5")
            m.status = "concern"
            concerns.append("II")
            m.findings.append("Less favourable treatment of like services or suppliers of some Members is indicated: a prima facie "
                              "inconsistency with Article II:1, which applies whether or not commitments exist (de facto discrimination counts).")
    elif diff == UNKNOWN:
        m.status = "incomplete"
        m.missing.append("mfn_differential")
        m.findings.append("Whether foreign suppliers from different Members are treated differently (in law or in fact) is not established.")
    else:
        m.findings.append("No differential treatment between foreign Members is indicated.")
    steps.append(m)

    # ---------------------------------------------------------------- 3. commitments
    c = StepResult("commitments", STEPS["commitments"], "no_concern",
                   provisions=["XVI", "XVII"], cases=["China-Publications"])
    committed = a.get("c_committed")
    ma_unbound = a.get("c_ma_unbound") == YES
    nt_unbound = a.get("c_nt_unbound") == YES
    limitation = a.get("c_limitation") == YES
    if committed == NO:
        c.status = "not_applicable"
        c.findings.append("No specific commitments in the sector and mode(s): Articles XVI and XVII do not apply. "
                          "Article II and the general obligations still do.")
    elif committed == UNKNOWN:
        c.status = "incomplete"
        c.missing.append("c_committed")
        c.findings.append("The Schedule has not been checked. The market access and national treatment analysis below is conditional on commitments existing.")
    else:
        c.status = "info"
        c.findings.append("Specific commitments exist for the sector and mode(s).")
        if ma_unbound:
            c.findings.append("Market access is 'Unbound' for the mode(s): no Article XVI obligation.")
        if nt_unbound:
            c.findings.append("National treatment is 'Unbound' for the mode(s): no Article XVII obligation.")
        if limitation:
            c.findings.append("The measure is covered by an inscribed limitation, which shields it to the extent of that limitation.")
        elif a.get("c_limitation") == UNKNOWN:
            c.missing.append("c_limitation")
    steps.append(c)
    conditional = committed == UNKNOWN

    # ---------------------------------------------------------------- 4. market access
    ma = StepResult("market_access", STEPS["market_access"], "no_concern", provisions=["XVI"], cases=["US-Gambling", "China-EPS"])
    types = a.multi("ma_types")
    zero = a.get("ma_zero_quota") == YES
    if committed == NO or ma_unbound:
        ma.status = "not_applicable"
        ma.findings.append("Not applicable: no market-access commitment for the affected mode(s).")
    elif types or zero:
        labels = [_label(XVI2, t) for t in types]
        if zero and "a" not in types:
            labels.append("a total prohibition of supply through a committed mode, which operates as a 'zero quota' under XVI:2(a) and (c)")
        if limitation:
            ma.findings.append("The measure falls under Article XVI:2 (" + "; ".join(labels) + ") but is covered by an inscribed limitation.")
        else:
            ma.status = "concern"
            concerns.append("XVI")
            ma.findings.append("The measure falls under the exhaustive list of Article XVI:2: " + "; ".join(labels) + ".")
            if conditional:
                ma.findings.append("This holds only if the Member has a market-access commitment for the mode(s).")
    else:
        if a.get("ma_zero_quota") == UNKNOWN and not types:
            ma.missing.append("ma_zero_quota")
        ma.findings.append("None of the six Article XVI:2 measure types is indicated. Other burdens belong under Articles VI or XVII.")
    steps.append(ma)

    # ---------------------------------------------------------------- 5. national treatment
    nt = StepResult("national_treatment", STEPS["national_treatment"], "no_concern", provisions=["XVII"], cases=["Argentina-FS"])
    if committed == NO or nt_unbound:
        nt.status = "not_applicable"
        nt.findings.append("Not applicable: no national-treatment commitment for the affected mode(s).")
    else:
        like = a.get("nt_like")
        if like == UNKNOWN and a.get("nt_origin") == YES:
            like = YES
            nt.findings.append("Likeness is presumed because the distinction is based exclusively on origin.")
        lfv = a.get("nt_lfv")
        if lfv == YES and like == YES:
            if limitation:
                nt.findings.append("Less favourable treatment of like services/suppliers is indicated but covered by an inscribed condition.")
            else:
                nt.status = "concern"
                concerns.append("XVII")
                nt.findings.append("The measure modifies the conditions of competition in favour of domestic like services or suppliers: "
                                   "a prima facie inconsistency with Article XVII (formal or de facto).")
                if conditional:
                    nt.findings.append("This holds only if the Member has a national-treatment commitment for the mode(s).")
        elif lfv == NO or like == NO:
            nt.findings.append("No less favourable treatment of like domestic services or suppliers is indicated.")
        else:
            nt.status = "incomplete"
            if like == UNKNOWN:
                nt.missing.append("nt_like")
            if lfv == UNKNOWN:
                nt.missing.append("nt_lfv")
            nt.findings.append("Likeness and/or the effect on conditions of competition are not established.")
    steps.append(nt)

    # ---------------------------------------------------------------- 6. domestic regulation
    dr = StepResult("domestic_regulation", STEPS["domestic_regulation"], "no_concern", provisions=["VI"])
    if a.get("dr_type") == YES:
        if committed == NO:
            dr.status = "not_applicable"
            dr.findings.append("Article VI:1 and VI:5 apply in committed sectors; none are indicated.")
        else:
            bad = [q for q in ("dr_admin_ok", "dr_burden_ok") if a.get(q) == NO]
            if bad:
                dr.status = "concern"
                concerns.append("VI")
                if "dr_admin_ok" in bad:
                    dr.findings.append("Administration does not appear reasonable, objective and impartial (Article VI:1).")
                if "dr_burden_ok" in bad:
                    dr.findings.append("The requirement does not appear objective, transparent and no more burdensome than necessary "
                                       "to ensure quality (Article VI:4-5).")
            else:
                need(dr, "dr_admin_ok", "dr_burden_ok")
                dr.findings.append("A licensing/qualification requirement or technical standard: Article VI disciplines apply.")
                if dr.missing:
                    dr.status = "incomplete"
            if a.get("dr_reference_paper") == YES:
                dr.findings.append("The Member has scheduled the Reference Paper on Services Domestic Regulation: its additional "
                                   "disciplines (transparency, objective criteria, timely procedures) also apply.")
    elif a.get("dr_type") == UNKNOWN:
        dr.missing.append("dr_type")
        dr.findings.append("Whether the measure is a licensing/qualification requirement or technical standard is not established.")
    else:
        dr.status = "not_applicable"
        dr.findings.append("Not a licensing/qualification requirement or technical standard.")
    steps.append(dr)

    if not concerns:
        for sid in ("exceptions", "chapeau", "security", "prudential"):
            steps.append(StepResult(sid, STEPS[sid], "skipped", findings=["Not reached: no prima facie inconsistency indicated."]))
        return _finish(a, measure, steps, scenario, concerns=concerns)

    # ---------------------------------------------------------------- 7. Article XIV
    x = StepResult("exceptions", STEPS["exceptions"], "incomplete", provisions=["XIV"], cases=["Korea-Beef", "US-Gambling"])
    para = a.choice("x_paragraph")
    xiv_ok = None  # True / False / None (undetermined)
    if not para:
        x.missing.append("x_paragraph")
        x.findings.append("No Article XIV paragraph identified for the measure's objective.")
    elif para == "none":
        x.status = "not_satisfied"
        xiv_ok = False
        x.findings.append("The objective is not covered by any Article XIV paragraph (the list is closed). Article XIV cannot justify the measure.")
    else:
        x.findings.append(f"Objective invoked under Article XIV {_label(XIV_PARAGRAPHS, para)}.")
        para_ok = True
        uncovered = []
        if para == "d":
            uncovered = [p for p in concerns if p != "XVII"]
        elif para == "e":
            uncovered = [p for p in concerns if p != "II"]
        if uncovered:
            para_ok = False
            x.findings.append(f"Paragraph ({para}) can only justify inconsistencies with Article "
                              f"{'XVII' if para == 'd' else 'II'}; it does not cover Article(s) {', '.join(uncovered)}.")
        if para == "a_order":
            v = a.get("x_order_threat")
            if v == NO:
                para_ok = False
                x.findings.append("Footnote 5: public order requires a genuine and sufficiently serious threat to a fundamental interest of society, which is not indicated.")
            elif v == UNKNOWN:
                x.missing.append("x_order_threat")
        if para.startswith("c"):
            x.cases += ["Colombia-Textiles", "Mexico-Soft-Drinks"]
            v = a.get("x_laws_consistent")
            if v == NO:
                para_ok = False
                x.findings.append("Paragraph (c) requires the underlying laws or regulations to be GATS-consistent, which is not indicated.")
            elif v == UNKNOWN:
                x.missing.append("x_laws_consistent")
            if para == "c_privacy":
                x.findings.append("Note: paragraph (c)(ii) concerns the privacy of individuals in relation to personal data; measures on non-personal data do not fit it.")
        design = a.get("x_design")
        contribution = a.get("x_contribution")
        alternative = a.get("x_alternative")
        restrictive = a.get("x_highly_restrictive")
        nec = None
        if design == NO:
            nec = False
            x.findings.append("The measure does not appear designed to pursue the objective.")
        elif contribution == NO:
            nec = False
            x.findings.append("The measure does not appear to make a material contribution to the objective; it is unlikely to be 'necessary'.")
        elif alternative == YES:
            nec = False
            x.findings.append("A reasonably available, less trade-restrictive alternative achieving the same level of protection has been identified: "
                              "the measure is unlikely to be 'necessary'.")
        elif design == YES and contribution == YES and alternative == NO:
            nec = True
            x.findings.append("Weighing and balancing: the measure is designed for the objective, contributes materially, and no reasonably "
                              "available alternative is identified. Necessity appears arguable.")
        else:
            for q in ("x_design", "x_contribution", "x_alternative"):
                if a.get(q) == UNKNOWN:
                    x.missing.append(q)
            x.findings.append("The necessity test cannot be completed on the inputs.")
        if restrictive == YES:
            x.findings.append("The measure is highly trade-restrictive, which raises the bar for showing a material contribution.")
            x.cases.append("Brazil-Tyres")
        if para_ok and nec is True and not x.missing:
            x.status, xiv_ok = "satisfied", True
        elif not para_ok or nec is False:
            x.status, xiv_ok = "not_satisfied", False
    steps.append(x)

    # ---------------------------------------------------------------- 8. chapeau
    ch = StepResult("chapeau", STEPS["chapeau"], "incomplete", provisions=["XIV_chapeau"], cases=["US-Gambling", "US-Shrimp"])
    chapeau_ok = None
    if xiv_ok is False:
        ch.status = "skipped"
        ch.findings.append("Not reached: the measure is not provisionally justified under a paragraph of Article XIV.")
    else:
        d1, d2 = a.get("ch_discrimination"), a.get("ch_disguised")
        if d1 == YES or d2 == YES:
            ch.status, chapeau_ok = "not_satisfied", False
            if d1 == YES:
                ch.findings.append("The measure appears to be applied with arbitrary or unjustifiable discrimination between countries where like conditions prevail.")
            if d2 == YES:
                ch.findings.append("The measure appears to operate as a disguised restriction on trade in services.")
        elif d1 == NO and d2 == NO:
            ch.status, chapeau_ok = "satisfied", True
            ch.findings.append("No arbitrary or unjustifiable discrimination or disguised restriction is indicated in the measure's application.")
        else:
            for q in ("ch_discrimination", "ch_disguised"):
                if a.get(q) == UNKNOWN:
                    ch.missing.append(q)
            ch.findings.append("The application of the measure (consistency of enforcement, flexibility, rationale of any discrimination) is not established.")
    steps.append(ch)

    # ---------------------------------------------------------------- 9. security
    sec = StepResult("security", STEPS["security"], "not_applicable", provisions=["XIVbis"], cases=["Russia-Transit"])
    sec_ok = None
    if a.get("sec_invoked") == YES:
        cat, plaus = a.get("sec_category"), a.get("sec_plausible")
        if cat == YES and plaus == YES:
            sec.status, sec_ok = "satisfied", True
            sec.findings.append("The security exception appears available: the circumstances fall within XIV bis:1(b) and the measure is "
                                "minimally plausible in good faith. The exception is broad but not entirely self-judging.")
        elif cat == NO or plaus == NO:
            sec.status, sec_ok = "not_satisfied", False
            sec.findings.append("The security exception does not appear available: the measure is outside the XIV bis:1(b) categories or "
                                "lacks a plausible connection to the security interests.")
        else:
            sec.status = "incomplete"
            for q in ("sec_category", "sec_plausible"):
                if a.get(q) == UNKNOWN:
                    sec.missing.append(q)
            sec.findings.append("The security defence cannot be assessed on the inputs.")
    else:
        sec.findings.append("No essential security interest invoked.")
    steps.append(sec)

    # ---------------------------------------------------------------- 10. prudential
    pr = StepResult("prudential", STEPS["prudential"], "not_applicable", provisions=["FS_2a"], cases=["Argentina-FS"])
    pr_ok = None
    if a.get("fs_sector") == YES:
        v = a.get("fs_prudential")
        if v == YES:
            pr.status, pr_ok = "satisfied", True
            pr.findings.append("The prudential carve-out appears available for this financial-services measure.")
        elif v == NO:
            pr.status, pr_ok = "not_satisfied", False
            pr.findings.append("The measure does not appear to be taken for prudential reasons, or is used to avoid commitments.")
        else:
            pr.status = "incomplete"
            pr.missing.append("fs_prudential")
    else:
        pr.findings.append("Not a financial service.")
    steps.append(pr)

    xiv_path = True if (xiv_ok is True and chapeau_ok is True) else (False if (xiv_ok is False or chapeau_ok is False) else None)
    defences = [xiv_path, sec_ok, pr_ok]
    if any(d is True for d in defences):
        justification = "available"
    elif (xiv_path is None
          or (sec_ok is None and a.get("sec_invoked") == YES)
          or (pr_ok is None and a.get("fs_sector") == YES)):
        justification = "doubtful"
    else:
        justification = "unavailable"
    return _finish(a, measure, steps, scenario, concerns=concerns, justification=justification)


COUNTER = {
    "II": "The respondent may argue that the services or suppliers are not 'like', that no less favourable treatment results, or rely on an Article II exemption or Article V.",
    "XVI": "The respondent may argue that the sector or mode is not committed, that the Schedule inscribes a limitation, or that the measure is not one of the six XVI:2 types (but a qualitative requirement under Article VI).",
    "XVII": "The respondent may contest likeness (different regulatory risks or consumer perception), argue that conditions of competition are not modified, or that a formally neutral criterion is unrelated to origin.",
    "VI": "The respondent may argue that the requirement is necessary to ensure the quality of the service and administered objectively, or that Article VI:5 only applies where commitments are nullified or impaired.",
}


def _finish(a: Answers, measure, steps, scenario, excluded=False, concerns=None, justification="not_needed") -> Assessment:
    concerns = concerns or []
    open_q = []
    seen = set()
    for st in steps:
        for q in st.missing:
            if q not in seen and q in BY_ID:
                seen.add(q)
                open_q.append({"id": q, "step": STEPS[BY_ID[q].step], "question": BY_ID[q].text})
    legal_qs = [q for q in QUESTIONS if q.kind in ("ynu", "choice", "multi") and q.step != "measure"]
    answered = sum(1 for q in legal_qs if (a.get(q.id) != UNKNOWN if q.kind == "ynu" else bool(a.raw.get(q.id))))
    completeness = round(answered / len(legal_qs), 2)

    names = {"II": "Article II (MFN)", "XVI": "Article XVI (market access)", "XVII": "Article XVII (national treatment)",
             "VI": "Article VI (domestic regulation)"}
    if excluded:
        risk, conclusion = "Low", "On the inputs, the measure falls outside the scope of GATS."
    elif not concerns:
        risk = "Low" if not open_q else "Medium"
        conclusion = "No prima facie inconsistency with GATS is indicated on the inputs."
        if open_q:
            conclusion += " Several facts are missing, so this conclusion is provisional."
    else:
        listed = ", ".join(names[c] for c in concerns)
        if justification == "available":
            risk = "Low"
            conclusion = (f"Prima facie inconsistency indicated with {listed}, but a defence appears available on the inputs. "
                          "The respondent bears the burden of proving it.")
        elif justification == "doubtful":
            risk = "Medium"
            conclusion = (f"Prima facie inconsistency indicated with {listed}. Whether it can be justified cannot be determined on the inputs; "
                          "see the open questions.")
        else:
            risk = "High"
            conclusion = f"Prima facie inconsistency indicated with {listed}, and no defence appears available on the inputs."

    counter = [COUNTER[c] for c in concerns]
    if justification == "available":
        counter.append("The complainant may challenge the defence: propose a reasonably available alternative, show uneven enforcement "
                       "(chapeau), or dispute that the objective fits the invoked paragraph.")
    return Assessment(measure, steps, [names[c] for c in concerns], justification, risk, conclusion, counter, open_q,
                      completeness, scenario.get("notes", {}), scenario.get("sources", []))
