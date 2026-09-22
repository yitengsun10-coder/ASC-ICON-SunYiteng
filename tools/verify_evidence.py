#!/usr/bin/env python3
"""Verify archived ICON representative-subset evidence without NetCDF dependencies."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    base = args.root / "representative_19d_19790701_19790720"
    validation = (base / "validation" / "VALIDATION.txt").read_text(encoding="utf-8")
    finish = (base / "config" / "finish.status").read_text().strip()
    wrapper = (base / "logs" / "subset_19d_formal.exit").read_text().strip()
    header_2d = (base / "validation" / "netcdf_2d_header.txt").read_text(
        encoding="utf-8", errors="replace"
    )
    header_3d = (base / "validation" / "netcdf_3d_header.txt").read_text(
        encoding="utf-8", errors="replace"
    )
    checks = {
        "scope=19 days": "19 simulated days" in validation,
        "steps=92520": "steps=92520" in validation,
        "mpi=32": "mpi_ranks=32" in validation,
        "finish.status=OK": finish == "OK",
        "final model time": "1979-07-20T00:00:00.000" in validation,
        "2D time=19": bool(re.search(r"\btime\s*=\s*(?:UNLIMITED\s*;\s*//\s*)?\(?(?:19 currently\)|19\b)", header_2d)),
        "3D time=19": bool(re.search(r"\btime\s*=\s*(?:UNLIMITED\s*;\s*//\s*)?\(?(?:19 currently\)|19\b)", header_3d)),
        "wrapper exit recorded": wrapper == "1",
        "wrapper explanation": "optional absent restart" in validation,
    }
    failures = []
    for label, ok in checks.items():
        print(f"{label}: {'OK' if ok else 'FAIL'}")
        if not ok:
            failures.append(label)

    if failures:
        print("FAIL:", "; ".join(failures))
        return 1
    print("PASS: 19-day scope, model finish, NetCDF dimensions, and wrapper warning verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
