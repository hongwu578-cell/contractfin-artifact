#!/usr/bin/env python3
"""Build the integrated ContractFin SCI manuscript v3 from gated source drafts."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def section_from(text: str, heading: str) -> str:
    index = text.find(heading)
    if index < 0:
        raise ValueError(f"missing heading: {heading}")
    return text[index:]


def section_between(text: str, start_heading: str, end_heading: str) -> str:
    start = text.find(start_heading)
    end = text.find(end_heading, start + len(start_heading))
    if start < 0 or end < 0:
        raise ValueError(f"cannot extract section from {start_heading} to {end_heading}")
    return text[start:end].rstrip()


def build(intro_path: Path, methods_path: Path) -> str:
    intro_source = intro_path.read_text(encoding="utf-8")
    methods_source = methods_path.read_text(encoding="utf-8")

    intro = section_from(intro_source, "## 1. Introduction")
    intro = intro.replace(
        "The held-out design freezes a deterministic, operation-stratified sample of 500 FinQA test items before inference. B0 and B1 are evaluated on the same items with balanced within-pair execution order. The primary outcome is full-sample final-answer correctness, analyzed with an exact paired test. Secondary outcomes cover canonical-program correctness, executable-program correctness, evidence F1, and response coverage; resource and stability measurements characterize the quality–cost trade-off. Inference artifacts are answer stripped, predictions must be made immutable before evaluation, and returned model identifiers are logged because a provider alias may not denote an immutable backend snapshot.",
        "The held-out design froze a deterministic, operation-stratified sample of 500 FinQA test items before inference. B0 and B1 were evaluated on the same items with balanced within-pair execution order. The primary outcome was full-sample final-answer correctness, analyzed with an exact paired test. Secondary outcomes covered canonical-program correctness, executable-program correctness, evidence F1, and response coverage; resource and stability measurements characterized the quality–cost trade-off. Inference artifacts were answer stripped, predictions were made immutable before evaluation, and returned model identifiers were logged because a provider alias may not denote an immutable backend snapshot.",
    )
    intro = intro.replace(
        "The paper therefore does not assume that tools are always preferable to teamwork, or that multi-agent systems are intrinsically unreliable. It tests a sequential engineering claim: before attributing value to additional model-controlled roles, a study should establish what a single agent gains from deterministic tools and whether the multi-agent implementation itself satisfies the same reliability contract. The held-out results will determine the empirical answer for the registered FinQA setting; the present manuscript does not infer that answer from development data.",
        "The paper therefore does not assume that tools are always preferable to teamwork, or that multi-agent systems are intrinsically unreliable. It tests a sequential engineering claim: before attributing value to additional model-controlled roles, a study should establish what a single agent gains from deterministic tools and whether the multi-agent implementation itself satisfies the same reliability contract. On the registered held-out sample, B1 improved final-answer accuracy by five percentage points over B0, but required substantially more calls and tokens; the B2 implementations failed their development-stage structural gates. The resulting evidence favors tool use before additional teamwork in this implementation and task setting, while preserving a strict boundary against generalizing the B2 result to multi-agent systems as a class.",
    )

    methods_and_results = section_between(
        methods_source,
        "## 3. Methods",
        "### 4.9 Threats to validity",
    )
    methods_and_results = methods_and_results.replace(
        "The frozen protocol covers 34 hashed data, configuration, code, test, and report files. The runtime remains immutable and unauthorized. Future live execution requires a separate dated authorization artifact bound to the frozen runtime hash and experiment scope; authorization does not modify the runtime itself. The source code, manifests, schedules, power analysis, and local audit passed 62 unit tests, two no-network dry runs, and a final read-only lock verification.",
        "The frozen protocol covers 34 hashed data, configuration, code, test, and report files. Runtime configurations remained immutable; live primary and stability execution was enabled only through dated authorization artifacts bound to the frozen runtime hash and experiment scope. Before live inference, the source code, manifests, schedules, power analysis, and local audit passed 62 unit tests, two no-network dry runs, and a read-only lock verification. After analysis, the same 62 tests passed again and the lock verification reported no hash mismatch among the 34 frozen files.",
    )
    methods_and_results = methods_and_results.replace(
        "The main paper should report the failure taxonomy and the 16/22 false-acceptance observation as formative evidence. Detailed item identifiers, traces, and rejected-candidate observability gaps belong in the supplement. The appropriate conclusion is that adding fixed roles did not automatically create independent error detection in these development implementations—not that all multi-agent architectures are inferior.",
        "Among the 22 candidates accepted by the B2-v1.1 verifier, 16 were ultimately incorrect, a formative false-acceptance rate of 72.73%. Detailed item identifiers, traces, and rejected-candidate observability gaps are retained in the supplementary artifacts. This result shows that adding fixed roles did not automatically create independent error detection in these development implementations; it does not establish that multi-agent architectures are generally inferior.",
    )

    abstract = """## Abstract

