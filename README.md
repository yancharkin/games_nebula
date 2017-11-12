# Games Nebula
Unofficial Linux client for GOG.

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
There is no "proper" packages for the application (and not planned at the moment). But it's not that hard to install.
### 1. Install dependencies
#### Mandatory dependencies

**Debian/Ubuntu:**

    sudo apt install python-gi python-bs4 python-lxml python-pil lgogdownloader innoextract
    
**Arch**

    sudo pacman -S python2-gobject python2-beautifulsoup4 python2-lxml python2-pillow

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

## Shortcuts
**Ctrl + F** - Toggle fullscreen
**Shift + T** - Toggle tabs visibility
**Ctrl + T** - Add tab
**Ctrl + W** - Close tab
**Ctrl + Tab** - Next tab
**Shift + Tab** - Previous tab
**Ctrl + S** - Search
**Ctrl + Q** - Quit
**RMB on filter** - invert filter type
**MMB on filter** - reset filter

## Roadmap
While poorly coded, 'Games Nebula' has all features that I intended to include in it, so no new features planned.

**Things need to be done:**
- fix bugs
- organize code
- improve code quality
- port to python3
- write replacement for lgogdownloader
- create proper packages

But for various reasons in the foreseeable future I'm not going to do more than fixing bugs.