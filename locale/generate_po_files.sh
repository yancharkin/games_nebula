#!/bin/bash

xgettext --language=Python --keyword=_ --output=./games_nebula.pot \
../*.py \
../../games_nebula_goglib_scripts/*/*.py \
../../games_nebula_mylib_scripts/free/*/*.py \
../../games_nebula_mylib_scripts/steam/*/*.py \
#~ ../../games_nebula_mylib_scripts/humblebundle/*/*.py

gen_po () {

    LANG="$1"

    mkdir -p ./$LANG/LC_MESSAGES

    if [ ! -f ./$LANG/LC_MESSAGES/games_nebula.po ]; then
        msginit --locale=$LANG --input=./games_nebula.pot \
        --output=./$LANG/LC_MESSAGES/games_nebula.po
    else
        msgmerge --update ./$LANG/LC_MESSAGES/games_nebula.po \
        ./games_nebula.pot
    fi

    # Generate .mo files
    #~ msgfmt --output-file=./$LANG/LC_MESSAGES/games_nebula.po \
    #~ ./$LANG/LC_MESSAGES/games_nebula.po

}

gen_po "en"
gen_po "ru"

rm ./games_nebula.pot
