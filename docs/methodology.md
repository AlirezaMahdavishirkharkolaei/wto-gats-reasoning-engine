# Methodology

This document sets out the decision rules the engine applies. It is meant to be read alongside the questionnaire ([`questions.py`](../gats_engine/questions.py)) and the sources ([`doctrine.py`](../gats_engine/doctrine.py)).

## Principles

* **Sequence:** the order follows WTO practice. Scope comes first. MFN is examined before commitments because it applies to all covered measures. Market access and national treatment are examined only where commitments exist. Defences come last.
* **Three-valued answers:** every legal question takes *yes*, *no* or *unknown*. An unknown answer never resolves a test; it produces the status *information missing* and an open question.
* **Conditional analysis:** if the Schedule has not been checked, Articles XVI and XVII are analysed on the assumption that commitments exist, and the findings say so.
* **Burden of proof:** findings of inconsistency are prima facie. Defences are the respondent's burden, and the conclusion says this whenever a defence appears available.

## Decision rules

| Step | Rule |
|---|---|
| Scope | GATS does not apply if there is no measure by a Member, if the measure does not affect trade in services, or if the service is supplied in the exercise of governmental authority. |
| MFN | Differential treatment between foreign Members → prima facie Art. II inconsistency, unless covered by an Art. II exemption. Art. V is noted as an available defence. |
| Commitments | No commitment → XVI and XVII not applicable. 'Unbound' → the respective article is not applicable. An inscribed limitation shields the measure. |
| Market access | Any XVI:2(a)-(f) measure type, or a total prohibition of supply through a committed mode (zero quota) → issue indicated. Other burdens go to Arts. VI or XVII. |
| National treatment | Likeness (answered yes, or presumed when the distinction is origin-based) **and** a modification of the conditions of competition → issue indicated. |
| Domestic regulation | Licensing, qualification or technical-standard measure in a committed sector that is not administered reasonably, objectively and impartially, or is more burdensome than necessary → issue indicated. |
| Art. XIV paragraph | 'None' → not satisfied. Public order needs a serious threat (fn. 5). Paragraph (c) needs GATS-consistent underlying laws. (d) covers only XVII and (e) only II. |
| Necessity | Not designed, no material contribution, or a reasonably available less restrictive alternative → not necessary. Designed + material contribution + no alternative → necessity arguable. Otherwise incomplete. |
| Chapeau | Arbitrary or unjustifiable discrimination, or a disguised restriction → not satisfied. 'No' to both → satisfied. |
| Security | Relevant XIV bis:1(b) category + minimal good-faith plausibility → available. |
| Prudential | A financial service + a measure taken for prudential reasons → available. |

## Overall assessment

* **No issue indicated:** risk is Low, or Medium if facts are missing.
* **Issue indicated and a defence available**, meaning the full Art. XIV path (paragraph, necessity and chapeau), XIV bis, or the prudential carve-out: risk is **Low**.
* **Issue indicated and the defence cannot be decided** on the inputs: risk is **Medium**.
* **Issue indicated and every invoked defence fails or none exists:** risk is **High**.

*Input completeness* is the share of legal questions answered.

## Validation

The `us_gambling_remote_betting` scenario encodes the facts as found in DS285. The engine reproduces the Appellate Body's sequence: an Article XVI violation (zero quota), provisional justification under XIV(a) including necessity, and failure of the chapeau. This is a regression test (`tests/test_engine.py`).

## Questionnaire


### Measure

* `name`: Name of the measure
* `member`: WTO Member adopting the measure
* `description`: Short description of what the measure requires or prohibits
* `sector`: Service sector (with W/120 or CPC reference if known)
* `modes`: Modes of supply affected

### 1. Scope (Article I)

* `s_measure`: Is it a measure by a WTO Member (any level of government, or a body exercising delegated governmental powers)?
* `s_affects`: Does the measure affect trade in services (purchase, payment, use or access to services, or the presence of suppliers)?
* `s_govauth`: Is the service supplied in the exercise of governmental authority, i.e. neither on a commercial basis nor in competition with other suppliers?

### 2. Most-favoured-nation treatment (Article II)

* `mfn_differential`: Does the measure treat services or suppliers of some foreign countries less favourably than like services or suppliers of other foreign countries, in law or in fact?
* `mfn_exemption`: Is the measure listed in the Member's Article II (MFN) exemptions?
* `mfn_art5`: Is the preference granted under an economic integration agreement that meets Article V?

### 3. Specific commitments (Schedule)

* `c_committed`: Has the Member undertaken specific commitments in the relevant sector for the affected mode(s)?
* `c_ma_unbound`: Is the market-access column 'Unbound' for the affected mode(s)?
* `c_nt_unbound`: Is the national-treatment column 'Unbound' for the affected mode(s)?
* `c_limitation`: Is the measure covered by a limitation or condition inscribed in the Schedule (sector-specific or horizontal)?

### 4. Market access (Article XVI)

* `ma_types`: Which Article XVI:2 measure types does the measure impose?
* `ma_zero_quota`: Does the measure prohibit supply of the service through a committed mode altogether (a 'zero quota')?

### 5. National treatment (Article XVII)

* `nt_origin`: Is the difference in treatment based exclusively on the origin of the service or supplier?
* `nt_like`: Are the foreign and domestic services and suppliers 'like' (in a competitive relationship)?
* `nt_lfv`: Does the measure modify the conditions of competition in favour of domestic services or suppliers (formally or de facto)?

### 6. Domestic regulation (Article VI)

* `dr_type`: Is the measure a qualification requirement or procedure, a licensing requirement or procedure, or a technical standard?
* `dr_admin_ok`: Is the measure administered in a reasonable, objective and impartial manner?
* `dr_burden_ok`: Is it based on objective and transparent criteria and no more burdensome than necessary to ensure the quality of the service?
* `dr_reference_paper`: Has the Member scheduled the 2021 Reference Paper on Services Domestic Regulation for this sector?

### 7. General exceptions (Article XIV)

* `x_paragraph`: Which Article XIV paragraph does the objective fall under?
* `x_order_threat`: (Public order only) Is there a genuine and sufficiently serious threat to a fundamental interest of society?
* `x_laws_consistent`: (Paragraph (c) only) Are the laws or regulations whose compliance is secured themselves consistent with GATS?
* `x_design`: Is the measure designed to pursue that objective (not incapable of contributing to it)?
* `x_contribution`: Does the measure make a material contribution to the objective?
* `x_highly_restrictive`: Is the measure highly trade-restrictive (e.g. a ban or exclusion of a category of suppliers)?
* `x_alternative`: Has a reasonably available, less trade-restrictive alternative been identified that would achieve the Member's chosen level of protection?

### 8. Chapeau of Article XIV

* `ch_discrimination`: Is the measure applied in a way that discriminates arbitrarily or unjustifiably between countries where like conditions prevail?
* `ch_disguised`: Is the measure applied as a disguised restriction on trade in services?

### 9. Security exceptions (Article XIV bis)

* `sec_invoked`: Does the Member invoke essential security interests?
* `sec_category`: Does the measure relate to provisioning a military establishment or fissionable/fusionable materials, or is it taken in time of war or other emergency in international relations?
* `sec_plausible`: Is the measure minimally plausible as a means of protecting the security interests articulated (good faith)?

### 10. Prudential carve-out (financial services)

* `fs_sector`: Is the service a financial service (Annex on Financial Services)?
* `fs_prudential`: Is the measure taken for prudential reasons and not used to avoid the Member's commitments?
