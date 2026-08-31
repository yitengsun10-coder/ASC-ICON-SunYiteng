#!/usr/bin/env python3
"""Parse ICON batch-run TSV into a compact, auditable JSON summary."""
from __future__ import annotations

import argparse
import csv
import json
import pathlib
import re


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("runs", type=pathlib.Path)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()
    rows = []
    with args.runs.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            log_path = pathlib.Path(row["log"])
            text = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
            row["mpi_ranks"] = int(row["mpi_ranks"])
            row["wall_seconds"] = float(row["wall_seconds"])
            row["icon_success_marker"] = bool(
                re.search(r"ICON.*finished|simulation.*finished|normal termination", text, re.I)
            )
            row["error_lines"] = [
                line for line in text.splitlines()
                if re.search(r"\b(error|fatal|abort)\b", line, re.I)
            ][-10:]
            rows.append(row)
    valid = [r for r in rows if r["status"] == "success" and r["icon_success_marker"]]
    best = min(valid, key=lambda r: r["wall_seconds"]) if valid else None
    payload = {"runs": rows, "best_valid_run": best, "valid_runs": len(valid)}
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

