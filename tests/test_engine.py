import json

import pytest

from gats_engine import assess, template
from gats_engine.cli import load_scenario, main, scenario_names
from gats_engine.doctrine import CASES, PROVISIONS
from gats_engine.questions import BY_ID, QUESTIONS
from gats_engine.report import html_page, markdown

BASE = {
    "modes": ["mode1"], "s_measure": "yes", "s_affects": "yes", "s_govauth": "no",
    "mfn_differential": "no", "c_committed": "yes", "c_ma_unbound": "no", "c_nt_unbound": "no",
    "c_limitation": "no", "ma_types": [], "ma_zero_quota": "no", "nt_like": "yes", "nt_lfv": "no", "dr_type": "no",
}


def run(**over):
    return assess({"answers": {**BASE, **over}})


def status(result, step):
    return next(s for s in result.steps if s.step == step).status


# --- scope ------------------------------------------------------------------------------

def test_governmental_authority_is_excluded():
    r = run(s_govauth="yes")
    assert status(r, "scope") == "excluded" and r.risk == "Low" and len(r.steps) == 1


def test_no_concern_gives_low_risk_and_skips_defences():
    r = run()
    assert r.inconsistencies == [] and r.risk == "Low" and r.justification == "not_needed"
    assert status(r, "exceptions") == "skipped"


# --- commitments gate XVI/XVII -------------------------------------------------------------

def test_no_commitments_means_no_market_access_or_nt_analysis():
    r = run(c_committed="no", ma_zero_quota="yes", nt_lfv="yes")
    assert status(r, "market_access") == "not_applicable"
    assert status(r, "national_treatment") == "not_applicable"
    assert r.inconsistencies == []


def test_mfn_applies_without_commitments():
    r = run(c_committed="no", mfn_differential="yes", mfn_exemption="no", mfn_art5="no", x_paragraph="none")
    assert r.inconsistencies == ["Article II (MFN)"] and r.risk == "High"


def test_mfn_exemption_covers_differential_treatment():
    r = run(mfn_differential="yes", mfn_exemption="yes")
    assert status(r, "mfn") == "no_concern"


def test_inscribed_limitation_shields_market_access():
    r = run(ma_types=["f"], c_limitation="yes")
    assert status(r, "market_access") == "no_concern"


def test_unbound_market_access():
    assert status(run(ma_types=["a"], c_ma_unbound="yes"), "market_access") == "not_applicable"


def test_unknown_commitments_keep_analysis_conditional():
    r = run(c_committed="unknown", ma_types=["a"])
    ma = next(s for s in r.steps if s.step == "market_access")
    assert ma.status == "concern" and any("only if" in f for f in ma.findings)
    assert any(q["id"] == "c_committed" for q in r.open_questions)


# --- national treatment -------------------------------------------------------------------

def test_likeness_presumed_for_origin_based_distinctions():
    r = run(nt_like="unknown", nt_origin="yes", nt_lfv="yes", x_paragraph="none")
    assert "Article XVII (national treatment)" in r.inconsistencies


def test_unknown_likeness_is_an_information_gap():
    r = run(nt_like="unknown", nt_lfv="yes")
    assert status(r, "national_treatment") == "incomplete"
    assert r.risk == "Medium" and any(q["id"] == "nt_like" for q in r.open_questions)


# --- Article XIV -----------------------------------------------------------------------------

JUSTIFIED = dict(ma_zero_quota="yes", x_paragraph="b", x_design="yes", x_contribution="yes", x_alternative="no",
                 ch_discrimination="no", ch_disguised="no")


def test_fully_justified_measure_is_low_risk():
    """The original engine rated this 'Medium'; justification must reduce risk."""
    r = run(**JUSTIFIED)
    assert r.inconsistencies and r.justification == "available" and r.risk == "Low"


def test_unlisted_objective_cannot_justify():
    r = run(**{**JUSTIFIED, "x_paragraph": "none"})
    assert status(r, "exceptions") == "not_satisfied" and r.risk == "High"
    assert status(r, "chapeau") == "skipped"


def test_reasonably_available_alternative_defeats_necessity():
    assert run(**{**JUSTIFIED, "x_alternative": "yes"}).justification == "unavailable"


def test_chapeau_failure():
    r = run(**{**JUSTIFIED, "ch_discrimination": "yes"})
    assert status(r, "chapeau") == "not_satisfied" and r.risk == "High"


def test_public_order_requires_serious_threat():
    assert run(**{**JUSTIFIED, "x_paragraph": "a_order", "x_order_threat": "no"}).justification == "unavailable"


def test_paragraph_c_requires_consistent_laws():
    assert run(**{**JUSTIFIED, "x_paragraph": "c_other", "x_laws_consistent": "no"}).justification == "unavailable"


def test_paragraph_d_only_covers_national_treatment():
    r = run(**{**JUSTIFIED, "x_paragraph": "d", "x_laws_consistent": "yes"})
    assert r.justification == "unavailable"  # the concern is under Article XVI


