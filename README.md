##Games Nebula - Unofficial Linux client for GOG
Do not expect a full-featured client like GOG Galaxy, it's not. But it's works (most of the times) and can be useful.

###Supported distros
Debian 9  
Ubuntu 16.04

Anything else may or may not work.

###How to install
#### Install dependencies

Debian/Ubuntu:

    sudo apt-get install python-gi python-webkit gir1.2-webkit-3.0 python-bs4 python-pil lgogdownloader innoextract p7zip-full cabextract unshield ffmpeg wine winetricks dosbox scummvm zenity

If you know what you're doing you can skip: 

    innoextract p7zip-full cabextract unshield ffmpeg wine winetricks dosbox scummvm zenity

####Download and extract tarball

Download the [latest release](https://github.com/yancharkin/games_nebula/releases) and extract it anywhere you like (For example: $HOME/Applications/games_nebula).

####Run setup.sh (optional)

It will create shortcut in main menu.

###How to use
####Configure lgogdownloader

[lgogdownloader](https://github.com/Sude-/lgogdownloader) is used for listing and downloading games. You can't use Games Nebula without configuring it first.

####Launch application
You can do it by executing start.sh, games_nebula.py or shortcut in main menu.

**Note:** If you have a lot of games in your library and/or slow CPU first launch can take some time.

###Limitations
For **every** game you need installation script. I've added quite a few, but for most games there is no scripts.  
[Scripts repository](https://github.com/yancharkin/games_nebula_goglib_scripts)
