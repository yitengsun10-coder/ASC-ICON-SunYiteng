#!/usr/bin/env bash
set -euo pipefail

# Reproducible CPU build helper for ASC26 ICON on Ubuntu 22.04.
# Usage: ./install.sh [source_dir] [build_dir]
SOURCE_DIR=${1:-"$PWD/ASC26-icon/icon-model"}
BUILD_DIR=${2:-"$PWD/build-icon-gcc"}
JOBS=${JOBS:-$(nproc)}

sudo apt-get update
sudo apt-get install -y \
  autoconf automake libtool make gcc-11 g++-11 gfortran-11 \
  openmpi-bin libopenmpi-dev libnetcdf-dev libnetcdff-dev \
  libhdf5-dev libeccodes-dev libfyaml-dev libxml2-dev \
  libblas-dev liblapack-dev ruby git git-lfs pkg-config

git lfs install
git -C "$(dirname "$SOURCE_DIR")" lfs pull
git -C "$(dirname "$SOURCE_DIR")" submodule update --init --recursive

# ASC snapshot contains CDI source but may not contain generated autotools files.
CDI_DIR="$SOURCE_DIR/externals/cdi"
if [[ -d "$CDI_DIR" && ! -x "$CDI_DIR/configure" ]]; then
  (cd "$CDI_DIR" && ./autogen.sh)
fi
if [[ -f "$CDI_DIR/config.guess" && ! -s "$CDI_DIR/config.guess" ]]; then
  cp /usr/share/automake-1.16/config.guess "$CDI_DIR/config.guess"
  chmod +x "$CDI_DIR/config.guess"
fi

mkdir -p "$BUILD_DIR/externals/cdi/src"
if [[ ! -s "$BUILD_DIR/externals/cdi/src/mo_cdi.f90" ]]; then
  ruby "$CDI_DIR/interfaces/f2003/bindGen.rb" \
    "$CDI_DIR/src/cdi.h" "$BUILD_DIR/externals/cdi/src/mo_cdi.f90"
fi

cd "$BUILD_DIR"
CC=gcc-11 CXX=g++-11 FC=gfortran-11 \
  "$SOURCE_DIR/configure" \
  --disable-ocean --disable-jsbach --disable-coupling \
  --disable-art --disable-rttov --disable-emvorado --disable-dace

/usr/bin/time -v make -j"$JOBS" 2>&1 | tee build.log
test -x "$BUILD_DIR/bin/icon"
sha256sum "$BUILD_DIR/bin/icon" | tee icon.sha256

