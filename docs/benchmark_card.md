# Benchmark card - boundaries kept distinct

**Purpose:** evaluate explicit output-format and task requirements for synthetic
legacy-EHR transformations. The eight task families remain those in the original
BoundaryBench README. Correct abstention can satisfy a task; parse failure cannot
be substituted for a correct abstention.

**Historical model evaluation:** Qwen3-4B-Instruct-2507; 256 held-out tasks;
three evidence modes; 768 executions; no accepted results. No selective-risk
estimate exists at zero coverage.

![Assessment update](application/figures/updated.svg)

**Added model evaluation:** Qwen2.5-0.5B-Instruct; eight original public-development
fixtures; all inference completed; no format-admitted or correct results. The
model revision and per-family outcomes are retained in the selected summaries.
This is not a held-out model comparison.

**Reference suites:** BeTaL v0.2, GBI v2 and DCSE v3 test their declared synthetic
or software properties. They execute no new model. Reported check counts cannot
be pooled into a clinical sample or a statistical success rate.

**Clinical boundary:** benchmark references do not establish diagnosis, treatment,
terminology equivalence, institutional policy correctness or safe autonomous
write-back. The repository is not an IHS-endorsed benchmark.