Large language model systems for financial numerical reasoning can be extended either with deterministic tools or with multiple model-controlled roles, but these interventions are often evaluated as bundled architectural changes. We conducted a preregistered, paired systems study that separated direct generation (B0), a tool-augmented single agent using deterministic document search and constrained calculation (B1), and exploratory fixed-role multi-agent pipelines (B2). B0 and B1 were compared on the same operation-stratified sample of 500 FinQA test items under balanced execution order, delayed gold access, immutable prediction artifacts, and full intention-to-test denominators. B1 answered 235/500 items correctly (47.0%) versus 210/500 for B0 (42.0%), a paired difference of +5.0 percentage points (95% bootstrap confidence interval, +1.4 to +8.8; exact McNemar p=0.01146). Program correctness increased from 18.6% to 39.0%, and executable-program correctness from 24.8% to 51.6%, whereas evidence F1 and response coverage did not improve significantly after multiplicity correction. The gain required 3.22 times as many model calls and 2.41 times as many tokens. In a preregistered 100-item, three-run stability analysis, correctness changed across runs for 12% of B0 items and 17% of B1 items. Both B2 variants failed development-stage structural gates; B2-v1.1's verifier accepted 16 incorrect candidates among 22 accepted outputs. Deterministic tool access therefore improved held-out financial numerical reasoning in this setting, but introduced a clear quality–cost trade-off and did not eliminate answer–program synchronization failures. Additional model-controlled roles should be evaluated as executable system components with explicit failure gates rather than assumed to provide independent verification.

**Keywords:** financial numerical reasoning; large language models; tool-augmented agents; multi-agent systems; preregistered evaluation; reliability; cost-aware evaluation
"""

    discussion = """## 5. Discussion

### 5.1 Tool augmentation improved the registered primary outcome

The confirmatory comparison supports the narrow claim tested in this study: under a matched provider, requested model alias, item set, output contract, and paired schedule, deterministic tool augmentation improved final-answer correctness relative to direct generation. The five-point gain was not an artifact of excluding failures or conditioning on completed answers. All 500 registered items remained in the intention-to-test denominator, and the advantage arose from 58 B1-only correct items versus 33 B0-only correct items. The prevalence-weighted descriptive estimate for the full FinQA test composition was similar, which reduces concern that deliberate coverage of rare operation strata alone produced the observed direction.

The result should nevertheless be interpreted as an architectural comparison, not as an isolated estimate of calculator value. B1 changed the interaction pattern as well as access to deterministic functions: it could retrieve evidence, invoke a constrained executor, observe tool output, and continue for several model turns. The study therefore establishes the performance of the complete tool-augmented system relative to the complete direct-generation system. It does not identify how much of the gain came from arithmetic execution, retrieval, extra inference opportunity, or their interaction. That distinction matters when translating the result into deployment decisions: tool access is beneficial here, but the measured effect belongs to a specified software architecture and budget.

### 5.2 Executable reasoning and final answers remained partially decoupled

