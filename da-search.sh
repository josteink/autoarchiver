#!/bin/sh

ROOT=$HOME/DocumentArchive
find $ROOT -iname *${*}*
find $ROOT -name '*.txt' -exec grep -Hi "$*" '{}' \;
