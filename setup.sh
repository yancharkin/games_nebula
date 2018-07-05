#!/bin/bash

PYGOGAPI='https://github.com/yancharkin/pygogapi/archive/master.zip'
GOGLIB_SCRIPTS1='https://github.com/yancharkin/games_nebula_goglib_scripts/archive/master.zip'
GOGLIB_SCRIPTS2='https://bitbucket.org/yancharkin/games_nebula_goglib_scripts/get/master.zip'
GOGLIB_SCRIPTS3='https://gitlab.com/yancharkin/games_nebula_goglib_scripts/-/archive/master/games_nebula_goglib_scripts-master.zip'
MYLIB_SCRIPTS1='https://github.com/yancharkin/games_nebula_mylib_scripts/archive/master.zip'
MYLIB_SCRIPTS2='https://bitbucket.org/yancharkin/games_nebula_mylib_scripts/get/master.zip'
MYLIB_SCRIPTS3='https://gitlab.com/yancharkin/games_nebula_mylib_scripts/-/archive/master/games_nebula_mylib_scripts-master.zip'
GOGLIB_IMAGES1='https://github.com/yancharkin/games_nebula_goglib_images/archive/master.zip'
MYLIB_IMAGES1='https://github.com/yancharkin/games_nebula_mylib_images/archive/master.zip'
INNOEXTRACT='https://github.com/dscharrer/innoextract/releases/download/1.7/innoextract-1.7-linux.tar.xz'

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
    DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
    SOURCE="$(readlink "$SOURCE")"
    [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

source "$DIR/scripts/shell_functions.sh"

ARCH=$(get_arch i)
if [ "$ARCH" != "amd64" ]; then
    ARCH="i686"
fi

# Functions
extract_all () {
    if [ -f "$DIR/tmp/pygogapi.zip" ]; then
        7z x -aoa -o"$DIR/tmp/pygogapi" "$DIR/tmp/pygogapi.zip"
        if [ ! -d "$DIR/gogapi" ]; then
            mv "$DIR/tmp/pygogapi/pygogapi-master/gogapi" "$DIR/"
        else
            cp -r "$DIR/tmp/pygogapi/pygogapi-master/gogapi/"* "$DIR/gogapi/"
        fi
    fi
    if [ -f "$DIR/tmp/goglib_scripts.zip" ]; then
        7z x -aoa -o"$DIR/tmp/goglib_scripts" "$DIR/tmp/goglib_scripts.zip"
        if [ ! -d "$DIR/scripts/goglib" ]; then
            mv "$DIR/tmp/goglib_scripts/"* "$DIR/scripts/goglib"
        else
            cp -r "$DIR/tmp/goglib_scripts/"*/* "$DIR/scripts/goglib/"
        fi
    fi
    if [ -f "$DIR/tmp/mylib_scripts.zip" ]; then
        7z x -aoa -o"$DIR/tmp/mylib_scripts" "$DIR/tmp/mylib_scripts.zip"
        if [ ! -d "$DIR/scripts/mylib" ]; then
            mv "$DIR/tmp/mylib_scripts/"*/free "$DIR/scripts/mylib"
        else
            cp -r "$DIR/tmp/mylib_scripts/"*/free/* "$DIR/scripts/mylib/"
        fi
        cp -r "$DIR/tmp/mylib_scripts/"*/autosetup.ini "$DIR/scripts/mylib/"
    fi
    if [ -f "$DIR/tmp/goglib_images.zip" ]; then
        7z x -aoa -o"$DIR/tmp/goglib_images" "$DIR/tmp/goglib_images.zip"
        if [ ! -d "$DIR/images/goglib" ]; then
            mv "$DIR/tmp/goglib_images/"* "$DIR/images/goglib"
        else
            cp -r "$DIR/tmp/goglib_images/"*/* "$DIR/images/goglib/"
        fi
    fi
    if [ -f "$DIR/tmp/mylib_images.zip" ]; then
        7z x -aoa -o"$DIR/tmp/mylib_images" "$DIR/tmp/mylib_images.zip"
        if [ ! -d "$DIR/images/mylib" ]; then
            mv "$DIR/tmp/mylib_images/"* "$DIR/images/mylib"
        else
            cp -r "$DIR/tmp/mylib_images/"*/* "$DIR/images/mylib/"
        fi
    fi
    if [ -f "$DIR/tmp/innoextract.tar.xz" ]; then
        mkdir -p "$DIR/tmp/innoextract"
        tar xf "$DIR/tmp/innoextract.tar.xz" --strip-components=2 -C "$DIR/tmp/innoextract"
        mkdir -p "$DIR/bin"
        mv "$DIR/tmp/innoextract/$ARCH/innoextract" "$DIR/bin/"
    fi
    rm -r "$DIR/tmp"
}

create_launcher () {
echo '#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
python "$DIR/games_nebula.py"' > "$DIR/start.sh"
chmod +x "$DIR/start.sh"
mkdir -p "$HOME/.local/share/applications"
echo "[Desktop Entry]
Name=Games Nebula
Comment=Application for managing and playing games
Exec=$DIR/start.sh
Icon=$DIR/images/icon.png
Type=Application
Terminal=false
Categories=Game;" > "$HOME/.local/share/applications/games_nebula.desktop"
chmod +x  "$HOME/.local/share/applications/games_nebula.desktop"
}

mkdir -p "$DIR/tmp"

# Download mandatory components
curl -L -o "$DIR/tmp/pygogapi.zip" -C - "$PYGOGAPI" || \
error_message "Failed to download pygogapi"

# Download all optional components:
question_y_n "Download all optional components?" \
"curl -L -o '$DIR/tmp/goglib_scripts.zip' -C - '$GOGLIB_SCRIPTS1' || \
curl -L -o '$DIR/tmp/goglib_scripts.zip' -C - '$GOGLIB_SCRIPTS2' || \
curl -L -o '$DIR/tmp/goglib_scripts.zip' -C - '$GOGLIB_SCRIPTS3' || \
error_message 'Failed to download goglib_scripts' && \
curl -L -o '$DIR/tmp/mylib_scripts.zip' -C - '$MYLIB_SCRIPTS1' || \
curl -L -o '$DIR/tmp/mylib_scripts.zip' -C - '$MYLIB_SCRIPTS2' || \
curl -L -o '$DIR/tmp/mylib_scripts.zip' -C - '$MYLIB_SCRIPTS3' || \
error_message 'Failed to download mylib_scripts' && \
curl -L -o '$DIR/tmp/goglib_images.zip' -C - '$GOGLIB_IMAGES1' || \
error_message 'Failed to download goglib_images' && \
curl -L -o '$DIR/tmp/mylib_images.zip' -C - '$MYLIB_IMAGES1' || \
error_message 'Failed to download mylib_images' && \
curl -L -o '$DIR/tmp/innoextract.tar.xz' -C - '$INNOEXTRACT' && \
extract_all || error_message 'Failed to extract files' && \
create_launcher && \
echo 'Done' && \
exit 0" \
:

# Or download selected components:
question_y_n "Download goglib_scripts?" \
"curl -L -o '$DIR/tmp/goglib_scripts.zip' -C - '$GOGLIB_SCRIPTS1' || \
curl -L -o '$DIR/tmp/goglib_scripts.zip' -C - '$GOGLIB_SCRIPTS2' || \
curl -L -o '$DIR/tmp/goglib_scripts.zip' -C - '$GOGLIB_SCRIPTS3' || \
error_message 'Failed to download goglib_scripts'" \
:
question_y_n "Download mylib_scripts?" \
"curl -L -o '$DIR/tmp/mylib_scripts.zip' -C - '$MYLIB_SCRIPTS1' || \
curl -L -o '$DIR/tmp/mylib_scripts.zip' -C - '$MYLIB_SCRIPTS2' || \
curl -L -o '$DIR/tmp/mylib_scripts.zip' -C - '$MYLIB_SCRIPTS3' || \
error_message 'Failed to download mylib_scripts'" \
:
question_y_n "Download goglib_images?" \
"curl -L -o '$DIR/tmp/goglib_images.zip' -C - '$GOGLIB_IMAGES1' || \
error_message 'Failed to download goglib_images'" \
:
question_y_n "Download mylib_images?" \
"curl -L -o '$DIR/tmp/mylib_images.zip' -C - '$MYLIB_IMAGES1' || \
error_message 'Failed to download mylib_images'" \
:
question_y_n "Download innoextract?" \
"curl -L -o '$DIR/tmp/innoextract.tar.xz' -C - '$INNOEXTRACT'" \
:
extract_all || error_message "Failed to extract files" && \
create_launcher && \
echo "Done"