The largest improvements occurred in machine-checkable computation. B1 more than doubled program ITT correctness and executable-program ITT correctness, while evidence F1 and coverage did not materially improve. Paired mechanism records point in the same direction: many B1-only gains were program or execution recoveries rather than improvements in evidence overlap. Deterministic calculation therefore addressed an important failure surface, but it did not make evidence selection uniformly better.

At the same time, executable reasoning did not guarantee a correct reported answer. Sixty-one B1 items had a program that executed to the reference answer but an incorrect final answer, compared with 17 for B0. The conditional consistency between an execution-correct program and the final answer was consequently lower for B1. This exposes an output-boundary problem: the system can obtain or construct a correct computation and still lose correctness when formatting, rounding, rescaling, or copying the result into a separately generated answer field. For financial applications, this distinction is operationally important. Auditable tool traces are valuable only if the final response is deterministically reconciled with the executed result. A production-oriented successor should bind the displayed answer to the executor output or apply a semantic consistency gate across answer, program, unit, and status fields.

### 5.3 Accuracy gains carried material resource costs

B1's higher accuracy required 1,610 model calls instead of 500 and 2.41 times as many tokens. Tokens per correct answer more than doubled, even though aggregate latency per correct answer remained similar in this provider run. The result is therefore better described as a quality–token-cost trade-off than as a general efficiency improvement. Whether that trade-off is acceptable depends on the application: an offline document-analysis workflow may tolerate additional calls for a five-point accuracy gain, whereas a high-volume or latency-constrained service may not.

The stability experiment adds a second caution. B1 had lower median within-item token and latency coefficients of variation than B0, yet more B1 items changed correctness state across the three runs. Resource stability and semantic stability were thus not interchangeable. A system can consume a similar amount of computation on repeated calls while still crossing the correct/incorrect boundary. Repeated evaluation, immutable model snapshots where available, and output-level consistency checks remain necessary even when tool use makes control flow appear more structured.

### 5.4 More roles did not create reliable verification in the implemented pipelines

The B2 development evidence explains why structural acceptance preceded any held-out multi-agent claim. Both fixed-role variants consumed more resources than B1 and failed to complete the registered development protocol reliably. Their traces showed evidence-contract violations, shared-budget exhaustion, cross-field inconsistency, output-ceiling failures, and verifier false acceptance. Most notably, the B2-v1.1 verifier accepted 16 incorrect candidates among 22 accepted outputs. Naming a model-controlled component “verifier” did not provide the behavior of a trained verifier or deterministic checker [@cobbe2021training; @lightman2023verify].

This finding is local to the implemented pipelines. It does not show that multi-agent systems are intrinsically ineffective, nor does it compare a structurally valid B2 system with B1 on the held-out sample. Instead, it establishes a methodological boundary: role decomposition should not enter a confirmatory comparison until the resulting system can satisfy the same completion, evidence, budget, and output-consistency contract as simpler alternatives. Multi-agent evaluation should report how disagreements are resolved, whether verification decisions are correct, which role consumes the shared budget, and whether repeated agents provide independent evidence or merely correlated restatements.

### 5.5 Implications for financial AI system design

Three engineering implications follow. First, deterministic capabilities should be added at the narrowest failure boundary. In this study, search and calculation improved the aspects of reasoning they could directly support without requiring a larger coordination architecture. Second, program execution should be connected to a deterministic finalization layer. Returning both an executable program and a separately generated answer creates an avoidable synchronization surface. Third, architecture gates should precede score comparisons. Completion rate, evidence-contract compliance, infrastructure failures, returned-model identity, and verifier false acceptance are properties of the evaluated system, not ancillary implementation details.

These principles are especially relevant in finance, where a numerically plausible answer may still be unusable if its evidence, operation, units, or audit trail are wrong. The appropriate optimization target is not raw answer accuracy alone, nor the number of agents, but a bounded system that produces mutually consistent and inspectable outputs at a disclosed resource cost.

### 5.6 Limitations and future work

