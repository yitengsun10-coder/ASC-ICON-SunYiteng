#!/usr/bin/env python3
"""Fail-fast validator for the ASC26 ICON ape_from_spinup workload."""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys


REQUIRED = {
    "grid": "icon_grid_0013_R02B04_G.nc",
    "ozone": "bc_ozone_ape.nc",
    "greenhouse": "greenhouse_historical_plus.nc",
    "restart_attributes": "ape_from_spinup_restart_atm_19790701T000000Z.nc/attributes.nc",
    "restart_patch": "ape_from_spinup_restart_atm_19790701T000000Z.nc/patch1_0.nc",
}


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=pathlib.Path, help="directory containing normalized input names")
    parser.add_argument("--json", type=pathlib.Path, default=pathlib.Path("input_manifest.json"))
    args = parser.parse_args()
    rows = []
    ok = True
    for role, relative in REQUIRED.items():
        path = args.root / relative
        exists = path.is_file() and path.stat().st_size > 0
        row = {"role": role, "path": str(path), "exists": exists}
        if exists:
            row.update(size_bytes=path.stat().st_size, sha256=sha256(path))
            if shutil.which("ncdump"):
                probe = subprocess.run(
                    ["ncdump", "-k", str(path)], text=True, capture_output=True
                )
                row["netcdf_kind"] = probe.stdout.strip()
                row["ncdump_ok"] = probe.returncode == 0
                exists = exists and probe.returncode == 0
        row["valid"] = exists
        ok &= exists
        rows.append(row)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    for row in rows:
        print(f"{'OK' if row['valid'] else 'MISSING/INVALID':15} {row['role']:20} {row['path']}")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())

