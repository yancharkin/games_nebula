##Games Nebula - Unofficial Linux client for GOG
**Warning!** It's not a full-featured client like GOG Galaxy, it's a poorly coded prototype with limited functionality. But it works (most of the times).

###How to install
#### Install dependencies

Debian/Ubuntu:

    sudo apt-get install python-gi python-webkit gir1.2-webkit-3.0 python-bs4 python-pil lgogdownloader innoextract p7zip-full cabextract unshield ffmpeg wine winetricks dosbox scummvm 

**Note.** If you know what you're doing you can skip: 

    innoextract p7zip-full cabextract unshield ffmpeg wine winetricks dosbox scummvm

####Download and extract tarball

Download the [latest release](https://github.com/yancharkin/games_nebula/releases) and extract it anywhere you like (For example: $HOME/Applications/games_nebula).

####Run setup.sh (optional)

It will create launcher in main menu.

###How to use
####Configure [lgogdownloader](https://github.com/Sude-/lgogdownloader)

lgogdownloader is used for listing and downloading games

####Launch application
You can do it by executing start.sh

**Note:** If you have a lot of games in your library and/or slow CPU first launch can take a lot of time.

###Limitations
For **every** game you need installation script. I've added quite a few, but for most games there is no scripts.