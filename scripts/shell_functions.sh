### Colors #####################################################################
COLOR_RESET='\033[0m'
COLOR_BLACK='\033[0;30m'
COLOR_RED='\033[0;31m'
COLOR_GREEN='\033[0;32m'
COLOR_ORANGE='\033[0;33m'
COLOR_BLUE='\033[0;34m'
COLOR_PURPLE='\033[0;35m'
COLOR_CYAN='\033[0;36m'
COLOR_CYAN='\033[0;36m'
COLOR_LIGHT_GRAY='\033[0;37m'
COLOR_DARK_GRAY='\033[1;30m'
COLOR_LIGHT_RED='\033[1;31m'
COLOR_LIGHT_GREEN='\033[1;32m'
COLOR_YELLOW='\033[1;33m'
COLOR_LIGHT_BLUE='\033[1;34m'
COLOR_LIGHT_PURPLE='\033[1;35m'
COLOR_LIGHT_CYAN='\033[1;36m'
COLOR_WHITE='\033[1;37m'

### Common #####################################################################
question_y_n () {

QUESTION="$1"
COMMAND1="$2"
COMMAND2="$3" # ":" can be used to pass "true" (empty command)

echo -ne "${COLOR_LIGHT_CYAN}\n$QUESTION [y/n]${COLOR_RESET} > "
read -n 1 ANSWER
echo -ne "\n"

if [ "$ANSWER" == "y" ] || [ "$ANSWER" == "Y" ] || [ "$ANSWER" == "n" ] || [ "$ANSWER" == "N" ]; then
    INCORRECT_ANSWER=0
    if [ "$ANSWER" == "y" ] || [ "$ANSWER" == "Y" ]; then
        echo -ne "\n"
        ANSWER="y"
    else
        ANSWER="n"
    fi
else
    INCORRECT_ANSWER=1
fi

while  [ "$INCORRECT_ANSWER" == 1 ]; do

    echo "Incorrect answer"

    echo "$QUESTION [y/n]"
    read -n 1 ANSWER

    if [ "$ANSWER" == "y" ] || [ "$ANSWER" == "Y" ] || [ "$ANSWER" == "n" ] || [ "$ANSWER" == "N" ]; then
        INCORRECT_ANSWER=0
        if [ "$ANSWER" == "y" ] || [ "$ANSWER" == "Y" ]; then
            ANSWER="y"
        else
            ANSWER="n"
        fi
    else
        INCORRECT_ANSWER=1
    fi

done

if [ "$ANSWER" == "y" ]; then
    eval "$COMMAND1"
else
    eval "$COMMAND2"
fi

}

error_message () {
    MESSAGE="$1"
    echo -ne "${COLOR_LIGHT_RED}\n$MESSAGE${COLOR_RESET}\n"
    exit 1
}

proc_timer () {
pid="$1"
msg="$2"
i=0
while [ -e "/proc/$pid" ]; do
sleep 0.1
i=$[$i + 1]
sec=$[$i / 10]
echo -ne "\r$msg - $sec""s"
done
echo -ne "${COLOR_LIGHT_GREEN}\r\nDone!${COLOR_RESET}\n"
}

get_arch () {
FORMAT="$1"
if [ $(uname -m) == "x86_64" ]; then
if [ "$FORMAT" == "x" ]; then
ARCH="x86_64"
fi
if [ "$FORMAT" == "i" ]; then
ARCH="amd64"
fi
else
if [ "$FORMAT" == "x" ]; then
ARCH="x86"
fi
if [ "$FORMAT" == "i" ]; then
ARCH="i386"
fi
fi
echo "$ARCH"
}

### Download and move ##########################################################
get_common_file () {
FILE_NAME="$1"
LINK="$2"
if [ ! -f "$DOWNLOAD_DIR/_distr/$FILE_NAME" ]; then
mkdir -p "$DOWNLOAD_DIR/_distr/"
curl -L -o "$DOWNLOAD_DIR/_distr/$FILE_NAME" -C - "$LINK" \
& proc_timer $! "Downloading $FILE_NAME"
fi
}

get_file () {
FILE_NAME="$1"
LINK="$2"
if [ ! -f "$DOWNLOAD_DIR/_distr/$GAME_NAME/$FILE_NAME" ]; then
mkdir -p "$DOWNLOAD_DIR/_distr/$GAME_NAME"
curl -L -o "$DOWNLOAD_DIR/_distr/$GAME_NAME/$FILE_NAME" -C - "$LINK" \
& proc_timer $! "Downloading $FILE_NAME"
fi
}

get_mylib_distr () {
FILE_NAME="$1"
LINK="$2"
if [ ! -f "$DOWNLOAD_DIR/$GAME_NAME/$FILE_NAME" ]; then
mkdir -p "$DOWNLOAD_DIR/$GAME_NAME"
curl -L -o "$DOWNLOAD_DIR/$GAME_NAME/$FILE_NAME" -C - "$LINK" \
& proc_timer $! "Downloading $FILE_NAME"
fi
}

