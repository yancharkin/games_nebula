#!/bin/bash

OWN_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "${OWN_DIR}/languages"

function compile_mo() {
    LANG="${1}"
    msgfmt --output-file="../src/data/locale/${LANG}/LC_MESSAGES/games_nebula.mo" \
        "../src/data/locale/${LANG}/LC_MESSAGES/games_nebula.po"
}

cd "${OWN_DIR}"
for LANG in "${LANGUAGES[@]}"; do
    if [ -f "../src/data/locale/${LANG}/LC_MESSAGES/games_nebula.po" ]; then
        compile_mo "${LANG}"
    fi
done
