"""Report-checker tests. These do not add any model or patient observations."""
from __future__ import annotations
import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gbi_assessment_review.check import check, inventory, load_outcomes, read_json, validate_outcomes

class ReportTests(unittest.TestCase):
    def setUp(self):
        self.data = load_outcomes(ROOT)

    def reject(self, change):
        values = copy.deepcopy(self.data)
        change(values)
        with self.assertRaises((ValueError, KeyError, TypeError)):
            validate_outcomes(values)

    def test_complete_report(self):
        result = check(ROOT)
        self.assertEqual(result["status"], "PASS_REPORT_CONSISTENCY")
        self.assertFalse(result["original_experiments_rerun"])
        self.assertFalse(result["legal_clearance"])

    def test_canonical_denominator(self):
        self.reject(lambda d: d["dataset"].update(total_records=52103))

    def test_subjects_are_not_record_count(self):
        self.reject(lambda d: d["dataset"]["counts"].update(patients=52102))

    def test_boolean_is_not_count(self):
        self.reject(lambda d: d["dataset"]["counts"].update(patients=True))

    def test_demographic_denominator(self):
        self.reject(lambda d: d["dataset"]["synthetic_race_counts"].update(White=219))

    def test_ihs_inference_is_not_promoted(self):
        self.reject(lambda d: d["dataset"].update(IHS_representativeness_established=True))

    def test_independent_clinical_n_is_not_invented(self):
        self.reject(lambda d: d["dataset"].update(independent_clinical_sample_size=52102))

    def test_dev_splits_remain_distinct(self):
        self.reject(lambda d: d["dataset"]["split_counts"]["public_dev"].update(tasks=8))

    def test_added_model_identity(self):
        self.reject(lambda d: d["model"].update(model="different"))

    def test_added_model_score(self):
        self.reject(lambda d: d["model"].update(benchmark_correct=1))

    def test_heldout_is_not_claimed(self):
        self.reject(lambda d: d["model"].update(held_out=True))

    def test_output_histogram(self):
        self.reject(lambda d: d["model"]["grade_histogram"].update(safe_parse_reject=5))

    def test_csv_must_agree(self):
        self.reject(lambda d: d["model_tasks"][0].update(format_admitted="1"))

    def test_length_limits(self):
        self.reject(lambda d: d["model"].update(length_limited=0))

    def test_no_nan_duration(self):
        self.reject(lambda d: d["model_tasks"][0].update(elapsed_seconds="NaN"))

    def test_duplicate_model_family(self):
        self.reject(lambda d: d["model_tasks"].__setitem__(0, copy.deepcopy(d["model_tasks"][1])))

    def test_original_fhir_failures_retained(self):
        self.reject(lambda d: d["fhir"]["before"].update(conversion_failures=0))

    def test_repaired_fhir_denominator(self):
        self.reject(lambda d: d["fhir"]["after"]["valid_by_resource"].update(Observation=40054))

    def test_schema_not_clinical(self):
        self.reject(lambda d: d["fhir"].update(clinical_approval=True))

    def test_full_validator_not_claimed(self):
        self.reject(lambda d: d["fhir"].update(full_HL7_validator_run=True))

    def test_erratum_retained(self):
        self.reject(lambda d: d["reference"].update(claims_recorded_met=96,claims_erratum=0))

    def test_scope_exclusions_retained(self):
        self.reject(lambda d: d["reference"].update(claims_out_of_scope=0))

    def test_suite_counts_not_new_model_trials(self):
        self.reject(lambda d: d["reference"].update(new_model_executions_in_reference_suites=148))

    def test_zero_coverage_risk_undefined(self):
        self.reject(lambda d: d["aggregate"].update(selective_risk=0))

    def test_no_unrun_confidence_interval(self):
        self.reject(lambda d: d["aggregate"].update(confidence_intervals=[0,0]))

    def test_original_histogram(self):
        self.reject(lambda d: d["modes"]["rows"][0]["parse_schema_status_distribution"].update(safe_schema_reject=132))

    def test_historical_family_rows(self):
        self.reject(lambda d: d["historical_slices"].pop())

    def test_public_approval_never_inferred(self):
        self.reject(lambda d: d["review_status"].update(public_release_authorized=True))

    def test_selected_summary_label(self):
        self.reject(lambda d: d["model"].update(record_kind="original_raw_log"))

    def test_duplicate_json(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "test.json"
            p.write_text('{"a":1,"a":2}')
            with self.assertRaises(ValueError): read_json(p)

    def test_nonfinite_json(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "test.json"
            p.write_text('{"a":NaN}')
            with self.assertRaises(ValueError): read_json(p)

    def copied(self, tmp):
        out = Path(tmp) / "review"
        shutil.copytree(ROOT, out, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        return out

    def test_changed_file(self):
        with tempfile.TemporaryDirectory() as t:
            out=self.copied(t)
            (out/"README.md").write_text("changed")
            with self.assertRaises(ValueError): inventory(out)

    def test_extra_file(self):
        with tempfile.TemporaryDirectory() as t:
            out=self.copied(t)
            (out/"extra.log").write_text("not listed")
            with self.assertRaises(ValueError): inventory(out)

    def test_removed_file(self):
        with tempfile.TemporaryDirectory() as t:
            out=self.copied(t)
            (out/"README.md").unlink()
            with self.assertRaises(ValueError): inventory(out)

    def test_symlink(self):
        with tempfile.TemporaryDirectory() as t:
            out=self.copied(t)
            (out/"README.md").unlink()
            (out/"README.md").symlink_to(ROOT/"README.md")
            with self.assertRaises(ValueError): inventory(out)

    def test_no_legal_clearance(self):
        self.reject(lambda d: d["review_status"].update(legal_clearance=True))

if __name__ == "__main__": unittest.main()
