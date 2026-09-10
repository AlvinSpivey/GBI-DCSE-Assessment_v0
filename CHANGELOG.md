# Assessment v0 - change index

![Assessment update](docs/application/figures/updated.svg)

This is an outcome-report update to the archived BoundaryBench narrative, not a
replacement of its frozen results or a full source release. Yellow denotes an
addition or revision relative to that narrative. Each row names its included
outcome extract; none implies a new experiment during edition preparation.

| ID | Previous reader context | What this edition adds | Included evidence |
|---|---|---|---|
| U01 | Synthetic legacy-EHR records | Actual canonical counts, sampling method and demographic limitations | `dataset_summary.json` |
| U02 | v0.1 refusal at the structured-output boundary | Reported BeTaL, GBI and DCSE reference-suite outcomes | `reference_summary.json` |
| U03 | Broader architectural aims | Original 99-claim accounting: 95 met, one erratum, three out of scope | `reference_summary.json` |
| U04 | Qwen3-4B frozen held-out result | A separate eight-case Qwen2.5-0.5B development run that also failed the output contract | `model_summary.json`, `model_task_outcomes.csv` |
| U05 | RPMS-shaped record mapping goal | Reported deterministic FHIR representation repair, with before/after denominators | `fhir_summary.json` |
| U06 | Further model and application evaluation | A phased plan separating model, FHIR, policy and clinical requirements | `next_evidence.csv` |

All extract files above are in `artifacts/assessment_v0/`. The six historical
aggregate files are byte-preserved. No original recorded score is replaced.
