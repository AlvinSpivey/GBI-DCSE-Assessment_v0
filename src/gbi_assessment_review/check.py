"""Ordinary file-inventory and reported-outcome checks, not an experiment engine.

No network or model calls occur. A passing result establishes consistency of this
fixed report only; original inference, source acquisition and validation are not
repeated. Self-contained hashes cannot establish source honesty.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

FAMILIES = {
    "patient_identity_normalization", "orphan_duplicate_detection", "field_anomaly_bleed",
    "code_system_version_validation", "rpms_to_fhir_mapping", "temporal_status_classification",
    "evidence_sufficiency", "policy_action_selection",
}
MODES = {"output_only", "token_top_k", "full_category_evidence"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        require(key not in result, "Duplicate JSON key: " + key)
        result[key] = value
    return result


def _invalid_constant(value: str) -> None:
    raise ValueError("Non-finite JSON constant: " + value)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_pairs,
                      parse_constant=_invalid_constant)


def nonnegative_integer(value: Any, label: str) -> int:
    require(type(value) is int and value >= 0, label + " must be a nonnegative integer")
    return value


def _false(record: dict[str, Any], *keys: str) -> None:
    for key in keys:
        require(record[key] is False, "Unsupported promotion of " + key)


def inventory(root: Path) -> int:
    """Inspect the working tree, excluding only root .git and Python caches."""
    require(root.is_dir() and not root.is_symlink(), "A real review directory is required")
    manifest = read_json(root / "MANIFEST.json")
    require(manifest["format"] == "gbi-dcse-assessment-v0-file-list", "Unknown inventory")
    expected = manifest["files"]
    require(type(expected) is dict and bool(expected), "Empty file list")
    actual = set()
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if relative.parts[0] == ".git" or "__pycache__" in relative.parts:
            continue
        require(not path.is_symlink(), "Symlink not permitted: " + str(relative))
        if path.is_file():
            actual.add(relative.as_posix())
    require(actual == set(expected) | {"MANIFEST.json"}, "Missing or unexpected review file")
    for name, info in expected.items():
        path = Path(name)
        require(not path.is_absolute() and ".." not in path.parts and "\\" not in name,
                "Invalid inventory path")
        raw = (root / name).read_bytes()
        require(info["bytes"] == len(raw), "Length mismatch: " + name)
        require(info["sha256"] == hashlib.sha256(raw).hexdigest(), "Hash mismatch: " + name)
    return len(actual)


def load_outcomes(root: Path) -> dict[str, Any]:
    new = root / "artifacts/assessment_v0"
    old = root / "artifacts/empirical/scored_v0_1"
    result = {name: read_json(new / (name + "_summary.json"))
              for name in ("dataset", "model", "fhir", "reference")}
    result.update(aggregate=read_json(old / "aggregate_metrics.json"),
                  modes=read_json(old / "per_mode_metrics.json"),
                  statuses=read_json(old / "status_distributions.json"),
                  risk_plot=read_json(old / "risk_coverage_plot_data.json"),
                  review_status=read_json(root / "REVIEW_STATUS.json"))
    with (new / "model_task_outcomes.csv").open(encoding="utf-8", newline="") as handle:
        result["model_tasks"] = list(csv.DictReader(handle))
    with (old / "task_family_slice_metrics.csv").open(encoding="utf-8", newline="") as handle:
        result["historical_slices"] = list(csv.DictReader(handle))
    return result


def validate_outcomes(data: dict[str, Any]) -> dict[str, int | None]:
    d, m, f, r = (data[k] for k in ("dataset", "model", "fhir", "reference"))
    for record in (d, m, f, r):
        require(record["record_kind"] == "selected_outcome_summary", "Summary origin misrepresented")
    require(d["counts"] == {"patients":310, "encounters":10934, "problems":805, "labs":40053},
            "Canonical counts differ from this report")
    for kind, value in d["counts"].items():
        nonnegative_integer(value, kind)
    require(sum(d["counts"].values()) == d["total_records"] == 52102, "Canonical denominator mismatch")
    for key in ("synthetic_state_counts", "synthetic_race_counts", "synthetic_ethnicity_counts"):
        require(sum(nonnegative_integer(v, key) for v in d[key].values()) == 310,
                "Demographic denominator mismatch")
    require(d["synthetic_state_counts"] == {"Massachusetts":310}, "Synthetic geography changed")
    require(d["synthetic_race_counts"]["American Indian or Alaska Native"] == 1, "Synthetic race count changed")
    require(d["independent_clinical_sample_size"] is None, "Clinical sampling inference is unsupported")
    _false(d, "IHS_representativeness_established", "raw_dataset_included")
    require(d["metadata_hashes_verified"] == d["metadata_hashes_total"] == 16, "Metadata counts disagree")
    for split, total in (("public_dev",64), ("heldout_eval",256)):
        row = d["split_counts"][split]
        require(set(row["families"]) == FAMILIES, "Unknown or missing task family")
        require(row["tasks"] == total == sum(row["families"].values()), "Split denominator mismatch")
        require(set(row["families"].values()) == {total // 8}, "Family balance changed")

    require(m["model"] == "Qwen/Qwen2.5-0.5B-Instruct" and
            m["revision"] == "7ae557604adf67be50417f59c2c2f167def9a775", "Added model identity changed")
    require(m["completed"] == 8 and type(m["completed"]) is int, "Eight development executions required")
    require(m["format_admitted"] == m["benchmark_correct"] == 0, "Added completion outcome changed")
    require(m["grade_histogram"] == {"safe_parse_reject":6,"safe_schema_reject":2}, "Added rejection counts disagree")
    require(m["population_risk_bound"] is None, "No population bound was estimated")
    _false(m, "held_out", "raw_outputs_included", "new_inference_for_this_edition")
    rows = data["model_tasks"]
    require(len(rows) == 8 and {row["task_family"] for row in rows} == FAMILIES,
            "Eight unique fixture families required")
    require(Counter(row["result"] for row in rows) == m["grade_histogram"], "CSV/JSON rejection disagreement")
    require(sum(row["finish_reason"] == "length" for row in rows) == m["length_limited"] == 2,
            "Length-limited outcome disagreement")
    for row in rows:
        require(row["completed"] == "1" and row["format_admitted"] == row["benchmark_correct"] == "0",
                "CSV completion changed")
        require(row["finish_reason"] in {"eos", "length"}, "Unexpected finish reason")
        require(int(row["output_tokens"]) > 0, "Invalid token count")
        elapsed = float(row["elapsed_seconds"])
        require(math.isfinite(elapsed) and elapsed > 0, "Invalid duration")

    by_type = {"Patient":d["counts"]["patients"],"Encounter":d["counts"]["encounters"],
               "Condition":d["counts"]["problems"],"Observation":d["counts"]["labs"]}
    require(f["canonical_input_records"] == d["total_records"], "FHIR input denominator mismatch")
    require(f["after"]["valid_by_resource"] == by_type and f["after"]["conversion_failures"] == 0,
            "Post-correction counts disagree")
    before = dict(by_type, Observation=38645)
    require(f["before"]["valid_by_resource"] == before and f["before"]["conversion_failures"] == 1408,
            "Original conversion failures not retained")
    for stage in ("before", "after"):
        require(sum(f[stage]["valid_by_resource"].values()) + f[stage]["conversion_failures"] == 52102,
                "Conversion outcome denominator mismatch")
    require(f["reported_schema_negative_controls"] == f["reported_schema_negative_controls_rejected"] == 5,
            "Schema control counts disagree")
    _false(f, "clinical_approval", "full_HL7_validator_run", "US_Core_6_1_0_validated",
           "is_model_generated_resource_score", "implementation_included")
    require(f["IHS_endpoint_calls"] == 0, "No endpoint execution is established")

    require(r["registered_claims"] == 99 and r["testable_claims"] == 96, "Claim denominators changed")
    require(r["claims_recorded_met"] == 95 and r["claims_erratum"] == 1 and r["claims_out_of_scope"] == 3,
            "Original exceptions must remain visible")
    require(r["claims_recorded_met"] + r["claims_erratum"] == r["testable_claims"], "Testable claims disagree")
    require(r["testable_claims"] + r["claims_out_of_scope"] == r["registered_claims"], "Claim totals disagree")
    require([r[k] for k in ("baseline_unit_checks", "BeTaL_v0_2_checks_reported_passed",
            "GBI_v2_checks_reported_passed", "DCSE_v3_checks_reported_passed")] == [109,319,72,148],
            "Reference-suite counts differ from source report")
    require(r["new_model_executions_in_reference_suites"] == 0, "Reference checks are not model trials")
    _false(r, "new_execution_for_this_edition", "full_implementation_included")

    a = data["aggregate"]
    require(a["canonical_execution_count"] == 768 and a["mode_count"] == 3, "Historical denominator changed")
    require(a["coverage"] == a["verified_completion"] == a["canonical_result_count"] == 0,
            "Historical outcome changed")
    require(a["selective_risk"] is None, "Zero-coverage risk must stay undefined")
    require(a["quarantine_count"] == 768 and a["invalid_output_rate"] == 1, "Historical refusal count changed")
    for key in ("confidence_intervals", "repeat_run_stability", "reported_provider_cost_usd"):
        require(a[key] == "NOT_RUN", "Historical unexecuted metric promoted")
    modes = data["modes"]["rows"]
    require(len(modes) == 3 and {row["evidence_mode"] for row in modes} == MODES, "Historical modes changed")
    for row in modes:
        s = data["statuses"]["canonical_runs"][row["evidence_mode"]]
        require(row["task_count"] == 256, "Historical per-mode task count changed")
        require(row["coverage"] == 0 and row["selective_risk"] is None, "Historical per-mode risk changed")
        require(row["parse_schema_status_distribution"] == s["parse_schema_status_distribution"] ==
                {"safe_parse_reject":123,"safe_schema_reject":133}, "Runner histogram differs")
        require(row["run_id"] == s["run_id"], "Canonical run changed")
        require(row["verifier_grade_status_distribution"] == {"safe_parse_reject":256}, "Verifier histogram differs")
    slices = data["historical_slices"]
    require(len(slices) == 24 and len({(x["evidence_mode"],x["task_family"]) for x in slices}) == 24,
            "Historical mode/family rows changed")
    for row in slices:
        require(row["evidence_mode"] in MODES and row["task_family"] in FAMILIES and int(row["task_count"]) == 32,
                "Historical family scope changed")
        require(row["selective_risk"] == "" and int(row["verified_completion"]) == 0, "Historical family outcome changed")
    require(data["risk_plot"]["points"] == [] and data["risk_plot"]["status"] == "NOT_RUN", "Undefined risk curve promoted")
    status = data["review_status"]
    require(status["intended_repository"] == "AlvinSpivey/GBI-DCSE-Assessment_v0", "Wrong repository name")
    require(status["status"] == "PRIVATE_OWNER_REVIEW_CANDIDATE", "Unexpected review status")
    _false(status, "clinical_approval", "legal_clearance", "public_release_authorized",
           "full_implementation_release", "new_empirical_execution_in_this_edition")
    return {"canonical_records":52102,"historical_model_executions":768,
            "added_model_executions":8,"added_admitted_results":0,"claim_register_count":99,
            "selective_risk":None}


def check(root: Path) -> dict[str, Any]:
    root = root.resolve()
    files = inventory(root)
    values = validate_outcomes(load_outcomes(root))
    return dict(status="PASS_REPORT_CONSISTENCY", checked_files=files, results=values,
                original_experiments_rerun=False, full_implementation_reproduced=False,
                remote_repository_inspected=False, public_release_authorized=False,
                legal_clearance=False)
