# G3 — 2036 outcome contract and deterministic hurdles

**Status:** bounded arithmetic and outcome-definition artifact; no portfolio forecast, probability, or investment authorization.

**Contract:** [`g3_outcome_contract_v1.json`](../research/stage512/2026-11-04/g3_outcome_contract_v1.json)

**Reproducible results:** [`g3_deterministic_hurdles_v1.json`](../research/stage512/2026-11-04/g3_deterministic_hurdles_v1.json)

**Calculation:** [`g3_goal_hurdle.py`](../decision/g3_goal_hurdle.py)

**Independent audit:** [`audit_g3_goal_hurdle.py`](../decision/audit_g3_goal_hurdle.py)

## Decision question this goal resolves

G3 fixes what “reach the goal” means and calculates the return hurdle implied by the current dated contribution fixture. This prevents later comparisons from changing the target definition, cashflow timing, CPI assumption, or success event without showing that change.

It does not select an investment or show the target is attainable. It converts the declared targets into explicit arithmetic requirements for later strategy tests.

## Preserved objective and outcome event

- **₹90 lakh in 2026 purchasing power** remains the primary planning floor. It is not a guarantee or a required contractual payoff.
- **₹1 crore in 2026 purchasing power** remains a separate stretch goal.
- The analysis default is net accessible after-tax wealth under a declared measurement and liquidation policy, converted to 2026 INR. The investor has not confirmed the final measurement month or exit method; this default is an analysis convention, not a new investor instruction.
- A **valuation** is a mark before sale; a **sale** is an executed disposal with possible costs and tax; **settled access** is cleared proceeds and retained liquid wealth after modeled obligations. These events are not interchangeable.
- Record tax paid from the portfolio versus outside it so the same tax is not subtracted twice.

For target (G) and measured real accessible wealth (W):

\[
\mathrm{success}=\mathbf{1}[W\geq G],\qquad
\mathrm{shortfall}=\max(G-W,0),\qquad
\mathrm{shortfall\ fraction}=\frac{\max(G-W,0)}{G}.
\]

No success probability is calculated in G3.

## Frozen cashflow fixture and limits

The calculation uses the existing schedule in `research/stage512/2026-11-02/cashflow_hurdle_monthly_2026-10_base.csv`:

- ₹42 lakh at illustrative month 0, October 2026;
- ₹25,000 at each month end, beginning November 2026;
- a 10% increase after each 12 SIPs;
- 120 payments through October 2036 as the primary arithmetic case;
- 122 payments through December 2036 as an alternate-date sensitivity.

The 120-payment SIP total is ₹47,81,227.38, making total contributed principal ₹89,81,227.38. The 122-payment SIP total is ₹49,10,914.50, making total contributed principal ₹91,10,914.50. These are the mathematical values in the frozen schedule. Actual dates, payment rounding, and the final 2036 measurement month remain unconfirmed.

Inflation rates of 4%, 6%, and 8% are compound scenarios, not forecasts. October 2026 is an assumed CPI reference month for this arithmetic; it is not confirmed as the investor's observed CPI anchor.

## Derivation

For (n) months, initial capital (P), end-of-month contribution (C_m), and constant monthly nominal return (r), the gross terminal value is:

\[
FV(r,n)=P(1+r)^n+\sum_{m=1}^{n}C_m(1+r)^{n-m}.
\]

For real target (G) and annual compound CPI scenario (i), the nominal target at the terminal month is:

\[
T_n=G(1+i)^{n/12}.
\]

The nominal hurdle solves (FV(r,n)=T_n). The reported effective annual nominal hurdle is ((1+r)^{12}-1). The real-cashflow cross-check deflates each contribution (C_m) by ((1+i)^{m/12}), then independently solves for the return that reaches (G) in 2026 purchasing power. The equivalent annual real return is:

\[
R_{real}=\frac{1+R_{nominal}}{1+i}-1.
\]

Both nominal and deflated-real calculations use Decimal arithmetic at 50-digit precision. Currency is displayed to paise; hurdle rates are solved at higher precision and then formatted for reporting.

## Central 6% planning scenario

| Target and horizon | Nominal target at 2036 | Required effective annual nominal gross return | Equivalent effective annual real return |
|---|---:|---:|---:|
| ₹90L floor, 120 payments / Oct 2036 | ₹1,61,17,629.27 | 8.2536% | 2.1260% |
| ₹1Cr stretch, 120 payments / Oct 2036 | ₹1,79,08,476.97 | 9.7117% | 3.5016% |
| ₹90L floor, 122 payments / Dec 2036 | ₹1,62,74,917.90 | 8.0970% | 1.9783% |
| ₹1Cr stretch, 122 payments / Dec 2036 | ₹1,80,83,242.11 | 9.5362% | 3.3361% |

