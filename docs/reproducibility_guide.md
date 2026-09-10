# Reproducibility guide

This is an **outcome-review snapshot**, not a full experiment-source release.

## Available here

Six byte-preserved v0.1 aggregate files; separately authored selected outcome
summaries for the dataset, reference suites, additional model run and FHIR
conversion; a per-family model outcome table; conventional report-checking code;
static figures and a review page.

## What the two commands verify

```bash
python scripts/verify_review.py
python -m unittest discover -s tests -v
```

The commands check the declared snapshot inventory, content hashes, type/range
constraints and internal arithmetic. They check that reported denominators and
limits are not silently changed. The unit tests deliberately mutate those inputs.
They are tests of the new review checker, not extra clinical or model trials.

## What cannot be reproduced from this snapshot

Original model generation, raw-output scoring, dataset acquisition, the underlying
GBI/DCSE reference-suite execution and full deterministic FHIR conversion.
Those source files and raw artifacts are not included. A summary's consistency
with another included summary does not independently establish how either was
obtained. A SHA-256 inventory detects changes relative to itself, not coordinated
fabrication of both the inventory and the records. Compare an approved manifest
through an independently trusted channel when authenticity matters.

## Baseline and new extract identities

The original six v0.1 files are retained without edits, including their original
NOT_RUN and null fields. New files under `artifacts/assessment_v0` are explicitly
identified as selected outcome summaries. Their field names and layout are
publication formats, not replicas of the source reports. Source-level provenance
and rights decisions remain with the maintainer.

Python caches, a root `.git` directory and its internals are excluded from the
working-tree inventory by the checker. Its PASS therefore does not assess Git
history or remote platform metadata.
