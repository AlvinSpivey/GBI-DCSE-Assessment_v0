# Data card - canonical synthetic fixture

![Assessment update](application/figures/updated.svg)

**Source kind:** separately identified Synthea alternative. The exact earlier Pine
Ridge source is documented as unavailable. This distribution contains aggregate
summaries only, not source patient rows or original FHIR bundles.

**Counts:** 310 synthetic subjects; 10,934 encounters; 805 problems; 40,053
observations. Total canonical records: 52,102. The supplied report also records
63,780 corruption events; those are not extra independent patients.

**Selection:** first 310 sorted source-bundle paths, not a random IHS sample.
All 310 synthetic state fields are Massachusetts. Synthetic race fields comprise
220 White, 35 Black or African American, 31 Other, 23 Asian and one American Indian
or Alaska Native. All ethnicity fields are recorded as Not Hispanic or Latino.
These labels describe generated records, not actual people.

**Reported integrity:** unique canonical source IDs, no orphan canonical links,
16/16 metadata hashes, no scanned model-input reference fields and no recorded
split task/source ID overlap. A finite integrity check does not prove universal
absence of leakage or appropriate population coverage.

**Split distinction:** packaged public development has 64 tasks, eight per family;
packaged held-out evaluation has 256 tasks, 32 per family. The additional small-model
run instead used the older eight public-development fixtures, one per family.

**Not established:** IHS representativeness, clinic-specific mapping validity,
clinical missingness behavior, patient-level independent sampling, or appropriate
performance across Tribal communities. A demographic fraction alone is neither
a bias test nor evidence of transportability.

Machine-readable selected summary: [dataset_summary.json](../artifacts/assessment_v0/dataset_summary.json).
