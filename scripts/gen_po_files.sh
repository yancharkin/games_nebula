#!/bin/bash

source ./languages

function gen_pot() {
    xgettext --language="Python" --keyword="_tr" --output="./games_nebula.pot" \
    "../src/games_nebula/client/api_wrapper.py" \
    "../src/games_nebula/client/commands.py" \
    "../src/games_nebula/client/config.py" \
    "../src/games_nebula/client/downloader.py" \
    "../src/games_nebula/client/installer.py" \
    "../src/games_nebula/client/launcher.py" \
    "../src/games_nebula/client/logger.py" \
    "../src/games_nebula/client/uninstaller.py" \
    "../src/games_nebula/client/cli/argparse_tr_hack.py" \
    "../src/games_nebula/client/cli/header.py" \
    "../src/games_nebula/client/cli/help.py" \
    "../src/games_nebula/client/cli/interactive.py" \
    "../src/games_nebula/client/cli/noninteractive.py" \
    "../src/games_nebula/client/cli/pager.py" \
    "../src/games_nebula/client/cli/valid_commands.py" \
    "../src/games_nebula/client/gui/gamewidget.py" \
    "../src/games_nebula/client/gui/gui.py" \
    "../src/games_nebula/client/gui/login.py" \
    "../src/games_nebula/client/gui/main_window.py" \
    "../src/games_nebula/client/gui/setup_window.py" \
    "../src/games_nebula/client/gui/sort_filter_proxy_model.py" \
    "../src/games_nebula/client/gui/systray.py" \
    "../src/games_nebula/client/utils/convert_from_bytes.py" \
    "../src/games_nebula/client/utils/downloader.py" \
    "../src/games_nebula/client/utils/reinput.py" \
    "../src/games_nebula/client/utils/unzipper.py"
}

function gen_po() {
    LANG="${1}"
    mkdir -p "../src/data/locale/${LANG}/LC_MESSAGES"
    if [ ! -f "../src/data/locale/${LANG}/LC_MESSAGES/games_nebula.po" ]; then
        msginit --locale="${LANG}" --input="./games_nebula.pot" \
            --output="../src/data/locale/${LANG}/LC_MESSAGES/games_nebula.po"
    else
        msgmerge --update "../src/data/locale/${LANG}/LC_MESSAGES/games_nebula.po" "./games_nebula.pot"
    fi
}

gen_pot
for LANG in "${LANGUAGES[@]}"; do
    gen_po "${LANG}"
done
rm "./games_nebula.pot"
