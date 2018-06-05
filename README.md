# Games Nebula
Unofficial Linux client for GOG.

- **[Features](#features)**  
- **[Screenshots](#screenshots)**  
- **[Installation](#installation)**  
   * [Debian/Ubuntu](#debianubuntu)  
   * [Archlinux](#archlinux)  
   * [Fedora](#fedora)  
- **[Shortcuts](#shortcuts)**  
- **[Roadmap](#roadmap)**  
- **[Links](#links)**  


## Features
- Listing, downloading and installing games from your gog library
- Possibility to create you own (non-gog) library by writing simple scripts
- Integration with wine, dosbox and scummvm to make running non-native games as easy as possible
- Utilities for configurating wine, dosbox and scummvm
- Utilities and patches for some games
- Advanced tagging

...and some other stuff.

## Screenshots
<details>
<summary>Click to show/hide screenshots</summary>
<p>

**Main window**

![main window screenshot](https://raw.githubusercontent.com/yancharkin/games_nebula/master/images/screenshots/main_window.jpg  "Main window")

**DOSBox Configuration Utility**

![dosbox utility screenshot](https://raw.githubusercontent.com/yancharkin/games_nebula/master/images/screenshots/dosbox_utility.jpg  "DOSBox Configuration Utility")

**Wine, DOSBox and ScummVM launchers**

![launchers screenshot](https://raw.githubusercontent.com/yancharkin/games_nebula/master/images/screenshots/launchers.png  "Launchers")

**Configuration utilities for 'Arcanum: Of Steamworks and Magick Obscura' and 'Planescape: Torment'**

![conf_utilities](https://raw.githubusercontent.com/yancharkin/games_nebula/master/images/screenshots/conf_utilities.png  "Configuration Utilities")
</p>
</details>

## Installation

### 1. Install dependencies

- **Mandatory dependencies** - with this dependencies installed you can install and run native games only.
- **Optional dependencies**  - with this dependencies installed you can install all games from GOG catalog (but it doesn't necessarily mean all of them will work).

#### Debian/Ubuntu

*Mandatory dependencies:*

Python 2

    sudo apt install python-gi python-bs4 python-lxml python-requests python-tz python-pil python-dateutil lgogdownloader innoextract x11-xserver-utils curl p7zip-full

Python 3

    sudo apt install python3-gi python3-bs4 python3-lxml python3-requests python3-tz python3-pil python3-dateutil lgogdownloader innoextract x11-xserver-utils curl p7zip-full


*Optional dependencies:*

    sudo apt install gksu xterm tar cabextract unshield ffmpeg megatools wine winetricks dosbox scummvm
    
#### Archlinux

'Games Nebula' available in [AUR](https://aur.archlinux.org/packages/games_nebula/), but that's unofficial package maintained by [mwohlert](https://github.com/mwohlert), so I can't guarantee that it's up-to-date.

*Mandatory dependencies:*

Python 2

    sudo pacman -S python2-gobject python2-beautifulsoup4 python2-lxml python2-pillow python2-requests python2-pytz python2-dateutil webkit2gtk innoextract xorg-xrandr curl p7zip

Python 3

    sudo pacman -S python-gobject python-beautifulsoup4 python-lxml python-pillow python-requests python3-pytz python-dateutil webkit2gtk innoextract xorg-xrandr curl p7zip

AUR: [htmlcxx](https://aur.archlinux.org/packages/htmlcxx/), [lgogdownloader](https://aur.archlinux.org/packages/lgogdownloader/)

*Optional dependencies:*

    sudo pacman -S gksu xterm tar cabextract unshield ffmpeg wine winetricks dosbox scummvm
    
AUR: [megatools](https://aur.archlinux.org/packages/megatools/)

#### Fedora

*Mandatory dependencies:*

Python 2

    sudo dnf install python python-gobject python2-pillow python-beautifulsoup4 python-requests pytz python-dateutil innoextract xorg-x11-server-utils curl p7zip p7zip-plugins

Python 3

    sudo dnf install python3 python3-gobject python3-pillow python3-beautifulsoup4 python3-requests pytz python3-dateutil innoextract xorg-x11-server-utils curl p7zip p7zip-plugins

Fedora CORP: [lgogdownloader](https://copr.fedorainfracloud.org/coprs/mmansell/lgogdownloader/)

*Optional dependencies:*

    sudo dnf install xterm tar cabextract unshield megatools wine winetricks dosbox scummvm

[RPM Fusion](https://rpmfusion.org/): ffmpeg

### 2. Install application
- Download and extract, or clone **games_nebula (master branch)** anywhere you like
- Run **setup.sh** in **terminal**. Script will download additional components (internet connection required) and create launcher

## Shortcuts
- **Ctrl + F** - Toggle fullscreen
- **Shift + T** - Toggle tabs visibility
- **Ctrl + T** - Add tab
- **Ctrl + W** - Close tab
- **Ctrl + Tab** - Next tab
- **Shift + Tab** - Previous tab
- **Ctrl + S** - Search
- **Ctrl + Q** - Quit
- **RMB on filter** - invert filter type
- **MMB on filter** - reset filter
- **RMB on game image** - add/edit tags

## Roadmap

- *~~port to python3~~*
- ***organize code & improve code quality (WIP)***

- ***write replacement for lgogdownloader (WIP)***
- *create proper packages*


## Links
- Scripts repository for gog games: [Bitbucket](https://bitbucket.org/yancharkin/games_nebula_goglib_scripts/src), [Github](https://github.com/yancharkin/games_nebula_goglib_scripts), [Gitlab](https://gitlab.com/yancharkin/games_nebula_goglib_scripts)
- Scripts repository for non-gog games: [Bitbucket](https://bitbucket.org/yancharkin/games_nebula_mylib_scripts/src/master/), [Github](https://github.com/yancharkin/games_nebula_mylib_scripts), [Gitlab](https://gitlab.com/yancharkin/games_nebula_mylib_scripts)
- [pygogapi](https://github.com/Yepoleb/pygogapi) by @Yepoleb
- My fork of [pygogapi](https://github.com/yancharkin/pygogapi) - works both in python 2 and 3 (at least partially)
