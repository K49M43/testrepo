# Investment Engine — Reconciled Audit and Delivery Plan

**As of:** 4 November 2026; current-status reconciliation appended 4 November 2026
**Planning inputs:** Consolidated Research Proposal v3.0 and Independent Audit, both dated 3 November 2026
**Repository snapshot inspected for original audit:** branch `codex/sprint1-increment3-event-ledger-20261103`, commit `3037d4b` (`Record Sprint 1 source trace CI results`)
**Latest verified remote snapshot:** `main` merge commit `2c5bd7b42a823d4044ed0d583956e5c8b77e0bed` (PR #14); both Sprint 1 workflows passed. The full roadmap below remains a planning baseline; see Section 14.2 for the updated Sprint 1/Sprint 2 state.
**Purpose:** reconcile the proposal with the repository's controlling mandate and observed implementation; define an incremental, reviewable route to a useful investment decision.
**Decision status:** **NO-GO for investment authorization.** This document does not approve a target change, guarantee, portfolio, forecast, or trade.

## Executive assessment

The proposal improves the program's framing by separating feasibility, achievable alternatives, model uncertainty, implementation, and investor authorization. Its strongest additions are the inverse/achievable-frontier question, explicit distinctions between opportunity and realizable wealth, protection against simulation overconfidence, independent evaluation, and the continuous Question, Challenge & Scientific Assurance Engine (QCSAE).

The proposal is a planning design, not a description of the current code. The repository is a focused Python research archive with stage-specific scripts, CSV/JSON evidence, markdown governance, and GitHub Actions workflows. It has no integrated instrument registry, model/experiment registry, simulation runner, optimizer, claim graph, or decision application. Sprint 1 supplies a deterministic tax-component and event/lot-ledger prototype, but its terminal outputs are synthetic fixtures. Several acceptance requirements remain unresolved.

One proposal statement conflicts with the repository's investor-controlled source of truth. The mandate defines **₹90 lakh of 2026 purchasing power as a planning-floor objective, not a contractual guarantee**, and **₹1 crore as a stretch goal**. Proposal v3 calls the ₹90 lakh floor a contractual hard requirement and the ₹1 crore goal the target. This plan preserves the declared mandate pending explicit investor amendment. A separate study may examine whether an enforceable CPI-linked guarantee is available and what it costs; it must not relabel the objective or make a guarantee a newly accepted investor requirement.

The recommended delivery method is **incremental construction with iterative challenge and correction**. Keep the 2036 decision as the primary outcome. Build only the smallest components needed to resolve decision-material uncertainty; do not start with services, a generic simulation framework, an optimizer, or UI. Run QCSAE from the first work item using versioned claims, questions, tests, decisions, and links in the existing repository conventions; automate it only when repeated use demonstrates value.

## 1. Mandate reconciliation

| Topic | Repository source of truth | Proposal v3 wording | Reconciled treatment |
|---|---|---|---|
| ₹90L real after-tax amount | Planning-floor objective in 2026 purchasing power; explicitly not guaranteed | “Original hard requirement”: contractually guaranteed CPI-linked floor | Keep it as an objective for probabilistic/conditional feasibility analysis. Separately investigate a contractual guarantee as an optional feasibility question. Do not change mandate semantics without investor approval. |
| ₹1Cr real amount | Stretch goal | Original real-wealth target | Preserve as stretch goal, not the sole or revised primary target. Report ₹90L and ₹1Cr separately. |
| 85% floor success | Aspirational model target, not validated or guaranteed | Around 15% failure tolerance appears as a prior preference needing definition | Do not use 15% as an approved risk limit until the investor defines the event, time window, and whether it is binding. Show any 85% calculation as an unvalidated aspiration until model gates pass. |
| 2036 timing | Calendar year 2036; October liquidation is not mandatory | October 2026 purchasing-power base, 2036 valuation/realization/settlement dates to distinguish | Preserve calendar-year flexibility. Compare explicit valuation, decision, sale, and settlement dates; confirm investor dates before an investor-specific result. |
| Contributions | ₹42L initial; ₹25k month-end convention, 10% step-up every 12 payments; no expected interruption | Same economics, with exact initial/SIP dates to verify | Keep frozen schedules as math fixtures. Do not invent actual transaction dates. Interruption cases remain optional sensitivities, not baseline blockers. |
| Risk preference | Disciplined risk assessment desired; drawdown/loss tolerance unconfirmed | Approx. 15% failure preference cited but not formally registered | No suitability claim or single “best” strategy until the investor defines the relevant loss event and tolerances. |
| Use of model results | Decision support; only investor can approve transactions | Decision menu and conditional alternatives | Adopt a decision menu with explicit evidence status. Model completion and a conditional alternative never authorize a purchase. |

**Mandate change control:** if the investor intends a contractual ₹90L CPI-linked guarantee, record that as an explicit amendment, including exact index, date, legal enforceability, eligible instrument, funding source, counterparty and acceptable cost. Until then, the guarantee analysis is a separate question, not an adopted hard constraint.

## 2. AS-IS repository and evidence assessment

### Repository and architecture

- The inspected checkout is the Sprint 1 branch at `3037d4b`; its local `origin` tracking ref matched that commit and the working tree was clean during this audit. This verifies the local Git snapshot only. GitHub Actions for `3037d4b`, live PR review state, and the current issue backlog were not independently verified in this audit.
- Governance and decision intent live in `AGENTS.md`, the mandate, evidence/model standards, decision gates, handoff, execution plan, sprint tracker, and decision logs. These are the strongest current architecture: written boundaries, scoped evidence claims, NO-GO state, and acceptance gates.
- Research is organized as historical stages, with Python scripts plus CSV/JSON results and source captures. There are many narrow GitHub Actions workflows, including the source and Sprint 1 audit workflows. This supports discrete reproducible checks but does not yet provide one versioned end-to-end experiment contract.
- The current implementation is script-oriented, not a deployable engine. No evidence was found for a package/release API, persistent database, optimizer service, generic plugin system, dashboard, or automated investment execution. This is appropriate for the immediate decision work; preserve that restraint.
- The proposal's component names (`InstrumentContract`, `ModelSpec`, `ExperimentSpec`, `FrontierResult`, etc.) are useful vocabulary, not evidence that these abstractions should be implemented now. Introduce typed boundaries only where two concrete uses or a correctness risk justify them.

### Current capability and evidence maturity

| Area | Observed current state | Scope and unresolved limit |
|---|---|---|
| Historical sources | 129 monthly official NSE Nifty 500 TRI anchors; 2,867 official AMFI NAV observations for LIC MF Nifty 8–13y G-Sec ETF; 165 linked/direct MoSPI CPI levels through Sep 2026; 437 RBI-origin bullion reference months from a secondary mirror with sampled official checks | These panels are not one complete official, investable, synchronized multi-asset history. Continuous NSE G-Sec TRI is not qualified; RBI bullion is not fully first-party recovered; fund NAV differs from ETF market price; actual candidate instruments and execution data remain unconfirmed. |
| Statistical research | Historical calibration, forward scenario, model-uncertainty, and predictive-validation artifacts exist. The predictive-validation report explicitly records a severe Gaussian downside miss in March 2020, overlapping-window dependence, and no validated 2036 success probability. | Scenario frequencies remain conditional on assumptions. There is little independent long-horizon evidence; additional Monte Carlo paths cannot resolve model-form, parameter, or representativeness uncertainty. |
| Deterministic cashflows | Frozen 120/122-month contribution schedule and hurdle calculations exist. | Timing and amount schedules are fixtures until exact investor dates are supplied; baseline is pre-tax/pre-cost and not a forecast. |
| CPI | CPI source-vintage checks reconcile 144 linked historical observations and 21 direct observations to transcribed official tables at published precision. | Raw original release bytes are not preserved; source capture hashes identify local transcriptions. Personal cashflow/base month is unconfirmed; real investor wealth is not qualified. |
| Tax | TY 2026–27 tax components use decimal arithmetic, explicit eligibility gates, and arithmetic examples; the prototype distinguishes annual tax from withholding credit. | This is a bounded current-law fixture, not a 2036 law forecast or personal tax result. Mixed special-income surcharge relief, losses/set-offs, statutory rounding, actual external income, complete instrument classifications, and qualified tax-professional review remain open. |
| Event/lot ledger | Event-level synthetic fixture models contributions, lots, income, costs, withholding, disposals and source IDs; terminal reconciliation compares synthetic fund, staged-sale and direct-bond cases. | A small fixture does not validate general lot handling, corporate actions, accrued interest, settlement, all loss/set-off cases, actual market pricing or investor taxes. The bond is par-priced with an invented 5% coupon; fund appreciation is invented; fees are zero; 2026–27 law is held constant. |
| QCSAE | Existing gate ledger, source citations, decision logs, and review process are useful foundations. | No structured question/claim/evidence dependency and invalidation system exists yet. Continuous independent challenge is a process requirement, not an implemented engine. |
| CI and release | Workflows encode several source and arithmetic audits. On PR #12 head `7c8dacb`, the earlier recorded four checks passed. | Commit `3037d4b` was pushed, but the new Actions state was not verified. Do not roll forward the earlier 4/4 status to the new commit. |

### Confirmed design/model findings and status

The audit's F01–F12 remain useful identifiers, but status must follow repository evidence and scope:

| Finding | Reconciled status | Required disposition |
|---|---|---|
| F01 contractual real floor | **Mandate conflict / unresolved**, not an adopted investor requirement | Preserve the mandate wording. Analyze enforceable guarantee feasibility separately; do not imply a stochastic model can meet a contractual guarantee. |
| F02 uncalibrated probability | **Confirmed limitation** | Publish model-conditional results only; keep real-world probability claims blocked absent independent calibration and defensible context of use. |
| F03 synthetic scenario labeled “Historical 11.8% replay” | **Confirmed defect** in `research/stage512/2026-11-02/stage512_risk_audit.py`: the scenario sets an assumed 11.8% geometric equity return and generates synthetic shocks | Preserve the old artifact, mark/restate its classification with a dated correction, and create a separate observed-history replay from eligible dated series. Never call the synthetic scenario historical. |
| F04 cross-stage CPI/horizon inconsistency | **Confirmed comparability risk**, partly reduced by later mandate/CPI work | Make each experiment declare contribution count, first/last flow dates, valuation/realization/settlement dates, CPI base/vintage, and inflation convention. Reconcile before comparing; never rewrite historical results. |
| F05 tax approximation and interactions | **Partially improved, still open** | Finish statutory edge cases and instrument/date classification; independently reconcile taxes and credits; get qualified review before tax-qualified claims. Do not use a universal marginal-rate shortcut. |
| F06 synthetic/non-executable sleeves | **Confirmed scope limitation** | Separate reference benchmarks from investable instrument returns; verify point-in-time identifiers, product status, execution route, economics, and tax classification before candidate ranking. |
| F07 tests too narrow for full model | **Confirmed** | Keep component checks, then add independent golden examples, property/metamorphic and adversarial integration checks. CI pass only supports the exact tested commit and scope. |
| F08 optimizer selection leakage | **Prospective design risk**; no current optimizer evidenced in this checkout | Require a trial registry and independent evaluation set before optimization is introduced. Do not build an optimizer until baseline policies and evaluation protocol exist. |
| F09 invalid adaptive stopping | **Prospective design risk**; no current assurance controller evidenced | Start with fixed, preregistered batches. Use sequential methods only after a precise estimand, valid method, coverage tests, multiplicity treatment, and stop protocol are specified. |
| F10 point-in-time data quality | **Partially improved, still open** | Preserve provenance/availability/instrument-history limits, source bytes or durable captures where lawful, corporate-action/calendar conventions, and first-party verification. Do not imply a complete investable panel. |
| F11 seed-only reproducibility | **Confirmed gap for a unified engine** | Pin code, inputs, configuration, dependency/environment, RNG stream allocation, output and validation artifacts in a run manifest. A seed alone is insufficient. |
| F12 research scope can delay decision | **Confirmed program risk** | Maintain decision-first prioritization, explicit compute/research budgets, materiality rationale and stop rules. Reject research without a defined decision consequence. |

## 3. Independent challenge of Proposal v3

### Retain

- Separate hard contractual protection, investor needs, aspirational goals, model-risk preferences, and implementation feasibility.
- Treat “strict” and “conditional alternative” analyses separately, and allow `INCONCLUSIVE` or `INSUFFICIENT_EVIDENCE`.
- Distinguish terminal wealth, target touched, executed realization, settled proceeds, and enforceable protection.
- Separate observational, parameter, model-form, Monte Carlo, and decision/ranking uncertainty.
- Keep an explicit comparison set including no deployment, simple baselines, and candidate strategies; track all model/optimizer trials.
- Use mathematical-first research across relevant disciplines, with a simple baseline and demonstrated decision value before adopting sophisticated or original methods.
- Make QCSAE continuous, falsifiable, independently adjudicated, and able to invalidate dependent findings.

### Correct or narrow before implementation

1. **Do not silently redefine the mandate.** The proposal's guarantee/target hierarchy conflicts with the signed-off repository mandate as documented. The crosswalk in Section 1 controls this plan until the investor changes it.
2. **Do not overstate robust optimization.** The proposed `inf_{P in Pset}` guarantee-like criterion is only informative if the ambiguity set is constrained and justified. An excessively broad `Pset` makes results vacuous; an overly narrow one hides model risk. Report sensitivity across explicit model sets and avoid calling the result a calibrated probability.
3. **Do not turn the inverse frontier into a hidden utility function.** A maximum supported goal at a chosen failure limit can select a corner policy with unacceptable drawdown, liquidity, or implementation burden. Keep a vector/Pareto menu and investor-defined constraints; don't optimize a single scalar until preferences are explicit.
4. **Separate mathematical feasibility from empirical support.** A computed strict feasible set being empty under selected assumptions means `MODEL_INFEASIBLE` or `INSUFFICIENT_EVIDENCE`, not proof that no real-world product could satisfy the requirement. Reserve `PROVEN_INFEASIBLE` for a defensible certificate covering the stated instrument/contract universe.
5. **Specify wealth and time accounting before defining `Y`.** State the CPI numerator/base, tax payment timing, accrued income, transaction costs, unsettled trades, withdrawal policy, redemption restrictions and settlement date. Use a single explicit valuation convention and retain tax liabilities/cash outside portfolio wealth without double-counting them.
6. **Treat year-2036 opportunity metrics as policy simulations.** `P(max_t Y(t) >= g)` is not directly useful unless the policy observes prices, chooses a sale, pays tax/costs, and settles proceeds. Preserve it as a diagnostic, not the success criterion.
7. **Do not use overlapping windows as independent validation samples.** Report dependence and effective evidence limits; time-series resampling and model stress do not create new independent decades or establish future calibration.
8. **Defer QCSAE automation.** Start with a compact, human-reviewable record and explicit links in the existing gate/decision log. The relational database for financial inputs/runs is now separately required; defer a graph database, graph service, AI scoring, or orchestration for QCSAE until actual repeated challenge workflows show those are necessary. Independent evidence cannot be replaced by agent plurality.
9. **Avoid duplicating gates.** The repo already has G0–G5 gates. Map the proposal's G0–G7 and GQ onto them with a crosswalk rather than creating two parallel release taxonomies. Add implementation/approval sub-gates only where the current definitions are incomplete.
10. **Treat external literature references as leads.** Verify exact methods, assumptions and applicability before making them implementation requirements. Do not add a method because it appears in a bibliography.

## 4. TO-BE architecture — decision-first and deliberately small

Use one reference case (the 2036 mandate) and the following logical boundaries. Keep the calculation engine in Python initially, but move canonical structured inputs, source observations, event ledgers, and run/result records into a versioned relational database through a small parity-tested migration. JSON/CSV remain import/export and evidence formats, not the live source of truth for repeated computation. Excel is not the production calculation layer.

1. **Mandate and decision contract:** versioned goals, dates, cashflows, risk semantics, hard/soft constraints and unknowns. The written mandate remains authoritative; fixture assumptions are separately labeled.
2. **Evidence and instrument catalog:** source identity, retrieval/observation times, transformations, hashes, units, calendar, vintage, instrument identity, return convention, lifecycle/inception and evidence grade. Distinguish benchmark, proxy, fund NAV, traded price and direct security.
3. **Deterministic accounting core:** dated cash, holdings, lots, accrued income, costs, tax liability/credits, settlement and CPI conversion. Keep a simple reference implementation and independent calculation fixtures. No simulation dependency.
4. **Model and experiment records:** model assumptions/domain of validity; scenario and policy definition; data/code/config/environment hashes; RNG stream plan when stochastic; preregistered estimands, validation set and stopping rule.
5. **Research components:** observed historical replay, scenario/stress analysis, then stochastic model alternatives. Each has an explicit context of use and separate output status. Retain legacy scripts and immutable artifacts.
6. **Statistical assurance:** report all five uncertainty classes; distinguish model-conditional numerical precision from predictive calibration and decision stability. Start with fixed batches and independent evaluation; add adaptive sampling only after coverage validation.
7. **Frontier and comparison:** strict requirement screen, conditional alternatives, explicit no-deployment/simple baselines, outcome vectors, sensitivity, implementation feasibility and materiality. No one-number rank unless investor preferences justify it.
8. **QCSAE control record:** claims, material questions, hypotheses, falsification tests, evidence, independent result, disposition, dependents and invalidation. Begin as versioned structured files/log entries; each phase must show its challenge and disposition. AI may propose challenges, never certify them.
9. **Decision and report:** reproducible decision pack with scope-limited claim status, gate ledger, limitations, feasible alternatives and human review. CLI/report tooling only when it materially improves repeatability. No trading, broker credential access or automatic orders.
10. **Relational persistence and compute boundary:** the database owns validated, versioned input/evidence references, ledger events, experiment/run manifests, and computed outputs. Python loads a consistent immutable run snapshot, performs numerical calculations outside the database, and commits results and manifest atomically. Use SQL constraints, indexes, and set-based queries for integrity and retrieval; do not run path simulation as row-by-row SQL or spreadsheet formulas. Start with a local SQLite pilot for single-user use; choose a server database only if verified concurrency/operations needs require it.

**Abstraction rule:** the relational store is now an explicit user requirement and should be piloted; this does not authorize service architecture, universal stochastic kernels, plugin frameworks, persistent graph databases, or dashboards. Add those only after concrete use cases demonstrate a correctness or maintenance benefit. Typed Python contracts are appropriate when they protect financial invariants or are used by multiple real components.

## 5. Dependency-aware implementation roadmap

Delivery is incremental; each increment includes an iterative challenge/refinement loop. Work may overlap only when the dependency is truly independent.

| Phase | Work and output | Depends on | Exit evidence |
|---|---|---|---|
| 0. Reconcile baseline and claim inventory | This mandate crosswalk; commit/PR/CI verification; index each prior result as fact, historical observation, synthetic fixture, conditional model output or unresolved claim. Preserve artifacts and supersede by dated correction. | None | Local and remote revisions clearly distinguished; every material Stage 5.12/Sprint 1 claim has scope and next challenge. |
| 1. Finish deterministic accounting qualification | Complete Sprint 1 tax/lot/terminal mechanics with independent golden examples, edge tests, tax-year/date boundaries, losses/set-offs, fractional lots, multiple disposals, fees, withholding, and cash/holding conservation. Split fixture correctness from personal-tax qualification. | Phase 0; current Sprint 1 code | Exact arithmetic reconciles independently; unknown classifications fail closed; no investor result claimed. Qualified professional review is an external acceptance input, not a coding substitute. |
| 1a. Database-backed compute pilot | Define versioned relational schema/migrations for the current synthetic fixture only; load a consistent snapshot, run existing Python calculations outside the database, and persist outputs/manifest transactionally. Keep legacy evidence files and do not bulk-migrate historical archives. | Phase 1 fixture contract; may use current fixture while investor-specific tax questions remain open | Clean database rebuild and migrations; database-run outputs match existing fixture and independent golden calculations exactly; content/config/code hashes and failure rollback are demonstrated. This proves the data/compute boundary, not faster performance or workbook replacement. |
| 2. Freeze mandate/time and instrument contracts | Resolve only consequential investor semantics when needed; record unconfirmed values. Build a small candidate/evidence matrix for actual investable routes including equities, direct/rolling sovereigns, gold, silver and alternatives. Preserve benchmark/proxy boundaries and determine availability/cost/tax at as-of dates. | Phase 0; accounting conventions from Phase 1 | Each candidate has stable identity, data/return convention, buy/hold/exit route, costs/taxes, lifecycle and explicit missing evidence. No fabricated pre-inception histories. |
| 3. Repair retrospective claim integrity and qualify evidence | Dated correction for synthetic “Historical 11.8% replay”; true observed-history replay only from qualified aligned data. Complete unresolved primary-source evidence for direct G-Sec TR and bullion where available; preserve limits where unavailable. | Phase 0; relevant qualified series from Phase 2 | Historical labels match data generation; no look-ahead; transformations and exclusions reconcile; data limitations are explicit. |
| 4. Prespecify models and assurance | Freeze estimands, model alternatives, train/evaluation split, trial count, comparison protocol, risk metrics, compute budget and fixed stopping batches before rerunning/optimizing. Calibrate models against available data and record irreducible long-horizon limitations. | Phases 1–3 | Independent evaluation not reused for tuning; model vs numerical uncertainty separated; tail and model disagreements reported; no unsupported 2036 probability claim. |
| 5. Produce the achievable-outcome menu | Compare strict contractual guarantee feasibility (as a separate question), original planning-floor and stretch goals, no-deployment and simple/eligible alternatives. Estimate conditional outcome frontiers, downside severity, costs, tax, real wealth and sensitivity only at supported evidence level. | Phases 1–4; mandate/risk semantics | Results are per model and policy; assumptions and alternative models visible; “empty” states distinguish proven infeasibility, model infeasibility and insufficient evidence. No hidden objective substitution. |
| 6. Decision pack and independent review | Assemble reproducible decision memo, evidence and gate ledger, source manifests, instrument execution checks, tax/suitability review and all QCSAE findings. Present `NO-GO`, `INCONCLUSIVE`, or conditional candidates honestly. Investor alone decides whether to amend objective or authorize action. | Phase 5 | Every readiness claim is independently reviewed; material gates pass within scope; no unsupported guarantee or investment authorization. |

QCSAE runs **across Phases 0–6**, not as a final gate. At every phase, record at least one material challenge, the test/evidence, result, unresolved issue, affected claims, and whether prior dependent claims need invalidation. If no material challenge is warranted, record why.

### Execution sequence and working cadence

Run the work in this order. A phase can be split into small PRs, but its exit evidence must exist before dependent phases are promoted.

**Step 0 — Re-establish the live development baseline**

1. Use GitHub CLI to inspect the repository default branch, open issue #3, PRs #11/#12, current base/head relationships, exact head SHAs, review state, and Actions runs. The local snapshot does not prove live GitHub state.
2. Record which changes are merged, draft, awaiting review, or pending CI. Keep `3037d4b` distinct from the earlier passing `7c8dacb`.
3. Decide the branch point for new work only after identifying whether the Sprint 1 draft is stacked and whether its parent PR changed. Do not merge or retarget PRs automatically.
4. Review this plan and turn its proposed issue specifications into a dependency-linked GitHub backlog only when explicitly directed. Keep issue #3 as the umbrella unless the owner chooses otherwise.

**Exit:** one current-state record with verified remote SHAs, PR dependency graph, issue links, exact CI outcomes, and next unblocked issue. If CLI authentication is not complete, remote facts stay marked unverified.

**Step 1 — Close Sprint 1 as a fixture-qualified accounting component**

1. Freeze the existing synthetic input contract and outputs as regression fixtures; do not rewrite them to make new examples pass.
2. Add independent, separately calculated golden cases for: zero return/cost; contribution step-up; two lots and multiple partial disposals; FIFO or explicit lot-selection policy; the exact statutory long/short cutoff; cross-tax-year income; losses and set-off; surcharge/marginal relief; statutory rounding; withholding versus liability; bond accrued interest/coupon/reinvestment; settlement delay; and CPI conversion.
3. For each change, write the expected amount and units before running candidate code. Reconcile cash, positions, tax liabilities and unsettled proceeds at each event and terminal checkpoint.
4. Keep law/version-specific tests separate from ledger mechanics. Unknown instrument identity or eligibility must reject the tax branch instead of guessing.
5. Ask for missing investor dates/tax facts only for calculations that need them. Do not block synthetic engine correctness on personal data.

**Exit:** independent arithmetic agrees within documented rupee precision; negative/adversarial cases fail safely; exact code and CI revision are recorded. Personal tax and tax-professional approval remain separate gates.

**Step 1a — Persist one qualified fixture and run it through the database-backed Python boundary**

1. Create versioned schema migrations for only the existing synthetic input contract, source/evidence references, event rows, run configuration/manifest and result rows. Keep migrations and golden fixtures in Git; keep the live database file and any licensed or large source data outside Git.
2. Canonicalize the run snapshot before hashing: include schema version, stable row order, units, source/version references, configuration and all calculation-relevant values. Record raw-source retention/licensing status; where raw storage is not permitted, retain allowed references, hashes and transformations.
3. Load the fixture in a transaction; Python computes from a consistent read snapshot without row-by-row database calls. Persist the completed result and manifest atomically; failed/interrupted runs remain explicitly failed and cannot look complete.
4. Re-run the same deterministic fixture from a clean rebuild and from an unchanged database snapshot. Reconcile every numeric output to the current script output and independent expected values; inspect that a source/config/schema change creates a distinct run identity.
5. Record load time, compute time and persistence time as diagnostic baselines. Do not claim a speed gain in this step; E2 owns comparative workload and target after the workbook is identified.

**Exit:** clean rebuild, repeatable migrations, stable snapshot hash, exact deterministic parity, and failure atomicity. This pilot does not retire Excel or qualify a forecast.

**Step 2 — Freeze decision semantics and evidence contracts**

1. Maintain the Section 1 mandate crosswalk as the approved planning interpretation; log a separate open question if the owner wishes to change guarantee semantics or the 15% event threshold.
2. Define common date fields: cashflow date, price observation date, trade date, settlement date, tax realization date, valuation date, goal-window date, and CPI publication/base date.
3. Define common units and return conventions: INR versus paise, price versus total return, NAV versus traded price, gross/net of TER, coupon/accrued interest, nominal/real base, and source precision/rounding.
4. Create a compact evidence record for only decision-relevant inputs: original source or URL, retrieval/observation time, local raw/transcription status, hash, transformation, qualification, limitations, and dependent claims.
5. Preserve historical versions and allow a source update to invalidate dependent evidence without erasing prior runs.

**Exit:** a reader can tell what each observation means, when it was knowable, how it was transformed, and which result depends on it.

**Step 3 — Build the candidate instrument register and evidence plan**

1. Start with the mandate's minimum 10 serious candidate securities/strategies, including broad equity, differentiated equity, direct GoI maturity choices, rolling sovereign funds, gold, silver, defensive alternatives, and non-deployment.
2. For each candidate identify actual security/product, ISIN or scheme identifier, return source, start/end history, price/NAV/benchmark convention, TER/fees/spreads, taxes, minimum sizing, purchase route, liquidity/redemption, settlement, and point-in-time availability.
3. Separate the underlying economic exposure, benchmark proxy, and actual instrument implementation. Never splice a product's pre-inception observations onto its return history.
4. Mark missing first-party sources and lawful fallbacks; obtain only data that can change candidate eligibility or the decision frontier.
5. Rank evidence gaps by decision consequence and collection cost; record a stop condition when a source is unavailable or the proxy is not fit for purpose.

**Exit:** at least 10 candidate rows have a clear status (`eligible for research`, `proxy only`, `not eligible`, or `evidence blocked`) and the required evidence to advance each one is explicit. This is not yet a candidate recommendation.

**Step 4 — Repair historical claim labels and construct defensible retrospective evidence**

1. Publish a dated correction for the synthetic “Historical 11.8% replay” and link the affected scenario outputs, reports, and decisions.
2. Define the observed-history estimand and eligible universe before recomputation; align every return interval at both endpoints and state missing-data/exclusion rules.
3. Report asset availability and survivorship limitations at each historical date. For assets with short product histories, run separate benchmark-level and investable-product analyses; do not call them equivalent.
4. Separate true observed historical replay, block-resampled synthetic paths, parametric simulations, deterministic stress, and hypothetical forward assumptions in schemas and report labels.
5. Independently reconstruct at least one path from raw/qualified observations and cashflows.

**Exit:** a reproducible observed-data replay has no look-ahead or false historical label, or the report documents why a qualified replay cannot be produced. A replay does not by itself establish future calibration.

**Step 5 — Preregister model comparison and statistical assurance**

1. Define the estimands first: terminal after-tax real wealth at named 2036 dates; shortfall events/severity; path drawdown/liquidity; and any executable target-lock policy.
2. Specify data vintage, candidate return/inflation/dependence models, training/evaluation split, stress library, risk metrics, trial registry, RNG streams, compute ceiling and stop rules before results are opened.
3. Begin with transparent deterministic and simple stochastic baselines. Add alternative model families only when they address a material failure mode.
4. Report observations/parameter/model-form/numerical/decision uncertainty separately. Use path count only to reduce Monte Carlo error after evidence/model uncertainty has been assessed.
5. Use fixed staged batches first. If sequential sampling is later proposed, demonstrate coverage and error control under repeated synthetic experiments for the actual estimand; account for model selection, multiple comparisons, dependence and tail estimators.
6. Preserve a protected evaluation set. Any tuning or inspection that leaks it creates a new experiment and a new holdout requirement.

**Exit:** independent evaluation supports only a bounded model context; severe misspecification and model disagreement are visible; no unqualified real-world success probability is reported.

**Step 6 — Produce strict and conditional outcome frontiers**

1. Screen enforceable contractual guarantees separately; state whether evidence shows available, unavailable within the searched universe, or not established.
2. Analyze the original ₹90L floor objective and ₹1Cr stretch across no-deployment, simple portfolios and screened eligible strategies under the same dated ledger and cost/tax/CPI conventions.
3. Show nominal gross, realized taxes/costs, accessible net nominal, real value, downside magnitude, liquidity, settlement and implementation feasibility.
4. Compare results across defensible model/parameter sets and investor-defined risk constraints. Do not compress competing risk, liquidity, and wealth outcomes into an arbitrary single score.
5. Distinguish a target touched from a policy sale, cleared/settled proceeds, and contractual protection.
6. If candidates depend on unverified taxes, instruments, costs, risk tolerance, or CPI alignment, label the frontier conditional or incomplete and keep its gate blocked.

**Exit:** a decision menu has reproducible evidence and limitation paths for every candidate, including a valid `NO-GO`/`INCONCLUSIVE` outcome. No strategy is selected by default.

**Step 7 — Independent challenge, decision memo, and closure**

1. Have a reviewer who did not author the relevant model reproduce material accounting and challenge data/model/mandate interpretation.
2. Resolve, accept with bounded scope, or retain each high-severity challenge; propagate changed assumptions to dependent outputs and regenerate them.
3. Complete the existing decision gates with one traceable evidence ledger mapped to proposal gates, not duplicate checklists.
4. Deliver the investor memo and limitations, execution requirements, monitoring/review triggers, and alternative actions if goals fail.
5. Keep investment authorization separate. Any eventual investment action requires the investor's own explicit decision after reviewing the final packet.

**Exit:** independent reviewer can reconstruct the decision pack; all blockers are explicit; investment decision is `NO-GO`, `INCONCLUSIVE`, or ready for human consideration within a defined scope. No technical gate flips authorization automatically.

### Iteration and rollback rules

- Every PR changes one decision-relevant unit of work and names the claim/gate it affects. Prefer small deliverables that can be independently reviewed.
- Before implementation: write the hypothesis, failure mode, independent check, acceptance threshold, and dependent claims. After implementation: record observed result, not intended result.
- A failed check returns the work to its current step; preserve failed evidence, root cause, and revised test. Do not proceed by weakening acceptance criteria without recorded justification.
- A material change to mandate, tax law, data vintage, instrument mapping, model family, objective or evaluation set creates a new version and invalidates dependent outputs as needed.
- A source-access blocker gets a bounded retry/alternative plan and failure record; no blind loops, CAPTCHA bypass, or synthetic gap filling.
- Stop research when remaining uncertainty cannot be reduced economically or cannot change the decision; record `INSUFFICIENT_EVIDENCE` or `INCONCLUSIVE` rather than extending the architecture.
- New GitHub issues document proposed work; creating public issues, editing descriptions, merging, or closing PRs requires the relevant user authorization. Never merge solely because checks pass.

## 6. Proposed GitHub issue breakdown

These are draft issue specifications, not created GitHub issues. Keep umbrella issue #3 as the decision-program tracker unless repository owners choose another hierarchy. Each issue should link its evidence and update the existing tracker/decision log. Assign owners only after confirming repository permissions and availability.

### A. Baseline and mandate

**Issue A1 — Reconcile proposal v3 with the investor mandate and freeze outcome semantics**
Priority: P0 · Depends on: none · Owner: decision owner + engineering maintainer
Scope: adopt the crosswalk in this plan; define terminal/opportunity/realizable/settled outcomes, separate goal from guarantee, preserve unknowns, define the status vocabulary.
Acceptance:
- Written mandate values, goal priority, dates, hard/soft constraints and unknowns match the approved investor mandate.
- ₹90L remains a planning-floor objective and ₹1Cr remains stretch unless the investor explicitly amends the mandate.
- Contract-guarantee feasibility is recorded as a distinct question with no probability substitution.
- Every legacy experiment has a date/horizon/CPI/cashflow crosswalk or is marked non-comparable.

**Issue A2 — Create claim and evidence inventory for decision-critical existing results**
Priority: P0 · Depends on: A1
Acceptance:
- Each retained result is classified as source fact, historical observation, synthetic fixture, assumption, conditional model output, recommendation or unresolved claim.
- Exact commit, inputs, transformations, output artifact, validation status, scope and limitations are recorded where evidence exists; unknowns are explicitly listed.
- No claim is promoted solely because its script, report or workflow exists.

### B. Deterministic finance and tax

**Issue B1 — Independently qualify cashflow, holdings, tax lots, costs and settlement invariants**
Priority: P0 · Depends on: A1
Acceptance:
- Independently hand-calculated cases cover contribution timing/step-up, acquisitions, multi-lot partial sales, lot aging at statutory cutoffs, income, reinvestment, loss/set-off, fees, withholding credits, fiscal-year boundary and settlement.
- Portfolio conservation reconciles cash + holdings + accrued items + liabilities at every checkpoint; no double taxation/cost or tax on unrealized gains.
- Unknown or unsupported security/tax classifications fail closed.
- Fixture outputs are labeled separately from actual-investor results; independent review is recorded.

**Issue B2 — Complete current-law tax rule coverage and professional review**
Priority: P0 · Depends on: B1 and instrument classifications
Acceptance:
- Primary statutory source/version/effective dates are pinned for each implemented component.
- Boundary and mixed-income/surcharge/marginal-relief, cess, loss/set-off, rounding, withholding-credit and relevant instrument tests reconcile to independent arithmetic.
- A qualified tax professional's reviewed worked examples, scope and date are recorded; until then any tax result remains explicitly provisional.
- Future law is represented as scenarios and never asserted as known.

### C. Evidence and model validity

**Issue C1 — Correct the synthetic “Historical 11.8% replay” claim and preserve prior results**
Priority: P0 · Depends on: A2
Acceptance:
- The dated source report identifies that the existing scenario uses an assumed 11.8% equity drift and generated shocks, not observed historical paths.
- Existing raw outputs remain preserved; any new labeling/correction is append-only and points to affected dependent claims.
- A separate historical replay uses only observed, date-aligned, qualified series and models point-in-time asset availability; unavailable assets are not backfilled.
- Synthetic and observed-history outputs cannot share a “historical replay” status.

**Issue C2 — Build a decision-relevant instrument and evidence register**
Priority: P0 · Depends on: A1; can proceed alongside B1
Acceptance:
- At least 10 candidate securities/strategies are screened at the mandate's required research level, with explicit benchmark/proxy/investable classification.
- Every candidate records identifier, as-of status, return convention, inception/history, distributions, costs, tax class, purchase/redemption route, liquidity and source provenance.
- Official Nifty500 TRI, direct/rolling sovereigns, gold and silver remain represented; material unavailable series are recorded as blocked, not substituted silently.
- No product is called executable until supported broker/market evidence is dated and verified.

**Issue C3 — Define and pin the statistical experiment protocol before new model comparisons**
Priority: P1 · Depends on: A2 and C2
Acceptance:
- Estimands, horizons, model alternatives, evaluation data, train/evaluation separation, metrics, trial registry, code/data/config/environment hashes and compute limits are preregistered.
- Stress, historical replay and model-based simulation are distinct experiment classes.
- Fixed staged sampling is the initial protocol; any sequential stopping method has a specified estimand and validated error/coverage behavior before use.
- Monte Carlo error, parameter/model/observational uncertainty and decision-ranking stability are reported separately.

**Issue C4 — Establish predictive-validity scope and benchmark model set**
Priority: P1 · Depends on: B1, C2, C3
Acceptance:
- Simple transparent baselines precede advanced models; at least two materially different plausible model families are compared on protected evaluation evidence.
- Tail misspecification, structural breaks, dependence, inflation/tax uncertainty, overlapping-window dependence and parameter uncertainty are explicitly tested.
- Model disagreement greater than simulation error triggers evidence/model work rather than path-count inflation.
- No real-world probability is described as calibrated without a defined population/context, calibration evidence and independent review.

### D. Frontiers and decision governance

**Issue D1 — Generate a separate strict-feasibility screen and conditional attainable frontier**
Priority: P1 · Depends on: A1, B1, B2, C2, C3, C4
Acceptance:
- The guarantee screen is separate from the original ₹90L planning-floor and ₹1Cr stretch-goal analysis.
- No-deployment, simple allocation, staged-entry/glide-path, fixed/rebalanced and other credible policies are compared with the same dated cashflows and cost/tax conventions.
- Results include gross nominal, tax/cost, net nominal, CPI conversion, real wealth, shortfall magnitude, liquidity and execution constraints at supported evidence level.
- Report a menu/vector of outcomes and model sensitivities; no scalar winner is selected without investor-defined preferences.
- Distinguish `PROVEN_INFEASIBLE`, `MODEL_INFEASIBLE`, `INSUFFICIENT_EVIDENCE`, `INCONCLUSIVE`, and conditional alternatives with explicit definitions and evidence.

**Issue D2 — Implement the minimal continuous QCSAE record and invalidation rules**
Priority: P1 · Depends on: A2; start process now, implement schema after two concrete claim workflows
Acceptance:
- Each decision-material claim links to question, hypothesis, falsification test, evidence, result, independent adjudication, scope and dependent claims.
- Material revisions create new versions and identify which downstream outputs must be recomputed or marked invalid.
- QCSAE tests detect the six proposal cases: unsupported assumptions, synthetic-history mislabel, model disagreement, infeasible guarantee, tax-rule invalidation and independent evidence requirements.
- AI-generated challenges cannot close a gate; no self-consensus or confidence score substitutes for evidence.

**Issue D3 — Independent readiness review and decision pack**
Priority: P0 at program close · Depends on: D1, D2
Acceptance:
- An independent reviewer can reconstruct all material outputs from pinned code, inputs, assumptions and instructions.
- Each G0–G5 gate has scope, state, evidence, limitations, next action and decision implication; mapped once to proposal G0–G7/GQ to avoid duplicate gate systems.
- Investor-facing memo distinguishes supported claims, conditional results, unresolved needs and decisions requiring investor confirmation.
- Actual trade approval remains separate and solely with the investor; no repository status changes it.

### E. Database-backed computation migration

**Issue E1 — Define the relational data contract and persist one deterministic run**
Priority: P1 · Depends on: B1 fixture contract; can begin with the existing synthetic ledger
Scope: pilot a small versioned relational schema for canonical fixture inputs, evidence/source references, event ledger, run manifest and results. Begin with local SQLite for single-user operation unless verified concurrency needs require another database.
Acceptance:
- Schema migrations are versioned, repeatable on a clean database, and reject invalid identifiers, units, dates, duplicate observations/events and broken references.
- Imported source/input records preserve source identity, as-of/availability dates, units, transformations and hashes; corrections create new versions rather than silently overwriting prior runs.
- Python reads a consistent run snapshot, computes outside the database, and writes outputs plus manifest atomically; a failed run leaves no partial result marked complete.
- Repeating the same deterministic fixture/config creates a traceable run and exactly reproduces its numeric outputs; no database-generated or spreadsheet formula silently changes a financial result.
- The existing file-based evidence remains preserved during the pilot; no bulk history migration is required to pass this issue.

**Issue E2 — Establish workbook parity and compute-performance evidence**
Priority: P1 · Depends on: E1 and a frozen representative workbook/calculation workload
Scope: inventory the workbook's formulas, inputs, outputs and rounding conventions; compare the database-backed Python path against independently frozen cases; measure input, compute and persistence costs separately.
Acceptance:
- Every in-scope workbook calculation has a named replacement function and a frozen representative case; outputs agree to a per-field tolerance justified by currency/unit/rounding semantics, with every mismatch resolved or explicitly excluded.
- Benchmark workload size, hardware/runtime environment, warm/cold state, repeats, and source versions are pinned; timings separate data load, numerical compute and result persistence.
- A target end-to-end workload and minimum useful improvement are preregistered before optimization. Claim “faster” only if repeated comparable measurements meet that target without failing parity or reproducibility.
- Excel may remain a temporary comparison/view/export tool during migration but is removed from the authoritative calculation path only after all in-scope cases pass and a rollback copy is retained.
- If the source workbook is unavailable, E2 remains blocked for workbook parity; deterministic Python/reference cases may proceed, but spreadsheet replacement is not claimed complete.

## 7. Current blocking items

1. New Actions results for `3037d4b` are not verified; earlier passing checks were for `7c8dacb`.
2. Investor input fields remain open: exact initial/SIP dates, 2036 measurement/exit preference, drawdown tolerance, actual product/ISIN/lot choices, fees, tax facts, and CPI anchor.
3. Qualified tax-professional review has not been recorded; no external reviewer has been contacted.
4. Continuous official NSE G-Sec TRI and complete first-party bullion history remain unavailable/unqualified in the current evidence set.
5. Predictive validity and independent ten-year probability calibration remain unestablished; prior Gaussian tail validation failed.
6. The mandate/proposal guarantee-language conflict needs investor confirmation only if the investor wants to amend the objective. It does not block continued synthetic accounting, evidence qualification, or the separately labeled guarantee feasibility research.

7. GitHub CLI is installed locally, but `gh auth status` reports no authenticated GitHub host. Consequently CLI integration is not yet verified and authenticated PR/issue/Actions reads cannot run.

## 8. Release and status rules

- Use the existing investment decision gate ledger and add artifact-level states: `experimental`, `computation_verified`, `research_validated_for_defined_use`, `decision_ready`, or `deprecated`.
- A source pass qualifies only the named source and scope. A code audit pass qualifies only the checked assertions and version. CI is `PENDING` until the exact commit result is verified.
- Use decision states `SUPPORTED_WITHIN_SCOPE`, `REFUTED`, `INCONCLUSIVE`, `FURTHER_EVIDENCE_REQUIRED`, and `DECISION_BLOCKED` for claims; never present them as investment authorization states.
- Preserve earlier artifacts and results; corrections are dated, linked and explain invalidation.
- Keep investment authorization **NO-GO** until all applicable gates pass and the investor separately approves any action.

## 9. Evidence reviewed

- Repository controls: `AGENTS.md`, `CODEX_START_HERE.md`, `README.md`.
- Mandate and governance: `docs/INVESTMENT_DECISION_MANDATE_2036.md`, `docs/INVESTMENT_DECISION_GATES.md`, `docs/EVIDENCE_AND_MODEL_STANDARDS.md`, `docs/CODEX_EXECUTION_PLAN.md`, `docs/DECISION_DELIVERABLES.md`, `docs/DECISION_LOG.md`, `docs/HANDOFF_STATUS_2026-11-02.md`.
- Active sprint and engine: `docs/SPRINT_01_AFTER_TAX_LEDGER.md`, `docs/SPRINT_01_INVESTOR_INPUT_WORKSHEET.md`, `decision/ty2026_27_tax_components.py`, `decision/after_tax_event_ledger.py`, `decision/terminal_case_reconciliation.py`, and their audit scripts.
- Research: `research/stage512/2026-11-02/README.md`, `stage512_predictive_validation_report.md`, `stage512_model_uncertainty_report.md`, `stage512_source_resolution_report.md`, `stage512_risk_audit.py`, source qualification artifacts and data manifests.
- Automation: `.github/workflows/sprint1-source-audits.yml`, `.github/workflows/sprint1-tax-ledger-audits.yml`, and stage-specific source workflows.
- Planning inputs supplied by the investor: `INVESTMENT_ENGINE_CONSOLIDATED_RESEARCH_PROPOSAL_V3_2026-11-03.md` and `INVESTMENT_ENGINE_INDEPENDENT_AUDIT_2026-11-03.md`.

**Audit limits:** This is a repository and planning audit, not a fresh execution of audits/tests, external tax opinion, live securities availability check, GitHub Actions refresh, comprehensive line-by-line audit of every historical stage, or independent forecast validation. No code tests or workflows were run for this document.

## 10. GitHub CLI installation and integration with current development

### Installation result

- Installed GitHub CLI **2.103.3** from the official GitHub release after verifying the release checksum and a valid Authenticode signature. MSI exit code was 0.
- The recommended WinGet route was present but returned `0x8A150001` (App Installer internal error); installation succeeded through the official release MSI fallback.
- Executable: `C:\Program Files\GitHub CLI\gh.exe`. Rechecked on 3 November 2026: the executable exists, but its directory is absent from machine, user, and current-process PATH. Call it by full path for now; PATH registration has not been verified and should not be reported as complete.
- The installed CLI is **not authenticated**: `gh auth status` reported no GitHub hosts. `gh repo view K49M43/testrepo` therefore could not authenticate. Selecting a Git Credential Manager account for `git push` does not establish that GitHub CLI has an API token.
- GitHub CLI's documented default login is a web/device authorization flow that stores a token in the operating-system credential store; do not request, paste, log, or commit a personal token. On 3 November 2026, an attempt to reuse Git Credential Manager credentials locally returned no credential, and GCM account listing failed with an access-denied process-inspection error. A one-time user authorization is therefore still required unless an approved existing `GH_TOKEN`/credential mechanism is configured.

### Recommended operating model

- Use `gh` for GitHub's API-backed reads and workflow operations: `gh pr view`, `gh pr checks`, `gh run list/view/watch`, `gh issue view/list`, and `gh api` for read-only details that are not exposed by the standard commands.
- Pass `--repo K49M43/testrepo` explicitly on commands. The repository has stacked PR history and an unverified live base relationship; explicit targets reduce accidental cross-repository actions.
- Continue using the existing Git/Git Credential Manager flow for `fetch`, `push`, and branch operations initially. Do not change global Git credential helpers or run `gh auth setup-git` unless a later requirement and review justify it.
- Keep writes gated by the task's explicit authorization: creating/editing GitHub issues or PR text, pushing, merging, deleting branches, and changing labels/projects are separate actions. CLI removes navigation friction; it does not broaden authorization.
- Once a user completes the one-time CLI login and a fresh Codex process sees PATH, validate with `gh auth status`, read-only `gh repo view`, `gh pr view 11`/`12`, `gh pr checks 12`, `gh run list --branch codex/sprint1-increment3-event-ledger-20261103`, and read-only issue list/view commands. Do not mark commit `3037d4b` checks passed until a run tied to that exact SHA is returned.

**Integration disposition:** installed and checksum/signature verified; executable is callable by full path, but PATH is not registered and `gh auth status` reports no authenticated GitHub host. No GitHub API repository/PR/check verification was possible in this audit. After a one-time authorization, routine status checks can use the CLI without browser navigation; the initial authorization itself requires an approved user-mediated login unless a supported credential is already configured.

## 11. Second-pass audit of this plan

| Audit question | Review result | Refinement applied |
|---|---|---|
| Does the plan preserve the actual investor objective? | Proposal v3 reverses the relative semantics of the floor/guarantee and target/stretch. | Added an explicit source-of-truth crosswalk and approval rule; guarantee analysis is now separate. |
| Are implementation dependencies ordered? | Accounting depends on stable event/date/tax definitions; forecast comparison depends on qualified sources and protected evaluation. | Ordered execution from live-state audit → deterministic mechanics → evidence/instruments → historical replay → preregistered models → frontier → independent decision review. |
| Can engineering progress without personal data? | Yes for fixtures, source qualification, candidate evidence and methodology; no for investor-specific tax/exit conclusions. | Separated synthetic engine acceptance from investor-input and tax-professional gates so unknown personal facts do not stall independent engineering. |
| Are tests decision-grade rather than broad counts? | The original milestone wording needed sharper negative-case and independent-reference expectations. | Added explicit event, lot, tax, CPI, settlement, leakage, model-disagreement and causal-policy tests; each needs preregistered expected results and scope. |
| Does the plan prevent statistical overclaiming? | More Monte Carlo paths cannot validate assumptions or create independent decades; the 15% event preference is not yet defined. | Required fixed staged sampling first, protected evaluation data, trial registry, uncertainty decomposition and model-context limits. |
| Is QCSAE first-class without excessive architecture? | A continuous challenge process is necessary; a graph database/orchestrator is not yet justified. | Started the claim/question/test/invalidation record immediately; deferred custom automation until repeated workflows demonstrate need. |
| Are issue criteria measurable and safely scoped? | GitHub issue creation and PR operations publish changes outside the local repository. | Kept issue texts as proposed drafts, required source/evidence/negative cases/dependencies/closure criteria, and separated user authorization for public writes and merges. |
| Does the plan include current-development integration? | Local and remote check status, stacked PR base, and CLI authentication affect what can be verified next. | Added Step 0 for exact live SHA/PR/Actions verification and a local CLI installation/authentication disposition. |
| Does the architecture move calculation out of Excel without confusing storage with computation? | A relational database can preserve/version inputs and results, but does not itself guarantee faster numerical computation. | Added CA-20/21 for the database and Python boundary, CA-22 for workbook parity and measured end-to-end speed, and a fixture-only SQLite pilot before migration. |
| Does “cannot promise” translate into actionable research? | A single caveat would not tell the team which uncertainties are measurable or reducible. | Added P0–P11 subproblems separating event definition, deterministic hurdle, contract feasibility, accounting, sources, parameter/model uncertainty, predictive evidence, simulation error, selection, robustness and independent review. |
| Is final investment readiness protected? | No current evidence supports a GO or guaranteed floor. | Every technical phase may end in `NO-GO`, `INCONCLUSIVE`, or `INSUFFICIENT_EVIDENCE`; human authorization stays separate. |

**Plan refinement outcome:** the plan is now operational enough to generate issue tickets and execute in small increments, including a bounded database-backed Python compute pilot and a separate spreadsheet parity/performance gate. Investor mandate changes, tax sign-off, market availability, and probability claims remain gated. It remains a plan, not proof that its acceptance criteria have been met.

## 12. Why a 2036 outcome cannot be promised — and how to investigate it

### What can and cannot be promised

The engine can aim to guarantee **process properties**: the exact cashflow arithmetic, the stated tax rule implementation and its scope, source lineage, reproducible outputs, and whether a named contract promises particular cashflows under its terms. It cannot promise that an unguaranteed portfolio will realize a specified future wealth or that a modeled success probability equals the future real-world frequency.

That limitation has several separable causes:

1. **Future shocks are unknown.** Contributions, asset returns, inflation, exchange rates, tax law, product structure and execution conditions over the next decade are not observed yet.
2. **The 2036 probability depends on a model.** Simulation estimates `P(success | chosen return/inflation/dependence/tax model)`. Raising the path count reduces simulation noise conditional on that model; it does not prove the model is representative.
3. **The available long-horizon sample is small.** The repository's earlier predictive-validation panel contains 219 synchronized monthly proxy observations. It yields 100 rolling 120-month windows, but adjacent windows share 119 of 120 observations; there is only one complete disjoint 120-month sequence in that panel. Those windows cannot be treated as 100 independent future decades.
4. **Market relationships can change.** Return levels, inflation persistence, dependence, regimes and instrument availability can shift. Additional paths generated from a fixed estimated process do not reveal an unseen structural break.
5. **An individual result depends on policy details.** Exact contribution dates, selected lots, current holdings and income, fees, tax-year law, realization choice, CPI anchor and settlement determine the measured outcome. Unknowns here are reducible with records or clarification; future conditions are not.

An illustration of the simulation distinction: with 25,000 independent simulated paths and a model success rate of 85%, the binomial Monte Carlo standard error is about 0.23 percentage points (about ±0.44 percentage points for a simple 95% interval). That describes numerical sampling error for the specified model. It says nothing by itself about model bias, parameter error, overlapping historical evidence, investor suitability or the true 2036 success rate.

The general verification/validation principle is to assess model credibility and uncertainty in proportion to the model's influence on the decision and the consequence of being wrong; see [NIST's 2026 uncertainty-quantification report](https://doi.org/10.6028/NIST.AMS.100-85). Sequentially valid confidence sequences can address repeated looks at data under their stated statistical assumptions; they do not cure nonrepresentative market data, dependent decade windows or an incorrect return model. See [Howard et al. (2021)](https://doi.org/10.1214/20-AOS1991).

The long-horizon sample description comes from the repository's [predictive-validation report](research/stage512/2026-11-02/stage512_predictive_validation_report.md). The P0–P11 labels below refine existing GitHub issue drafts A1–E2; they are not a proposal to create 12 additional components or a second backlog.

### Smaller investigations and closure states

| Work package | Question to settle | Method and measurable output | What a pass means / does not mean |
|---|---|---|---|
| P0 — Define the event | Is success terminal wealth, any touch during 2036, executed sale, or settled net proceeds? What are the precise goal, date window, CPI base and allowable failure event? | Version an outcome contract with dates, rupee basis, taxes/costs, policy action and risk threshold. Keep unknown fields explicit. | Removes ambiguity from the calculation; does not show the goal is feasible. |
| P1 — Compute deterministic hurdles | What return/cashflow path is mathematically required for ₹90L and ₹1Cr real under the current fixture and under investor-confirmed dates? | Independently solve dated cashflow/XIRR and terminal-wealth equations; run zero-return, fixed-rate and sensitivity tables for inflation, fees and taxes. Compare exact cashflows to the frozen 120/122-month fixtures. | Validates required-return arithmetic under declared inputs; does not say those returns are likely. |
| P2 — Test contractual protection separately | Is there a lawful, enforceable CPI-linked or otherwise acceptable contract matching the stated amount/date, and what funding/counterparty/tax/settlement conditions apply? | Inventory eligible contracts/instruments and primary terms; calculate purchase cost and mismatch risk; record searched universe and exclusions. | Can establish a named contract's stated obligations and conditions or that none was found in the searched universe; never convert a portfolio probability into a guarantee. |
| P3 — Verify deterministic mechanics | Does the ledger conserve cash, units, lots, tax basis, tax liabilities, fees, withholding credits and settled proceeds across event sequences? | Independent hand calculations, a separately written reference case, boundary/property/adversarial tests and reproducible CI tied to exact commit. | Establishes computation correctness within tested operations/rules; not forecast validity or professional tax approval. |
| P4 — Qualify evidence | Are asset and CPI series the actual series claimed, available at decision time, aligned, complete enough, and relevant to products that could be held? | Source/date/hash audits; dual-end date alignment; point-in-time availability; breaks/outliers/corporate actions; explicit proxy and inception handling; CPI base/link checks. | Qualifies observations for named uses; not future-return calibration. |
| P5 — Bound parameter uncertainty | How sensitive is the outcome to expected returns, volatility, inflation, cross-asset dependence, fees, tax and regime persistence? | Estimate ranges/posteriors only where justified; benchmark against historical, valuation/yield-based and conservative structural scenarios; pre-register sensitivity grids and report driver ranking. | Shows which inputs drive the decision and whether a conclusion survives ranges; does not prove the ranges contain the future. |
| P6 — Challenge model form | Would reasonable alternative return, tail, regime, inflation and dependence models change goal outcomes or strategy ranking? | Compare simple baseline, heavy-tail/block/resampling and regime challengers on same frozen inputs; test known crisis periods; retain failed models and limitations. | Identifies model-sensitive conclusions; cannot rule out all unobserved future models. |
| P7 — Assess predictive evidence | Does the available observed history discriminate the candidate models for relevant horizons? | Prespecified rolling-origin tests; correct for overlapping horizons/dependence; include calibration and tail coverage; compare to naive baselines and disclose effective sample limits. Explore longer/cross-market data only with a transferability argument. | May reject poor models or support a bounded forecast use; likely cannot certify a precise individual 10-year success probability from one short panel. |
| P8 — Quantify numerical uncertainty | Is simulation error small enough that it no longer changes the decision under each model? | For each estimand, use independent seeded batches and valid fixed/sequential intervals; convergence tests for probabilities, quantiles and expected shortfall; separately test numerical precision. | Certifies numerical precision conditional on the model and sampling assumptions only. |
| P9 — Guard against selection | Did repeated portfolio/model searches pick an apparent winner by chance or leak the evaluation sample? | Register every candidate and trial; separate selection from evaluation; use protected periods/path sets and multiplicity/backtest-overfitting checks; compare all finalists to simple baselines. | Reduces measured selection bias; cannot eliminate all model risk or choice of candidate universe. |
| P10 — Test decision robustness | Does the shortlist/ranking/action change under plausible assumptions, risk preferences, exit dates and model families? | Present a multi-outcome frontier and flip-point analysis; explicitly vary goal date, real objective, loss event, fees/taxes and product execution. | Identifies robust choices and unresolved trade-offs; does not choose the investor's risk preference. |
| P11 — Independent adjudication | Can a reviewer reproduce or refute material claims without author guidance? | Independent rerun from pinned evidence/code/config; tax-specialist review of legal examples; review claim dependencies and invalidation. | Supports a bounded, human-reviewable conclusion; investor still owns authorization. |

### Decision ladder and result language

For each work package, record one of: **PASS within named scope**, **FAIL**, **BLOCKED by named evidence/input**, **INCONCLUSIVE**, or **NOT APPLICABLE with reason**. For each investment claim, use:

- **Arithmetic verified:** calculation matches independent references under specified inputs.
- **Evidence qualified:** named observations and transformations are fit for a specified test.
- **Model-conditional result:** outcome holds under a stated process and assumptions.
- **Predictive evidence limited/unqualified:** available observations cannot support the claimed real-world probability or transfer.
- **Contract obligation verified:** a named legal instrument/provider term promises a named cashflow subject to explicit conditions.
- **Investor decision:** a separate human choice after reviewing the evidence and limitations.

The investigation succeeds even if the final finding is “we can reproduce the required hurdle and identify the dominant uncertainties, but cannot validate an 85% real-world 2036 success probability.” That is a useful, falsifiable result. It must not be restated as “impossible to invest” or “the target is guaranteed.”

## 13. Capital-allocation design requirements and smallest build sequence

### 13.1 Product boundary

The engine is a **capital-allocation decision-support system**. For a dated mandate, a set of feasible uses of capital, available evidence, and explicit constraints, it must show the consequences of each allocation and the conditions under which the preferred action changes. It does not need to predict markets exactly, imitate a person's internal reasoning, or place trades. Human-like capabilities are implemented as observable disciplines: ask for missing decision-critical facts, check provenance, find contradictions, generate falsification attempts, compare alternatives, and revise conclusions when evidence changes.

The decision object is not “an 85% probability.” It is a reviewable mapping:

`mandate + current state + feasible actions + evidence/model set -> outcome distribution/range + constraints + decision boundaries + evidence status`

The output must preserve multiple outcomes (wealth, shortfall, loss, liquidity, taxes/costs, and execution feasibility). A scalar ranking is allowed only after investor preferences and constraints are explicit. Forecast probability remains conditional on named models and evidence; it is never silently promoted to a real-world guarantee.

### 13.2 Atomic requirements

Each requirement below is independently reviewable. Implement one small vertical slice at a time; do not build a general framework ahead of the first concrete use. “Acceptance” means the stated artifact and checks exist on the exact commit. It does not imply an investment gate passes unless that scope is named.

| ID | Requirement | Smallest deliverable | Acceptance evidence |
|---|---|---|---|
| CA-01 | State the decision being made | Versioned mandate/outcome record for ₹90L floor and ₹1Cr stretch, with unknown investor fields explicit | A reviewer can identify goal, rupee/CPI basis, date window, contribution schedule, failure event, and unresolved fields without inference; conflicting values fail validation. |
| CA-02 | Represent available capital and timing | Dated cash-flow schedule with source, amount, currency, and availability date | Independently recomputed schedule totals and dates match the frozen fixture; missing dates are flagged rather than fabricated. |
| CA-03 | Define feasible actions | Initial action register containing a precisely defined cash-hold policy, simple reference allocations, and only evidenced candidate instruments | Every action has a stable ID, eligibility status, rationale, and explicit unsupported fields; cash-hold yield, access, costs and tax are explicit; no proxy is represented as a purchasable instrument. |
| CA-04 | Define the as-of state | Minimal state record for cash, units/lots, prices/NAV convention, accrued income, tax basis/liability, pending trades and settlement | Hand-calculated event sequence reconciles opening state + events = closing state by currency/unit; impossible negative balances or unknown classifications fail closed. |
| CA-05 | Account for an action consistently | Deterministic transition from state + dated action/event to new state | Golden cases cover contribution, buy, income/coupon, fee, partial sale, tax/withholding, settlement, CPI conversion; independent expected values and units agree at declared precision. |
| CA-06 | Make alternatives comparable | Common dated outcome record per action: nominal/real wealth, taxes, costs, shortfall, drawdown, liquidity and settlement | Same mandate, dates, cash flows, CPI convention, return-path input and cost/tax scope are applied across every compared action; absent metric is marked unavailable, never zero. |
| CA-07 | Separate fact from assumption | Each material input carries value/unit, source or owner, as-of/availability date, status, transformation, and dependent result IDs | A report can trace every decision-material input to source or explicit assumption; changing an input identifies affected outputs. |
| CA-08 | Represent uncertainty without conflation | Uncertainty ledger distinguishes observation/sample, parameter, model form, numerical, and preference/decision uncertainty | A report labels each interval/result by uncertainty class and conditional scope; Monte Carlo error is not presented as total predictive uncertainty. |
| CA-09 | Challenge the result continuously | For each decision-material claim, record question, plausible counter-hypothesis, test/evidence, result, reviewer, and disposition | A release candidate has at least one material challenge per changed claim or a documented reason none is warranted; failed challenges block dependent claims or trigger explicit scope limits. |
| CA-10 | Compare models before choosing | Frozen baseline and challenger definitions with identical decision inputs and evaluation protocol | Any model comparison identifies changed assumptions, metrics, and protected evaluation data; tuning data cannot be reported as independent validation. |
| CA-11 | Show when action preference flips | Threshold/sensitivity table identifying input values or observable conditions that change eligibility, feasibility, or ranking | At least one independently recomputed flip point for each proposed recommendation; if preferences are unknown, output a Pareto/menu view rather than a winner. |
| CA-12 | Support monitoring and revision | Human-reviewed policy record with review dates, observable triggers, permitted responses, and evidence needed | Each trigger is measurable, has an owner/action and a review trail; triggers do not execute trades automatically. |
| CA-13 | Reproduce a decision pack | Run manifest pinning code commit, source/evidence hashes, configuration, dependency environment, seeds/streams, and outputs | Independent rerun reproduces deterministic outputs exactly and stochastic outputs within preregistered tolerances; changed inputs create a distinct run ID. |
| CA-14 | Make the result decision-useful | Concise decision pack: mandate, feasible actions, outcome comparison, uncertainty, flip points, blockers, and next review | A reviewer can answer “what can we do, what could happen, why might this be wrong, what would change the choice?” using the pack alone. |
| CA-15 | Preserve human authorization | Explicit status separation between research result, candidate for consideration, and investor authorization | No code path, CI result, optimizer output or model threshold changes investor authorization; authorization requires a separately recorded investor decision. |
| CA-16 | Define the allocation decision variables and constraints | Versioned allocation proposal with amount/weight by action and date, cash reserve, permitted bounds, minimum sizes, and borrowing/shorting permissions | Independently recomputed allocations sum to available deployable capital within stated rounding; every constraint is checked at every action date; unspecified permissions default to disallowed. |
| CA-17 | Record investor objective and risk constraints | Explicit preference record separating binding constraints from goals and reporting preferences | No strategy is called “best” unless the investor-selected comparison rule is recorded; unset preferences produce a multi-metric menu, not inferred utility weights. |
| CA-18 | Specify the allocation policy over time | Versioned one-time or recurring contribution, rebalance, withdrawal, target-lock, and exit/settlement rules, with unsupported rules omitted | Replay of the same dated events and policy reproduces identical actions; all trigger variables are observable and timestamped; absent policy fields remain unresolved rather than silently defaulted. |
| CA-19 | Connect market assumptions to ledger outcomes | Minimal model-to-ledger contract supplying dated price/total-return/inflation observations or declared conditional paths, and the convention for applying them | A hand-reconstructed path matches ledger output at every event; return type, timing, missing observations and model-conditional status are explicit; incompatible series are rejected. |
| CA-20 | Store canonical inputs and evidence in a versioned relational database | Small migrated schema for mandate/configuration, source/evidence references, observations, cashflows/events, and schema versions | Clean rebuild and sequential migrations succeed; keys/units/dates/references are constrained; source revisions are append-only/versioned; the same snapshot has a stable content hash. |
| CA-21 | Keep computation deterministic and outside the database | Python run boundary that reads a consistent snapshot, computes, and atomically writes outputs plus a run manifest | A failed run cannot appear complete or leave partial published results; repeating an identical deterministic run reproduces outputs exactly and links to code/config/data versions. |
| CA-22 | Migrate spreadsheet calculations with measured parity and speed | Workbook formula inventory and a frozen, representative benchmark/parity set for a database-backed Python path | Per-output tolerances and workload are fixed before comparison; all in-scope cases reconcile; load/compute/persist timings are separated; “faster” is claimed only after a preregistered end-to-end target is met. |

### 13.3 Dependency order and first vertical slice

Build in dependency order, with one small PR per coherent requirement cluster:

1. **Slice A — Contract the decision (CA-01, CA-02):** freeze the existing planning fixture, encode goal/date/cash-flow semantics, and expose unknowns. This is data/document work plus validation; no optimizer or stochastic code.
2. **Slice B — Establish the data-store contract (CA-20):** version the relational schema and migrate only the synthetic fixture needed for one end-to-end run. Preserve old files and require a stable content hash.
3. **Slice C — Enumerate actions (CA-03):** register a defined cash-hold policy and simple references first; add a product only when identity, history, costs, tax route, and execution evidence are sufficiently qualified.
4. **Slice D — State, transitions, and compute boundary (CA-04, CA-05, CA-21):** complete the deterministic ledger with independent cases; compute in Python from a consistent database snapshot and persist the result atomically. Keep tax law fixtures versioned and isolate unresolved legal interpretations.
5. **Slice E — Comparable consequences (CA-06, CA-07, CA-19):** calculate the same decision metrics from the same ledger and preserve source/assumption lineage. First compare deterministic hurdles and simple scenarios.
6. **Slice F — Challenge and uncertainty (CA-08, CA-09):** attach uncertainty classes and adversarial questions to every material claim. This starts before simulation and continues through every later slice.
7. **Slice G — Define allocation and policy (CA-16, CA-17, CA-18):** encode allocation variables, constraints and only investor-stated decision preferences; specify when actions occur and how the policy responds. Until then, report a menu, not an optimum.
8. **Slice H — Connect return evidence and challenge models (CA-19, CA-08, CA-09, CA-10):** prove the deterministic path-to-ledger contract first; only then compare qualified historical and conditional model paths.
9. **Slice I — Measure spreadsheet migration/performance (CA-22):** inventory workbook logic and benchmark equivalent workloads only after the Python/database vertical slice is correct; no speed claim without measured end-to-end improvement.
10. **Slice J — Decision boundaries (CA-11):** locate input/observable flip points under the declared policy and preference constraints; show where model disagreement changes the action.
11. **Slice K — Adaptation and reproducibility (CA-12, CA-13):** add monitoring policy and full run manifest when repeated experiments require them; no automated reallocation.
12. **Slice L — Decision pack and authorization boundary (CA-14, CA-15):** assemble independently reviewable outputs; keep NO-GO/INCONCLUSIVE available and authorization separate.

The **first vertical slice** is CA-01/02, CA-04/05/06, CA-16, CA-19/20/21 for the current synthetic fixture: migrate the fixture to the relational store, read a versioned snapshot, run a named deterministic allocation and return path in Python, persist a manifest and outcomes, and compare with a defined cash-hold policy. Reconcile to the existing implementation and independent arithmetic. This qualifies storage, ledger mechanics and reproducibility only; it cannot establish workbook replacement (CA-22), product eligibility, tax advice, forecast calibration, or investment readiness.

### 13.4 Design constraints and decision gates

- Keep the first implementation in the current Python/repository workflow. Do not introduce Rust unless profiling shows computation time is blocking a preregistered experiment, or a specific correctness boundary benefits from a Rust component. If introduced, require cross-language golden vectors, deterministic serialization, bounded numeric tolerances, and a demonstrated maintenance/performance benefit.
- Use the database for durable, versioned state and batch I/O; perform numerical path/portfolio calculations in Python over a consistent snapshot. Measure database I/O and compute separately. A relational database is in scope; distributed compute, service deployment, and a database rewrite of every historical research file are not.
- Treat a local SQLite database as the pilot default only while development is single-user and local. If concurrent writers, multi-user access, or hosted execution are required, evaluate a server database before expanding the schema; do not add an adapter/abstraction layer without a real second backend.
- No optimizer until action definitions, common outcomes, investor constraints/preferences, model evaluation split, and trial registry are accepted. Before that point, enumerate and compare a small declared set.
- “No deployment” is not a zero-return or risk-free comparator by default. Define the actual cash instrument/account, rate convention, access restrictions, costs and taxes, or label a zero-return case as a mathematical reference only.
- A portfolio/action is not fully specified by target weights. Record action dates, purchase sizing/rounding, rebalancing/withdrawal/exit rules and settlement convention; otherwise label the comparison as a static allocation fixture.
- Distinguish binding investor constraints (must satisfy) from goals (optimize toward) and reporting metrics (show but do not optimize). Unknown preferences must not be inferred from historic choices or the aspirational 85% figure.
- No single expected-wealth or success-probability objective may erase liquidity, drawdown, shortfall severity, taxes, or execution constraints.
- No inference from a model output to a guarantee, calibrated personal probability, suitability result, or authorization.
- Excel is not authoritative for calculation after the parity migration gate passes. Until then, preserve it as a frozen comparator; do not remove or overwrite source workbooks. If no workbook is available, keep replacement status blocked and continue against independent golden cases.
- Each requirement closes as `PASS within scope`, `FAIL`, `BLOCKED`, `INCONCLUSIVE`, or `NOT APPLICABLE`; record the exact evidence and commit. A requirement may be split further when one PR cannot be independently understood and reviewed.
- The issue backlog in Section 6 remains the delivery tracker. Map CA IDs onto those existing draft issues and split only where dependencies, owners, or acceptance artifacts differ; do not create a parallel planning hierarchy.

### 13.5 Audit result and remaining design questions

The first draft had five material gaps, now corrected above: it treated “no deployment” as self-explanatory; it named portfolio outcomes without specifying the return-path-to-ledger boundary; it did not explicitly capture allocation variables, investor constraints/preferences, or the time policy; it placed model comparison before those allocation semantics; and it did not make the requested spreadsheet-to-database migration an explicit deliverable. The revised requirements add CA-16–CA-22, define the cash-hold comparator, separate database persistence from Python numerical computation, and reorder the dependent slices. The first vertical slice now includes a deterministic path, relational persistence, and an explicit cash comparator.

The following are deliberately **not** decided by this design audit and must remain explicit inputs or later research questions: exact investor cash dates and reserve needs; acceptable loss/shortfall event and risk limit; whether the investor prefers a fixed allocation or an adaptive policy; the candidate instrument universe and actual execution route; the actual workbook/formula inventory and representative performance workload; whether single-user SQLite remains sufficient; which return/inflation models deserve inclusion; what probability-calibration evidence is adequate for a real-world claim; and whether a Rust component is justified by measured profiling. These are not reasons to block a synthetic storage/mechanics pilot, but they block claims of completed workbook replacement or investor-specific allocation where material.

To keep implementation pieces genuinely small, CA-05 must be delivered as event-level increments rather than one ledger mega-PR: (a) contribution and cash conservation, (b) purchase and unit/rounding rules, (c) income/coupon/accrual, (d) fee and withholding, (e) partial disposal and lot basis, (f) tax liability/set-off/rounding, (g) settlement, and (h) CPI conversion. Each increment adds an independently calculated golden case and updates the invariant ledger; later cases must not weaken earlier accepted results. The opening vertical slice should stop at the first subset required to compare the chosen fixture actions, then extend by dependency—not implement all eight event classes at once.

**Original audit disposition (3 November 2026):** the design was sufficiently bounded to begin G0 and a fixture-only relational-store/ledger pilot under CA-20/CA-21. The 4 November status reconciliation below records the Sprint 1 closeout and creation of the Sprint 2 issue. It is not yet a complete production specification for an investor-specific allocator or a validated Excel replacement. Before selecting any allocation, CA-03/CA-16/CA-17/CA-18, qualified evidence, tax scope, and statistical assurance gates remain necessary.

## 14. Incremental sprint and short-goal plan

This is the proposed delivery sequence for Section 6 issues and CA-01–CA-22. It assigns **one verifiable outcome per short goal**; related goals may be grouped into sprints after the owner's capacity is known. Sprint 1's bounded synthetic ledger scope closed on 4 November 2026. Sprint 2 is now explicitly scoped to G2 under GitHub milestone #1 and issue #15; no calendar duration is promised. Each goal carries a QCSAE challenge: state the claim, strongest counter-case, evidence/check, result, and affected downstream claims.

| Order | Short goal / sprint outcome | Scope and mapped draft issues | Dependency | Measurable exit / stop condition |
|---|---|---|---|---|
| G0 | Re-establish live baseline and turn the plan into a traceable backlog | Verify default branch, exact PR/branch SHAs, review and CI state with `gh`; reconcile A1/A2 and map all CA IDs to A–E issues. Identify the workbook and formula source for E2 or record that it is not in the inspected repository. This plan is local planning evidence, not proof of live GitHub state. | None | One dated baseline record has exact remote SHAs and check runs, or explicitly marks remote state blocked by CLI authentication; every CA ID maps to an issue/work item and every issue has dependency and exit evidence; E2 has a named workbook source or remains explicitly blocked. No public issues until separately authorized. |
| G1 | Close the existing deterministic ledger fixture | Sprint 1; B1 and applicable parts of B2; CA-04/05. **Complete within bounded synthetic scope**; PR #12 and the audit hardening in PR #14 are merged. | G0 | Exact fixture mechanics and statutory component scope reconcile at the tested scope; unsupported cases fail closed; exact-head CI passed. Investor-specific qualification remains open. |
| G2 | Persist and compute one fixture through the database-backed Python path | **Sprint 2; GitHub milestone #1 and issue #15.** E1; CA-20/21. Migrate only the current synthetic fixture into a versioned local relational database; compute in Python from a stable snapshot and persist results/manifests. | G1 complete; G0 remote baseline verified; G3/G4 documentation may proceed in parallel | Clean rebuild/migrations pass; source/config/input snapshot is hashed; database result exactly matches existing deterministic output and independent golden arithmetic; failures cannot leave a completed partial run. No performance or workbook-replacement claim yet. |
| G3 | Freeze the capital-allocation question and deterministic hurdles | A1 completion; CA-01/02; P0/P1. Preserve ₹90L floor / ₹1Cr stretch semantics, explicit unknowns, dated fixture schedule, success/shortfall event definitions, and independently solved nominal/real hurdles under declared CPI assumptions. | G0; G1 only for after-tax hurdles | Versioned outcome contract distinguishes valuation, sale, and settled-proceeds events; unknown personal inputs remain unknown; hurdle calculations match an independent calculation and are labeled arithmetic, not likelihood. |
| G4 | Specify the action and allocation policy | CA-03/16/17/18; define cash-hold comparator, deployable capital, reserve, allocation variables/bounds, policy dates, and preference/constraint capture. Start with a small enumerated action set; no optimizer. | G3 | Every action is either fully defined for fixture comparison or explicitly blocked; allocations reconcile to deployable capital and satisfy all stated constraints; no “best” label where investor preferences are unset. |
| G5 | Qualify decision-relevant instruments and repair evidence labels | C1/C2; CA-07; P2/P4. Correct the synthetic “Historical 11.8% replay” label append-only; build candidate/proxy/evidence register; qualify only data that can change candidate eligibility or the decision. | G0, G3; can run in parallel with G4 if claim inventory is stable | Each candidate is investable, proxy-only, excluded, or blocked with identifier, point-in-time status, data convention, costs/tax/execution evidence and missing fields; corrected history claim links all affected outputs; no silent pre-inception splice. |
| G6 | Prove one deterministic path from action to comparable outcomes | CA-06/19/21 plus necessary CA-04/05/07/20; implement one fixed, fully declared return/inflation path through the ledger; compare selected fixture allocations with the defined cash-hold case using identical dates/cost/tax conventions. | G1–G5 | Independent event-by-event reconstruction agrees at declared precision; every output traces to inputs; absent data is unavailable, not zero. Result is explicitly a mechanics fixture, not a forecast. |
| G7 | Freeze uncertainty and experiment contracts | C3 and process portion of D2; CA-08/09/10/13/20/21; define estimands, model contexts, competing assumptions, evaluation split, trial registry, seeds/streams, numerical tolerances, compute budget, and invalidation record. | G5–G6 | Protocol is reviewed and pinned before new comparison runs; numerical, parameter, model, evidence, and preference uncertainties are separate; at least one falsification challenge per material claim; no holdout leakage. |
| G8 | Challenge model and probability credibility | C4; P5–P9; compare only the preregistered minimal baselines/challengers and assess predictive evidence, calibration limits, tails, dependence, and selection effects. | G7; eligible data from G5 | Each model has a bounded context of use; forecast differences larger than simulation error are attributed to model/data uncertainty; if evidence cannot support calibration, result is explicitly conditional or `INSUFFICIENT_EVIDENCE`, not an invented precise probability. |
| G9 | Produce the attainable capital-allocation menu and flip points | D1; CA-10/11/16/17/18/22; P10; compare no-deployment/cash-hold, simple reference policies, and only qualified candidates against both goals, including real after-tax outcomes, shortfall magnitude, drawdown, liquidity, cost and execution. | G4–G8; G5 required for workbook parity/performance claims | Comparable outcome vectors and sensitivity/flip points reproduce from pinned inputs; feasibility labels distinguish contract evidence, model infeasibility and insufficient evidence; no scalar winner without investor preferences. Workbook replacement/performance is claimed only if E2 passes. |
| G10 | Independent challenge, adaptive review policy, and decision pack | D2 completion and D3; CA-09/12/14/15/22; map gates once to existing G0–G5; define measurable review triggers and assemble evidence, limits, alternatives and next actions. | G9 | Independent reviewer can reproduce and challenge material claims; dependencies are invalidated when inputs change; investor authorization remains a separate explicit human decision. `NO-GO` and `INCONCLUSIVE` remain valid outcomes. |

### 14.1 Sprint sizing and working rules

- Use goals G0–G10 as the source sequence; create a sprint container only after confirming actual team capacity. If a goal exceeds one sprint, split it by its listed deliverables without changing its exit condition. If multiple goals fit, combine adjacent goals only when their dependencies and review evidence remain clear.
- Sprint 1 is complete for its bounded synthetic scope; use `docs/SPRINT_01_AFTER_TAX_LEDGER.md` as its closure record. Sprint 2 is the single G2 database pilot tracked by [GitHub issue #15](https://github.com/K49M43/testrepo/issues/15) under [milestone #1](https://github.com/K49M43/testrepo/milestone/1).
- Each work item must fit this template: **claim/question → minimal change → independent check → acceptance threshold → evidence artifact → affected claims/gate → rollback/invalidation rule**. If any field is unclear, the item is not ready for implementation.
- Definition of done per goal: reviewed diff; focused checks appropriate to the change; recorded exact commit and evidence; QCSAE challenge/disposition; tracker and decision log updated; no scope expansion based only on a passing test.
- Order is dependency-aware, not a promise that later goals will all be executable. Evidence gates may stop, narrow, or redirect work. Preserve failed results; never weaken a threshold simply to keep sprint progress green.
- Planning status as of 4 November 2026: the live baseline is verified through PR #14 and its passing merge-commit workflows; G1 is complete within scope. G2 is the next implementation goal. Its first action is to freeze one existing synthetic fixture and independent expected outputs before defining database tables. The authoritative Excel workbook is still absent from the inspected repository, so workbook parity and replacement remain blocked under E2/CA-22.

### 14.2 Sprint 2 — database-backed deterministic compute pilot

**Objective:** prove that the current deterministic synthetic fixture can be stored, read, computed, and reproduced through a versioned database/Python boundary. This is a data integrity and reproducibility milestone; it is not a speed claim or Excel replacement.

**GitHub tracking:** [Sprint 2 milestone #1](https://github.com/K49M43/testrepo/milestone/1), [issue #15](https://github.com/K49M43/testrepo/issues/15), under umbrella [issue #3](https://github.com/K49M43/testrepo/issues/3).

**Execution sequence:**
1. Freeze the existing **nine-event, two-lot, two-tax-year synthetic fixture** in `decision/audit_after_tax_event_ledger.py` as `research/sprint2/fixture_v1/input.json` plus `expected.json`. Capture its event list, units, explicit tax inputs, offset schedule, code version, and expected outputs: ₹2,433 gross terminal wealth, ₹473.564 incremental portfolio tax, and ₹2,109.436 net fixture wealth. This is the first task; do not design tables around guessed investor data. These figures are synthetic mechanics evidence, not investor outcomes.
2. Define and migrate only the fixture's relational schema (SQLite for this single-user pilot): run configuration, event/lot input, source/evidence references, schema version, manifest, and result.
3. Add constraints and a transactional loader; canonicalize and hash the calculation-relevant input snapshot.
4. Read a stable database snapshot into Python, calculate using the existing deterministic implementation, and atomically persist outputs plus manifest.
5. Rebuild from an empty database, rerun the identical fixture, compare every result to the existing script and independent golden arithmetic, and prove failure rollback and distinct run identities after an input/config/code change.
6. Record load, compute, and persistence timings separately as baselines. Keep any speedup claim blocked until E2/CA-22 identifies the authoritative workbook and preregisters a comparable workload/target.

**Sprint 2 exit:** repeatable clean migrations; exact deterministic numeric parity; stable source/config/input/run hashes; invalid references rejected; failed runs never marked complete; existing research evidence preserved. Investor authorization remains NO-GO.

### 14.3 Traceability from design requirements to the existing issue draft

This is an explicit mapping aid for G0; A1–E2 remain the draft issue specifications in Section 6. Sprint 2's G2/E1 pilot is now tracked separately as GitHub issue #15; the broader A1–E2 backlog has not all been created as public issues.

| Existing draft issue | Primary CA requirements | Planned short goal |
|---|---|---|
| A1 — Mandate and outcome semantics | CA-01, CA-02, CA-17 | G0, G3, G4 |
| A2 — Claim/evidence inventory | CA-07, CA-08, CA-09, CA-13 | G0, G5, G7 |
| B1 — Accounting mechanics | CA-04, CA-05, CA-19, CA-21 | G1, G2, G6 |
| B2 — Tax rules and review | CA-05, CA-06, CA-07 | G1, G6, G9 (professional review is an external gate) |
| C1 — Historical-label correction | CA-07, CA-09 | G5 |
| C2 — Instrument/evidence register | CA-03, CA-07, CA-16, CA-19, CA-20 | G4, G5, G6 |
| C3 — Experiment protocol | CA-08, CA-10, CA-13, CA-20, CA-21 | G7 |
| C4 — Predictive-validity assessment | CA-08, CA-10, CA-11 | G8, G9 |
| D1 — Feasibility/frontier | CA-03, CA-06, CA-10, CA-11, CA-16, CA-17, CA-18, CA-19, CA-22 | G4, G9 |
| D2 — QCSAE and invalidation | CA-07, CA-09, CA-13 | G0, G7, G10 |
| D3 — Independent review/decision pack | CA-12, CA-14, CA-15 | G10 |
| E1 — Relational storage and deterministic run | CA-20, CA-21 | G2 |
| E2 — Workbook parity and performance evidence | CA-22 | G9, G10 |

Some CA requirements span multiple issues because accounting, evidence, and allocation outputs depend on one another. G0 must split an issue only when it has an independent owner, dependency, deliverable, and acceptance test; otherwise retain the cross-reference rather than creating duplicate backlog items.

## 15. Final pre-implementation audit — 3 November 2026

| Audit area | Result | Evidence / remaining condition |
|---|---|---|
| Original objective and mandate | **PASS — preserved** | The plan still treats ₹90L real as the planning floor and ₹1Cr real as the stretch goal; neither is a guarantee, and the aspirational 85% is not an approved or calibrated probability. |
| Capital-allocation focus | **PASS — explicit** | CA requirements cover deployable capital, alternatives, constraints, preferences, dated policy, comparable after-tax outcomes and action flip points. |
| Build sequence and work size | **PASS — sequenced; capacity not sized** | G0–G10 have dependencies and exits; event accounting and database migration are split into small pilots. Sprint durations/owners are intentionally unset until capacity and cadence are known. |
| Database/compute boundary | **PASS — explicit pilot** | CA-20/21 define relational persistence and a deterministic Python compute boundary; CA-22 gates spreadsheet replacement on exact parity and measured performance. SQLite is only the single-user pilot default. |
| Architecture and scope control | **PASS — bounded** | Python/repository workflow remains the default; no optimizer, service, dashboard or Rust rewrite is a prerequisite. Rust is conditional on measured need. |
| Uncertainty and evidence controls | **PASS — claims bounded** | Numerical precision, model/parameter/evidence uncertainty and investor preference are separate; failure and `INSUFFICIENT_EVIDENCE` remain acceptable outcomes. |
| Issue traceability | **PASS — draft mapping present** | CA-01–CA-22 map to existing A1–E2 drafts. The GitHub issues themselves remain uncreated. |
| Workbook migration baseline | **BLOCKED for parity** | No `.xls`, `.xlsx`, `.xlsm`, or `.ods` workbook is present in the inspected repository. E1 and fixture-based Python work can proceed; E2 cannot claim formula parity or completed Excel replacement until the authoritative workbook and representative workloads are identified. |
| CLI installation | **PASS — installed** | `C:\Program Files\GitHub CLI\gh.exe` exists and reports version 2.103.3. It is not on machine, user, or current-process PATH; use the full path until PATH is separately fixed. |
| CLI authentication / live GitHub audit | **BLOCKED** | `gh auth status` reports no logged-in host. Git Credential Manager did not supply a token to the local bridge attempt. No live PR, issue, or Actions state was verified. Do not use browser fallback; obtain an approved CLI login before relying on remote state or publishing. |
| Local document quality | **PASS — basic static check** | Direct scan found zero trailing-whitespace lines and all 22 CA IDs in the issue map. The file is untracked, so Git diff checks do not yet validate it. This is not a software test or independent verification of financial calculations. |

**Start condition:** the plan is ready for local, reversible work on G0 and fixture-scoped implementation planning. Before any push, PR/issue creation, or claim that remote checks pass, authenticate `gh` and verify exact remote SHAs/check runs. Do not treat the current CLI installation as complete GitHub access. Investment authorization remains **NO-GO**.