These are gross arithmetic hurdles **before tax, fees, spreads, and other costs**. The target itself is after-tax and real. Therefore, these gross rates are not sufficient proof that a strategy will deliver the after-tax target. A strategy-specific after-tax hurdle needs its instruments, dated returns, taxable events, costs, law assumptions, and exit policy.

## Inflation sensitivity

| Goal | Horizon | CPI scenario | Nominal target | Gross annual nominal hurdle |
|---|---:|---:|---:|---:|
| ₹90L floor | 120 months | 4% | ₹1,33,22,198.56 | 5.6018% |
| ₹90L floor | 120 months | 6% | ₹1,61,17,629.27 | 8.2536% |
| ₹90L floor | 120 months | 8% | ₹1,94,30,324.98 | 10.8376% |
| ₹1Cr stretch | 120 months | 4% | ₹1,48,02,442.85 | 7.0715% |
| ₹1Cr stretch | 120 months | 6% | ₹1,79,08,476.97 | 9.7117% |
| ₹1Cr stretch | 120 months | 8% | ₹2,15,89,249.97 | 12.2897% |
| ₹90L floor | 122 months | 4% | ₹1,34,09,568.17 | 5.4336% |
| ₹90L floor | 122 months | 6% | ₹1,62,74,917.90 | 8.0970% |
| ₹90L floor | 122 months | 8% | ₹1,96,81,159.92 | 10.6894% |
| ₹1Cr stretch | 122 months | 4% | ₹1,48,99,520.18 | 6.8861% |
| ₹1Cr stretch | 122 months | 6% | ₹1,80,83,242.11 | 9.5362% |
| ₹1Cr stretch | 122 months | 8% | ₹2,18,67,955.47 | 12.1214% |

The 122-month case includes two additional stepped-up contributions and two additional months of compounding. It is a sensitivity, not an investor-confirmed exit date.

## Local derivatives: how the hurdle moves

The sensitivity of the solved annual hurdle (R=(1+r)^{12}-1) to the nominal target (T) follows from implicit differentiation:

\[
\frac{dR}{dT}=\frac{12(1+r)^{11}}{\partial FV/\partial r},
\]

where:

\[
\frac{\partial FV}{\partial r}=nP(1+r)^{n-1}+
\sum_{m=1}^{n-1}(n-m)C_m(1+r)^{n-m-1}.
\]

For the 120-month, 6% CPI floor case, around the solved hurdle:

- each additional ₹1 lakh in nominal target raises the required annual gross hurdle by about **0.0860 percentage points**;
- a one-percentage-point CPI increase raises the nominal target by about **₹15.21 lakh** and the gross annual hurdle by about **1.3078 percentage points**.

These are local derivatives at the stated scenario. They should not be extrapolated linearly across large target or CPI changes. The independent audit checks them against centered finite differences.

## Independent challenge and validation

The independent audit:

- independently rebuilds the cashflow balance month by month, rather than using the production power-sum implementation;
- uses Decimal `exp`/`ln` CPI factors as a separate calculation route;
- solves each of the 12 goal/horizon/CPI cases in both nominal and deflated-real terms;
- reconstructs terminal amounts to less than one paisa;
- matches the existing floor-only float baseline within (10^{-9}) in annual-return fraction;
- challenges the target and CPI derivatives with finite differences;
- checks that the stretch hurdle exceeds the floor hurdle under the same assumptions.

On the current artifact, the maximum nominal reconstruction residual is below ₹0.000000001 and the maximum real reconstruction residual is below ₹0.000000000000000000000000003. The two independent real-hurdle calculations differ by less than (5\times10^{-17}) in annual-return fraction.

## Continuous Question & Challenge Engine record

- **Claim:** the fixture schedule implies a particular constant gross return hurdle for each declared real target and CPI scenario.
- **Strongest counter-case:** meeting a deterministic hurdle does not establish feasibility or likelihood. Variable returns, bad sequence, tax, expenses, eligible instruments, future law, and exit timing can all change accessible real wealth.
- **Falsification checks:** independent real-cashflow solution, terminal reconstruction, legacy-baseline comparison, and derivative finite differences.
- **Disposition:** arithmetic requirement only. Probability, forecast, recommendation, and authorization are out of scope.
- **Invalidation triggers:** target, cashflow dates or amounts, payment convention, CPI base/scenario, or measurement/liquidation policy changes.

## Remaining unknowns and downstream work

Investor confirmation is still needed for exact dates, CPI base month, 2036 measurement month, liquidation policy, risk tolerance, and account/product constraints. The after-tax hurdle remains strategy-specific. G4 must define allowed actions, deployment capital, reserve, policy dates, and investor constraints before any alternative is called preferable. Later probability work must estimate outcomes under explicit assumptions and pass predictive validation; G3 does not supply a success probability. Investment authorization remains **NO-GO**.
