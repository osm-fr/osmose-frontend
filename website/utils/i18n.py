#! /bin/bash

echo "Content-Type: text/html; charset=utf-8"
echo ""

cd $OSMOSE_ROOT/po

make statistics | sed -n '1h;2,$H;${g;s/\n/<br>/g;p}'