def test_missing_defence_facts_give_medium():
    r = run(ma_zero_quota="yes", x_paragraph="b")
    assert r.justification == "doubtful" and r.risk == "Medium"


def test_security_exception_as_alternative_defence():
    r = run(ma_zero_quota="yes", x_paragraph="none", sec_invoked="yes", sec_category="yes", sec_plausible="yes")
    assert r.justification == "available"


def test_prudential_carve_out():
    r = run(ma_types=["f"], x_paragraph="none", fs_sector="yes", fs_prudential="yes")
    assert r.justification == "available"


# --- scenarios ----------------------------------------------------------------------------------

def test_us_gambling_reproduces_the_dispute_outcome():
    """Validation: XVI violation, provisionally justified under XIV(a), fails the chapeau."""
    r = assess(load_scenario("us_gambling_remote_betting"))
    assert r.inconsistencies == ["Article XVI (market access)"]
    assert status(r, "exceptions") == "satisfied"
    assert status(r, "chapeau") == "not_satisfied"
    assert r.risk == "High"


@pytest.mark.parametrize("name", scenario_names())
def test_every_scenario_runs_and_renders(name):
    sc = load_scenario(name)
    unknown = set(sc["answers"]) - set(BY_ID)
    assert not unknown, f"unknown question ids {unknown}"
    r = assess(sc)
    assert r.risk in {"Low", "Medium", "High"}
    assert markdown(r).startswith("# GATS analysis")
    assert html_page(r).startswith("<!DOCTYPE html>")
    json.dumps(r.to_dict())
    if "expected" in sc:
        assert r.risk == sc["expected"]["risk"] and r.inconsistencies == sc["expected"]["inconsistencies"]


def test_data_act_scenarios_flag_their_pivotal_questions():
    r = assess(load_scenario("eu_data_act_art32_governmental_access"))
    assert {q["id"] for q in r.open_questions} >= {"nt_lfv"}
    r = assess(load_scenario("eu_data_act_art35_interoperability"))
    assert status(r, "domestic_regulation") == "incomplete"


def test_origin_neutral_access_duties_raise_no_market_access_issue():
    """Arts. 3-5: qualitative duties are not XVI:2 limitations; the open issue is de facto national treatment."""
    r = assess(load_scenario("eu_data_act_art3_5_connected_product_data"))
    assert r.inconsistencies == [] and status(r, "market_access") == "no_concern"
    assert {q["id"] for q in r.open_questions} >= {"nt_lfv", "dr_type"}


def test_proposed_transfer_ban_turns_on_localisation_and_security_questions():
    r = assess(load_scenario("eu_data_act_art32_3a_transfer_ban_proposal"))
    assert r.inconsistencies == ["Article XVII (national treatment)"] and r.justification == "doubtful"
    assert {q["id"] for q in r.open_questions} >= {"ma_zero_quota", "sec_category", "x_alternative"}


def test_unknown_facts_are_never_reported_as_no_issue():
    assert status(run(ma_zero_quota="unknown"), "market_access") == "incomplete"
    assert status(run(dr_type="unknown"), "domestic_regulation") == "incomplete"


# --- doctrine and questionnaire integrity ----------------------------------------------------------

def test_every_reference_resolves():
    for q in QUESTIONS:
        assert not q.provision or q.provision in PROVISIONS, q.id
        assert all(c in CASES for c in q.cases), q.id
    for c in CASES.values():
        assert c.url.startswith("https://www.wto.org/english/tratop_e/dispu_e/cases_e/ds")


def test_template_contains_every_question():
    t = template()
    assert set(t["answers"]) == {q.id for q in QUESTIONS}
    assert assess(t).risk in {"Low", "Medium"}  # blank template never claims a violation


def test_innovation_is_not_an_article_xiv_ground():
    opts = dict(BY_ID["x_paragraph"].options)
    assert "innovation" in opts["none"] and not any("innovation" in v for k, v in opts.items() if k != "none")


# --- CLI ---------------------------------------------------------------------------------------------

def test_cli(tmp_path, capsys):
    assert main(["examples"]) == 0
    assert "eu_data_act_art5_gatekeepers" in capsys.readouterr().out
    out = tmp_path / "memo.html"
    assert main(["assess", "data_localisation_cloud", "--format", "html", "--out", str(out)]) == 0
    assert "Article XIV" in out.read_text()
    capsys.readouterr()
    assert main(["assess", "us_gambling_remote_betting", "--format", "json"]) == 0
    assert json.loads(capsys.readouterr().out)["risk"] == "High"
    assert main(["assess", "nope"]) == 2


def test_bool_answers_are_accepted():
    r = assess({"answers": {**BASE, "s_govauth": True, "s_measure": True, "s_affects": True}})
    assert status(r, "scope") == "excluded"
