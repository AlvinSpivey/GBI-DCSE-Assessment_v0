#!/usr/bin/env python3
"""Check the local report inventory and arithmetic; never publish or make network calls."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gbi_assessment_review.check import check

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        print(json.dumps(check(args.root), indent=2, sort_keys=True))
        return 0
    except (ValueError, KeyError, TypeError, OSError, OverflowError) as exc:
        print("REPORT_CHECK_FAILED: " + str(exc), file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
