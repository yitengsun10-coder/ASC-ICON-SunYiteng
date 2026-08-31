#!/usr/bin/env bash
set -euo pipefail

# Batch runner. It never starts a paid run unless input validation succeeds.
# INPUT_ROOT must expose the normalized names documented in validate_inputs.py.
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
SOURCE_ROOT=${SOURCE_ROOT:-"$PWD/ASC26-icon"}
BUILD_DIR=${BUILD_DIR:-"$PWD/build-icon-gcc"}
INPUT_ROOT=${INPUT_ROOT:-"$SOURCE_ROOT/testcase/normalized_inputs"}
RESULT_ROOT=${RESULT_ROOT:-"$PWD/results"}
MPI_LIST=${MPI_LIST:-"1 2 4 8 16"}

mkdir -p "$RESULT_ROOT"
python3 "$SCRIPT_DIR/validate_inputs.py" "$INPUT_ROOT" \
  --json "$RESULT_ROOT/input_manifest.json"
test -x "$BUILD_DIR/bin/icon"

printf 'name\tmpi_ranks\twall_seconds\tstatus\tlog\n' > "$RESULT_ROOT/runs.tsv"
for ranks in $MPI_LIST; do
  name="mpi_${ranks}"
  run_dir="$RESULT_ROOT/$name"
  mkdir -p "$run_dir"
  start_ns=$(date +%s%N)
  status=success
  (
    cd "$run_dir"
    export ICON_EXEC="$BUILD_DIR/bin/icon"
    export no_of_nodes=1
    export mpi_procs_pernode="$ranks"
    export OMP_NUM_THREADS=1
    export OMPI_MCA_rmaps_base_mapping_policy=slot
    export OMPI_MCA_hwloc_base_binding_policy=core
    bash "$SOURCE_ROOT/testcase/ape_from_spinup.run"
  ) >"$run_dir/output.log" 2>&1 || status=failed
  end_ns=$(date +%s%N)
  wall=$(awk -v s="$start_ns" -v e="$end_ns" 'BEGIN {printf "%.6f",(e-s)/1e9}')
  printf '%s\t%s\t%s\t%s\t%s\n' \
    "$name" "$ranks" "$wall" "$status" "$run_dir/output.log" >> "$RESULT_ROOT/runs.tsv"
done

python3 "$SCRIPT_DIR/parse_results.py" "$RESULT_ROOT/runs.tsv" \
  --output "$RESULT_ROOT/summary.json"

