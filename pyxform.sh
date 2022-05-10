#!/bin/bash

# Usage: ./pyxform.sh [previous kpi release tag] [new kpi release tag]

# You need to have the kpi source code `git clone`d here
KPI_SOURCE_DIR="$SOURCES_BASE_DIR/kpi"
old_kpi_tag="$1"
new_kpi_tag="$2"

function get_pyxform_version {
   cd "$KPI_SOURCE_DIR" && \
   git show "$1":dependencies/pip/requirements.txt | grep 'pyxform==' | cut -f 3 -d '='
}

old_pyxform_version=$(get_pyxform_version "$old_kpi_tag")
new_pyxform_version=$(get_pyxform_version "$new_kpi_tag")

if [ "$old_pyxform_version" != "$new_pyxform_version" ]
then
    echo "This release contains Pyxform version $new_pyxform_version, upgraded from version $old_pyxform_version."
    echo "For a list of changes, please refer to the [Pyxform change log](https://github.com/XLSForm/pyxform/blob/master/CHANGES.txt)."
else
    echo "This release contains Pyxform version $new_pyxform_version."
fi