The provider exposed a dynamic model alias rather than a guaranteed immutable snapshot. Balanced temporal blocking, returned-model logging, and a mismatch threshold reduced this risk but could not detect unreported backend changes. The experiment involved one provider, one requested alias, one primary dataset, and two architectures that passed development gates. FinQA offers executable programs and controlled scoring, but it is narrower than forecasting, investment research, compliance, advisory, or open-ended financial decision support.

The primary comparison also bundled deterministic tool access with additional interaction turns; a factorial study would be needed to separate retrieval, execution, and inference-budget effects. The 100-item stability analysis was descriptive, and its additional runs were not treated as independent observations in the primary test. Rare operation strata remained small despite deliberate coverage, so subgroup estimates should guide follow-up work rather than support strong stratum-specific claims. Finally, the B2 observations came from development data and structurally incomplete implementations. A future multi-agent study should preregister a revised architecture only after it passes stronger local tests for candidate observability, evidence-packet enforcement, budget isolation, and answer–program consistency. Cross-provider replication and external validation on benchmarks such as TAT-QA or FinanceBench would provide a stronger test of generalizability.
"""

    conclusion = """## 6. Conclusion

This study evaluated a sequential architecture question for financial numerical reasoning: what is gained by adding deterministic tools before adding more model-controlled roles? On a preregistered, paired sample of 500 FinQA items, a tool-augmented single agent improved final-answer accuracy from 42.0% to 47.0% and produced substantially more correct and executable programs than direct generation. The improvement was statistically supported but required more than three times as many model calls and 2.41 times as many tokens. Repeated-call analysis further showed that lower resource dispersion did not imply stable correctness, and mechanism analysis identified a persistent gap between correct program execution and the separately reported final answer.

The exploratory multi-agent implementations did not satisfy the development-stage reliability contract and therefore were not promoted to the held-out comparison. Their failures reinforce a practical conclusion: additional roles do not constitute verification unless the verifier's decisions and the system's handoffs are themselves evaluated. For the registered FinQA setting, the evidence supports tool use before teamwork—not as a universal ordering of architectures, but as a disciplined engineering strategy. Add deterministic support where the failure is deterministic, bind executed results to final outputs, and require every increase in model-controlled complexity to earn its place through explicit structural and cost-aware evaluation.

## Data and Artifact Availability

FinQA is a public benchmark available from its cited source. The study package contains the frozen manifests, answer-stripped inference inputs, interleaved schedules, runtime configurations, authorization records, immutable predictions, task logs, evaluation reports, statistical outputs, and SHA-256 lock file used for this analysis. A public archival repository identifier should be added when the submission venue and release location are selected.

## References

References are maintained in `references_verified_v1.bib` and will be rendered in the target journal's required style during submission formatting.
"""

    title = "# Tool Use Before Teamwork: A Cost-Aware and Auditable Evaluation of LLM Architectures for Financial Numerical Reasoning"
    provenance = (
        "<!-- Integrated working manuscript v3. "
        f"Introduction/Related Work source SHA-256: {sha256_file(intro_path)}; "
        f"Methods/Results source SHA-256: {sha256_file(methods_path)}. -->"
    )
    return "\n\n".join(
        [
            title,
            provenance,
            abstract.strip(),
            intro.strip(),
            methods_and_results.strip(),
            discussion.strip(),
            conclusion.strip(),
        ]
    ) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--intro",
        default="manuscript/contractfin_sci_introduction_related_work_v1.md",
    )
    parser.add_argument(
        "--methods",
        default="manuscript/contractfin_sci_methods_experiments_v2.md",
    )
    parser.add_argument(
        "--output",
        default="manuscript/contractfin_sci_full_v3.md",
    )
    args = parser.parse_args()
    intro_path = (PROJECT_ROOT / args.intro).resolve()
    methods_path = (PROJECT_ROOT / args.methods).resolve()
    output_path = (PROJECT_ROOT / args.output).resolve()
    output_path.write_text(build(intro_path, methods_path), encoding="utf-8")
    try:
        display_path = output_path.relative_to(PROJECT_ROOT)
    except ValueError:
        display_path = output_path
    print(f"wrote {display_path} sha256={sha256_file(output_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