get_java_i586 () {
# Download page: https://www.java.com/en/download/manual.jsp
LINK='http://javadl.oracle.com/webapps/download/AutoDL?BundleId=220303_d54c1d3a095b4ff2b6607d096fa80163'
FILE_NAME="java_i586.tar.gz"
get_common_file "$FILE_NAME" "$LINK"
tar -xzvf "$DOWNLOAD_DIR/_distr/$FILE_NAME" -C "$INSTALL_DIR/$GAME_NAME"
mv "$INSTALL_DIR/$GAME_NAME/jre"* "$INSTALL_DIR/$GAME_NAME/jre"
}

get_java_x64 () {
LINK='http://javadl.oracle.com/webapps/download/AutoDL?BundleId=220305_d54c1d3a095b4ff2b6607d096fa80163'
FILE_NAME="java_x64.tar.gz"
get_common_file "$FILE_NAME" "$LINK"
tar -xzvf "$DOWNLOAD_DIR/_distr/$FILE_NAME" -C "$INSTALL_DIR/$GAME_NAME"
mv "$INSTALL_DIR/$GAME_NAME/jre"* "$INSTALL_DIR/$GAME_NAME/jre"
}

get_from_mega () {
FILE_NAME="$1"
LINK="$2"
if [ ! -f "$DOWNLOAD_DIR/_distr/$GAME_NAME/$FILE_NAME" ]; then
mkdir -p "$DOWNLOAD_DIR/_distr/$GAME_NAME/"
megadl "$LINK" --path "$DOWNLOAD_DIR/_distr/$GAME_NAME/"
fi
}

get_weidu () {
FILE_NAME="WeiDU-Linux-240.zip"
LINK='http://www.weidu.org/%7Ethebigg/WeiDU-Linux-240.zip'
get_common_file "$FILE_NAME" "$LINK"
ARCH=$(get_arch i)
7z e -aoa -o"$INSTALL_DIR/$GAME_NAME/game" \
"$DOWNLOAD_DIR/_distr/$FILE_NAME" \
"WeiDU-Linux/bin/$ARCH/weidu" \
"WeiDU-Linux/bin/$ARCH/tolower" \
& proc_timer $! "Extracting $FILE_NAME"
}

get_upx () {
ARCH=$(get_arch i)
FILE_NAME="upx-$ARCH_linux.tar.xz"
LINK='https://github.com/upx/upx/releases/download/v3.94/upx-3.94-'"$ARCH"'_linux.tar.xz'
get_common_file "$FILE_NAME" "$LINK"
tar xvfJ "$DOWNLOAD_DIR/_distr/$FILE_NAME" --strip-components=1 -C \
"$INSTALL_DIR/$GAME_NAME/game/"
}

setup_lavfilters () {
LINK='https://github.com/Nevcairiel/LAVFilters/releases/download/0.69/LAVFilters-0.69-x86.zip'
get_common_file 'LAVFilters-0.69-x86.zip' "$LINK"
echo -e 'mkdir -p "$WINEPREFIX/drive_c/Program Files/LAVFilters"
7z x -aoa -o"$WINEPREFIX/drive_c/Program Files/LAVFilters" \
"$DOWNLOAD_DIR/_distr/LAVFilters-0.69-x86.zip"
cd "$WINEPREFIX/drive_c/Program Files/LAVFilters"
"$WINELOADER" regsvr32.exe LAVSplitter.ax
"$WINELOADER" regsvr32.exe LAVVideo.ax
"$WINELOADER" regsvr32.exe LAVAudio.ax' >> \
"$ADDITIONS_FILE" && chmod +x "$ADDITIONS_FILE"
}

### Other ######################################################################
heroes_chronicles_create_links () {
cd "$INSTALL_DIR/$GAME_NAME/game/"
mv 'Data' "$INSTALL_DIR/heroes_chronicles_common_data/"
mv 'MP3' "$INSTALL_DIR/heroes_chronicles_common_data/"
ln -s "$INSTALL_DIR/heroes_chronicles_common_data/Data" 'Data'
ln -s "$INSTALL_DIR/heroes_chronicles_common_data/MP3" 'MP3'
}

heroes_chronicles_update_links () {
cd "$INSTALL_DIR/$GAME_NAME/game/"
rm -R -f 'Data'
rm -R -f 'MP3'
ln -s "$INSTALL_DIR/heroes_chronicles_common_data/Data" 'Data'
ln -s "$INSTALL_DIR/heroes_chronicles_common_data/MP3" 'MP3'
}

