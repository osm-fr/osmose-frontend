#!/bin/bash

sh ./osmose2maproulette.sh 1070 1 overlap \
    "[world] Highway intersecting building" \
    "Objects that can not be overlapped in the same location."

sh ./osmose2maproulette.sh 1110 "" highwaylink \
    "[world] Bad highway link" \
    "Check the consistency of link with the main way, way may also be too long to be a link."

sh ./osmose2maproulette.sh 1120 "" highway-continuity \
    "[world] Broken highway level continuity" \
    "There is a discontinuity in the classification of the tracks. Although the street is narrow the classification must remain the same."

sh ./osmose2maproulette.sh 4080 "" duplicate \
    "[world] Object tagged twice as node, way or relation" \
    "An entity must be present only once, remove one and eventually merge the tags."

sh ./osmose2maproulette.sh 8170 147 soccer \
    "[france] Missing soccer pitch" \
    "Missing a soccer pitch or appropriate tags leisure=pitch and sport=soccer."
