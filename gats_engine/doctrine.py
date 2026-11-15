"""Legal sources used by the engine: GATS provisions and WTO dispute settlement reports.

Holdings are paraphrased summaries for orientation. Pinpoint paragraphs are
given only where the author has checked them; always read the report itself.
Dispute pages follow the WTO's stable URL pattern.
"""

from __future__ import annotations

from dataclasses import dataclass

GATS_URL = "https://www.wto.org/english/docs_e/legal_e/26-gats_01_e.htm"


def _ds(n: int) -> str:
    return f"https://www.wto.org/english/tratop_e/dispu_e/cases_e/ds{n}_e.htm"


@dataclass(frozen=True)
class Provision:
    id: str
    title: str
    summary: str
    url: str = GATS_URL


@dataclass(frozen=True)
class Case:
    id: str
    short_title: str
    ds: str
    reports: str
    holding: str
    url: str
    pinpoints: tuple[tuple[str, str], ...] = ()  # (analysis step, paragraphs)

    def cite(self, step: str | None = None) -> str:
        pin = dict(self.pinpoints).get(step or "", "")
        return f"{self.short_title} ({self.ds}), {self.reports}" + (f", {pin}" if pin else "")


PROVISIONS: dict[str, Provision] = {p.id: p for p in [
    Provision("I", "Article I – Scope and definition",
              "GATS applies to measures by Members affecting trade in services. Measures by central, regional or local "
              "governments and by non-governmental bodies exercising delegated powers are covered (I:3(a)). Trade in "
              "services is supplied through four modes (I:2). Services supplied in the exercise of governmental "
              "authority (neither on a commercial basis nor in competition) are excluded (I:3(b)-(c))."),
    Provision("II", "Article II – Most-favoured-nation treatment",
              "Each Member must accord to services and service suppliers of any other Member treatment no less "
              "favourable than it accords to like services and suppliers of any other country. The obligation applies "
              "whether or not specific commitments exist, subject to listed Article II exemptions."),
    Provision("V", "Article V – Economic integration",
              "Permits preferential agreements with substantial sectoral coverage that eliminate substantially all "
              "discrimination among the parties."),
    Provision("VI", "Article VI – Domestic regulation",
              "In committed sectors, measures of general application must be administered reasonably, objectively and "
              "impartially (VI:1). Qualification and licensing requirements and technical standards should be based on "
              "objective and transparent criteria and not be more burdensome than necessary to ensure the quality of the "
              "service (VI:4-5). The 2021 Reference Paper on Services Domestic Regulation adds disciplines for the "
              "Members that scheduled it (in force since 27 February 2024)."),
    Provision("XVI", "Article XVI – Market access",
              "In committed sectors and modes, a Member may not maintain or adopt the six types of measure listed in "
              "XVI:2 unless inscribed as a limitation: limits on (a) the number of suppliers, (b) the value of "
              "transactions or assets, (c) the number of operations or quantity of output, (d) the number of natural "
              "persons employed, (e) measures restricting or requiring specific types of legal entity or joint venture, "
              "and (f) limits on foreign capital participation. The list is exhaustive."),
    Provision("XVII", "Article XVII – National treatment",
              "In committed sectors, subject to inscribed conditions, a Member must accord foreign services and "
              "suppliers treatment no less favourable than its own like services and suppliers. Formally identical or "
              "different treatment is less favourable if it modifies the conditions of competition in favour of domestic "
              "services or suppliers (XVII:2-3)."),
    Provision("XIV", "Article XIV – General exceptions",
              "A measure otherwise inconsistent with GATS may be justified if it falls under paragraphs (a)-(e) and "
              "meets the chapeau: (a) necessary to protect public morals or maintain public order; (b) necessary to "
              "protect human, animal or plant life or health; (c) necessary to secure compliance with GATS-consistent "
              "laws or regulations, including on (i) deceptive and fraudulent practices or default on contracts, "
              "(ii) the privacy of individuals in the processing and dissemination of personal data, (iii) safety; "
              "(d) differential direct taxation (Article XVII only); (e) double-taxation agreements (Article II only). "
              "Footnote 5: the public order exception may be invoked only where a genuine and sufficiently serious "
              "threat is posed to one of the fundamental interests of society."),
    Provision("XIV_chapeau", "Article XIV – Chapeau",
              "The measure must not be applied in a manner that would constitute a means of arbitrary or unjustifiable "
              "discrimination between countries where like conditions prevail, or a disguised restriction on trade in "
              "services."),
    Provision("XIVbis", "Article XIV bis – Security exceptions",
              "Nothing prevents a Member from taking action it considers necessary for the protection of its essential "
              "security interests (i) relating to the supply of services for provisioning a military establishment, "
              "(ii) relating to fissionable and fusionable materials, or (iii) taken in time of war or other emergency "
              "in international relations."),
    Provision("FS_2a", "Annex on Financial Services, paragraph 2(a)",
              "A Member may take measures for prudential reasons, including to protect investors, depositors or "
              "policy-holders or to ensure the integrity and stability of the financial system. Such measures may not "
              "be used as a means of avoiding the Member's commitments or obligations."),
]}