heroes_chronicles_counter () {
TYPE="$1"
if [ "$TYPE" == "add" ]; then
mkdir -p "$INSTALL_DIR/heroes_chronicles_common_data"
COUNT_FILE="$INSTALL_DIR/heroes_chronicles_common_data/count_file"
COUNT=0
INSTALLED_GAMES=$(ls $INSTALL_DIR)
readarray -t INSTALLED_GAMES_ARRAY <<<"$INSTALLED_GAMES"
IFS=$'\n';
for i in ${INSTALLED_GAMES_ARRAY[@]}; do
if [[ "$i" == heroes_chronicles_chapter* ]]
then COUNT=$(($COUNT + 1))
fi
done
echo $COUNT > "$COUNT_FILE"
cd "$INSTALL_DIR/$GAME_NAME/game"
if (($COUNT == 1)); then
heroes_chronicles_create_links
else
heroes_chronicles_update_links
fi
fi
if [ "$TYPE" == "remove" ]; then
COUNT_FILE="$INSTALL_DIR/heroes_chronicles_common_data/count_file"
COUNT=$(cat "$COUNT_FILE")
COUNT=$(($COUNT - 1))
if (($COUNT == 0)); then
rm -R -f "$INSTALL_DIR/heroes_chronicles_common_data"
else
echo $COUNT > "$COUNT_FILE"
fi
fi
}

get_exult () {
FILE_NAME="exult_git_dee7d24.7z"
LINK="https://mega.nz/#!TgIzRR6R!NCxRYaXk0ee7jBjjFoXVr56DDGz8jnjyYcfSEwMAdjw"
if [ ! -f "$DOWNLOAD_DIR/_distr/ultima_7/$FILE_NAME" ]; then
mkdir -p "$DOWNLOAD_DIR/_distr/ultima_7"
megadl "$LINK" --path "$DOWNLOAD_DIR/_distr/ultima_7/" \
& proc_timer $! "Downloading $FILE_NAME"
fi
mkdir -p "$INSTALL_DIR/exult/data"
mkdir -p "$INSTALL_DIR/exult/saves"
if [ ! -d "$INSTALL_DIR/exult/bin" ]; then
7z x -aoa -o"$INSTALL_DIR/exult" "$DOWNLOAD_DIR/_distr/ultima_7/$FILE_NAME"
fi
}

get_exult_audio () {
FILE_NAME="exult_audio.zip"
LINK="http://prdownloads.sourceforge.net/exult/exult_audio.zip"
if [ ! -f "$DOWNLOAD_DIR/_distr/ultima_7/$FILE_NAME" ]; then
mkdir -p "$DOWNLOAD_DIR/_distr/ultima_7"
curl -L -o "$DOWNLOAD_DIR/_distr/ultima_7/$FILE_NAME" -C - "$LINK" \
& proc_timer $! "Downloading $FILE_NAME"
fi
7z x -aoa -o"$INSTALL_DIR/exult/share/exult" "$DOWNLOAD_DIR/_distr/ultima_7/exult_audio.zip"
}

write_exult_cfg () {
if [ ! -f "$INSTALL_DIR/exult/exult.cfg" ]; then
echo -e "<config>
 <disk>
  <data_path>
  $INSTALL_DIR/exult/share/exult
  </data_path>
  <game>
   <blackgate>
    <path>
    $INSTALL_DIR/exult/data/blackgate
    </path>
    <static_path>
    $INSTALL_DIR/exult/data/blackgate/static
    </static_path>
    <savegame_path>
    $INSTALL_DIR/exult/saves/blackgate
    </savegame_path>
    <gamedat_path>
    $INSTALL_DIR/exult/saves/blackgate
    </gamedat_path>
   </blackgate>
   <forgeofvirtue>
    <path>
    $INSTALL_DIR/exult/data/forgeofvirtue
    </path>
    <static_path>
    $INSTALL_DIR/exult/data/forgeofvirtue/static
    </static_path>
    <savegame_path>
    $INSTALL_DIR/exult/saves/forgeofvirtue
    </savegame_path>
    <gamedat_path>
    $INSTALL_DIR/exult/saves/forgeofvirtue
    </gamedat_path>
   </forgeofvirtue>
   <serpentisle>
    <path>
    $INSTALL_DIR/exult/data/serpentisle
    </path>
    <static_path>
    $INSTALL_DIR/exult/data/serpentisle/static
    </static_path>
    <savegame_path>
    $INSTALL_DIR/exult/saves/serpentisle
    </savegame_path>
    <gamedat_path>
    $INSTALL_DIR/exult/saves/serpentisle
    </gamedat_path>
   </serpentisle>
   <silverseed>
    <path>
    $INSTALL_DIR/exult/data/silverseed
    </path>
    <static_path>
    $INSTALL_DIR/exult/data/silverseed/static
    </static_path>
    <savegame_path>
    $INSTALL_DIR/exult/saves/silverseed
    </savegame_path>
    <gamedat_path>
    $INSTALL_DIR/exult/saves/silverseed
    </gamedat_path>
   </silverseed>
   <serpentbeta>
    <path>
    $INSTALL_DIR/exult/data/serpentbeta
    </path>
    <static_path>
    $INSTALL_DIR/exult/data/serpentbeta/static
    </static_path>
    <savegame_path>
    $INSTALL_DIR/exult/saves/serpentbeta
    </savegame_path>
    <gamedat_path>
    $INSTALL_DIR/exult/saves/serpentbeta
    </gamedat_path>
   </serpentbeta>
   </game>
 </disk>
</config>" > "$INSTALL_DIR/exult/exult.cfg"
fi
}
