#!/bin/bash

# Usage: ./all.sh [previous kpi/kobocat release tag] [new kpi/kobocat release tag]

echo '## pyxform'
./pyxform.sh "$1" "$2"

echo
echo '## kpi'
./release-notes.py kpi "$1" "$2"

echo
echo '## kobocat'
./release-notes.py kobocat "$1" "$2"

echo
echo '## formpack'
./formpack.sh "$1" "$2"
