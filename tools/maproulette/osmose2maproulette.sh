#!/bin/bash

DATABASE="osmose_frontend"
USER=""
HOST=""
PASSWORD=""

ITEM=$1
CLASS=$2
NICK=$3

CHALLENGE_TITLE="$4"
CHALLENGE_INSTRUCTION="$5 http://wiki.openstreetmap.org/wiki/Osmose/errors#$ITEM"

if [ "$CLASS" = "" ]; then
SLUG="osmose-$ITEM-$NICK"
QUERY="SELECT lat, lon, elems AS osmoseid FROM marker WHERE item=$ITEM"
else
SLUG="osmose-$ITEM-$CLASS-$NICK"
QUERY="SELECT lat, lon, elems AS osmoseid FROM marker WHERE item=$ITEM AND class=$CLASS"
fi

#ssh -L 5000:localhost:80 challenges@maproulette.org
SERVER="http://localhost:5000/"
#SERVER="http://maproulette.org/"

#ssh -L 5000:localhost:80 maproulette@dev.maproulette.org
#SERVER="http://dev.maproulette.org/"


echo "==$SLUG=="
./process.py \
    -v \
    --title "$CHALLENGE_TITLE" \
    --server "$SERVER" \
    --instruction "$CHALLENGE_INSTRUCTION" \
    "$SLUG" use-db \
    "$QUERY" \
    --database "$DATABASE" \
    --user "$USER" \
    --password "$PASSWORD" \
    --host "$HOST" \
