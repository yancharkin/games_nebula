#!/bin/bash

xgettext --language=Python --keyword=_ --output=./games_nebula.pot \
../*.py \
../../games_nebula_goglib_scripts/*/*.py \
#~ ../../games_nebula_mylib_scripts/*/*.py
