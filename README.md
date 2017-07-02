# Games Nebula
Unofficial Linux client for GOG.

#### Important notes
- In terms of quality it's a prototype software at best
- I'm not a programmer so code quality probably even worse than I think
- Chances that I will re-write it properly are extremely low
- But it works (most of the time) and has some cool and useful features

## Features
- Listing, downloading and installing games from your gog library
- Possibility to create you own (non-gog) library by writing simple scripts
- Integration with wine, dosbox and scummvm to make running non-native games as easy as possible
- Utilities for configurating wine, dosbox and scummvm
- Utilities and patches for some games
- Advanced tagging

...and some other stuff.

## Screenshots
**Main window**

![main window screenshot](https://raw.githubusercontent.com/yancharkin/games_nebula/master/images/screenshots/main_window.jpg  "Main window")

**DOSBox Configuration Utility**

![dosbox utility screenshot](https://raw.githubusercontent.com/yancharkin/games_nebula/master/images/screenshots/dosbox_utility.jpg  "DOSBox Configuration Utility")

**Wine, DOSBox and ScummVM launchers**

![launchers screenshot](https://raw.githubusercontent.com/yancharkin/games_nebula/master/images/screenshots/launchers.png  "Launchers")

**Configuration utilities for 'Arcanum: Of Steamworks and Magick Obscura' and 'Planescape: Torment'**

![conf_utilities](https://raw.githubusercontent.com/yancharkin/games_nebula/master/images/screenshots/conf_utilities.png  "Configuration Utilities")

## Installation
For the reasons stated above there is no "proper" packages for the application (and not planned at the moment). But it's not that hard to install.
### 1. Install dependencies
#### Mandatory dependencies

**Debian/Ubuntu:**

    sudo apt install python-gi python-bs4 python-lxml python-pil lgogdownloader innoextract
    
**Arch**

    sudo pacman -S python-gobject python2-beautifulsoup4 python2-lxml python2-pillow

*AUR: [htmlcxx](https://aur.archlinux.org/packages/htmlcxx/), [lgogdownloader](https://aur.archlinux.org/packages/lgogdownloader/), [innoextract](https://aur.archlinux.org/packages/innoextract/)*

**Fedora**

    sudo dnf install python python-gobject python2-pillow python-beautifulsoup4 innoextract

*You have to compile [lgogdownloader](https://github.com/Sude-/lgogdownloader) yourself*

#### Optional (but highly recommended) dependencies

**Debian/Ubuntu:**

    sudo apt install gksu xterm curl tar p7zip-full cabextract unshield ffmpeg megatools wine winetricks dosbox scummvm

**Arch**

    sudo pacman -S gksu xterm curl tar p7zip cabextract unshield ffmpeg wine winetricks dosbox scummvm
    
*AUR: [megatools](https://aur.archlinux.org/packages/megatools/)*
    
**Fedora**

    sudo dnf install xterm curl tar p7zip p7zip-plugins cabextract unshield megatools wine winetricks dosbox scummvm

*[RPM Fusion](https://rpmfusion.org/): ffmpeg*
### 2. Install application
- Download the [latest release](https://github.com/yancharkin/games_nebula/releases) and extract it anywhere you like.
- Run **setup.sh**. It will create shortcut in main menu.
- It's recommended to configure lgogdownloader before launching 'Game Nebula'. And for versions < 3.2 it's a mandatory.

## Also...
- If you have a lot of games in your library and/or slow CPU, first launch can take some time
- [Scripts repository for gog games](https://github.com/yancharkin/games_nebula_goglib_scripts)
- [Scripts repository for non-gog games](https://github.com/yancharkin/games_nebula_mylib_scripts)
- [If anyone wants to make a donation](https://www.paypal.me/yancharkin)
