#!/bin/bash

# Usage: ./formpack.sh [previous kpi release tag] [new kpi release tag]

# You need to have the kpi source code `git clone`d here
KPI_SOURCE_DIR="$SOURCES_BASE_DIR/kpi"
old_kpi_tag="$1"
new_kpi_tag="$2"

function get_formpack_rev {
   cd "$KPI_SOURCE_DIR" && \
   git show "$1":dependencies/pip/requirements.txt | grep egg=formpack | cut -f 2 -d '@' | cut -f 1 -d '#'
}

old_formpack_rev=$(get_formpack_rev "$old_kpi_tag")
new_formpack_rev=$(get_formpack_rev "$new_kpi_tag")

./release-notes.py formpack "$old_formpack_rev" "$new_formpack_rev"