CASES: dict[str, Case] = {c.id: c for c in [
    Case("EC-Bananas", "EC – Bananas III", "DS27", "Appellate Body Report, WT/DS27/AB/R (1997)",
         "Confirmed the broad reach of 'affecting' trade in services and that Articles II and XVII cover de facto as "
         "well as de jure discrimination.", _ds(27)),
    Case("Canada-Autos", "Canada – Autos", "DS139/DS142", "Appellate Body Report, WT/DS139/AB/R (2000)",
         "Set out the analysis under Article II: first whether the measure is covered by GATS, then whether it "
         "accords less favourable treatment to like services or suppliers of some Members.", _ds(139)),
    Case("Mexico-Telecoms", "Mexico – Telecoms", "DS204", "Panel Report, WT/DS204/R (2004)",
         "Applied Article XVI to measures restricting cross-border supply and interpreted the Reference Paper on "
         "basic telecommunications.", _ds(204)),
    Case("US-Gambling", "US – Gambling", "DS285", "Appellate Body Report, WT/DS285/AB/R (2005)",
         "A prohibition on the supply of a committed service through a mode is a 'zero quota' within Article "
         "XVI:2(a) and (c). Public morals/order under XIV(a) covered the US gambling laws; on necessity, a "
         "complainant's alternative is not 'reasonably available' if merely theoretical or unduly burdensome. "
         "The US failed the chapeau because remote betting on horse racing was permitted for domestic suppliers.",
         _ds(285), (("exceptions", "paras. 304-311"),)),
    Case("China-Publications", "China – Publications and Audiovisual Products", "DS363",
         "Appellate Body Report, WT/DS363/AB/R (2009)",
         "Found national treatment violations in the distribution of audiovisual services and interpreted scheduled "
         "sectors in light of their ordinary meaning and evolving technology.", _ds(363)),
    Case("China-EPS", "China – Electronic Payment Services", "DS413", "Panel Report, WT/DS413/R (2012)",
         "Clarified the scheduling of market access and national treatment commitments and that a monopoly-type "
         "requirement can be a limitation on the number of suppliers under XVI:2(a).", _ds(413)),
    Case("Argentina-FS", "Argentina – Financial Services", "DS453", "Appellate Body Report, WT/DS453/AB/R (2016)",
         "Likeness under Articles II and XVII concerns the competitive relationship of services and suppliers; "
         "where a distinction is based exclusively on origin, likeness may be presumed. Less favourable treatment "
         "means a modification of the conditions of competition. Also addressed the prudential carve-out.",
         _ds(453)),
    Case("Korea-Beef", "Korea – Various Measures on Beef", "DS161/DS169", "Appellate Body Report, WT/DS161/AB/R (2001)",
         "Necessity (GATT Article XX(d), applied by analogy under GATS XIV) involves weighing and balancing the "
         "importance of the interests protected, the contribution of the measure and its trade-restrictiveness, and "
         "asking whether a reasonably available, less restrictive alternative exists.", _ds(161),
         (("exceptions", "paras. 161-166"),)),
    Case("Brazil-Tyres", "Brazil – Retreaded Tyres", "DS332", "Appellate Body Report, WT/DS332/AB/R (2007)",
         "A measure's contribution to its objective must be material, not marginal, especially for highly "
         "trade-restrictive measures such as bans; the chapeau looks at the cause and rationale of discrimination.",
         _ds(332)),
    Case("Mexico-Soft-Drinks", "Mexico – Taxes on Soft Drinks", "DS308", "Appellate Body Report, WT/DS308/AB/R (2006)",
         "'Laws or regulations' in the compliance exception (GATT XX(d), analogous to GATS XIV(c)) refers to rules "
         "forming part of the domestic legal system of the Member.", _ds(308)),
    Case("Colombia-Textiles", "Colombia – Textiles", "DS461", "Appellate Body Report, WT/DS461/AB/R (2016)",
         "Set out the two-step test for the compliance exception: the measure must be designed to secure compliance "
         "with laws or regulations and be necessary to do so.", _ds(461)),
    Case("EC-Seals", "EC – Seal Products", "DS400/DS401", "Appellate Body Reports, WT/DS400/AB/R (2014)",
         "Members may set their own level of protection for public morals; the chapeau requires examining whether "
         "discrimination can be reconciled with the policy objective.", _ds(400)),
    Case("US-Shrimp", "US – Shrimp", "DS58", "Appellate Body Report, WT/DS58/AB/R (1998)",
         "The chapeau prevents abuse of exceptions; rigid, unilateral application without considering conditions in "
         "exporting countries can be arbitrary or unjustifiable discrimination.", _ds(58)),
    Case("Russia-Transit", "Russia – Traffic in Transit", "DS512", "Panel Report, WT/DS512/R (2019)",
         "The security exception (GATT XXI, which GATS XIV bis mirrors) is not entirely self-judging: panels review "
         "whether the circumstances in the sub-paragraphs objectively exist and whether the measure meets a minimum "
         "requirement of plausibility in good faith.", _ds(512)),
]}


def provision(pid: str) -> Provision:
    return PROVISIONS[pid]


def case(cid: str) -> Case:
    return CASES[cid]
