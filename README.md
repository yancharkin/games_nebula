# Games Nebula
Unofficial Linux client for GOG.

**Games Nebula is a prototype software, it works OK for me and for at least few dozen people, but that doesn't necessarily mean it will work (without issues) for you. You can face different problems using it, if you're not ready for that, then don't use this software.**

You can find installation instruction below, **it's the only supported way of installation**, I do not provide any distro-specific packages. If you installed the application using another way (AUR for example), try re-install using instruction before reporting a bug.

## Features
- Listing, downloading and installing games from your gog library
- Possibility to create you own (non-gog) library by writing simple scripts
- Integration with wine, dosbox and scummvm to make running non-native games as easy as possible
- Utilities for configurating wine, dosbox and scummvm
- Utilities and patches for some games
- Advanced tagging

...and more.

## Screenshots

**Main window**

![main window screenshot](images/screenshots/main_window.jpg  "Main window")

**DOSBox Configuration Utility**

![dosbox utility screenshot](images/screenshots/dosbox_utility.jpg  "DOSBox Configuration Utility")

**Wine, DOSBox and ScummVM launchers**

![launchers screenshot](images/screenshots/launchers.png  "Launchers")

**Configuration utilities for 'Arcanum: Of Steamworks and Magick Obscura' and 'Planescape: Torment'**

![conf_utilities](images/screenshots/conf_utilities.png  "Configuration Utilities")

## Installation

### 1. Install dependencies

- **Mandatory dependencies** - with this dependencies installed you can install and run native games only.
- **Optional dependencies**  - with this dependencies installed you can install all games from GOG catalog (but it doesn't necessarily mean all of them will work).

#### Debian/Ubuntu

*Mandatory dependencies:*

Python 2

    sudo apt install python-gi python-bs4 python-lxml python-requests python-tz python-pil python-dateutil gir1.2-webkit2-4.0 lgogdownloader x11-xserver-utils curl p7zip-full

Python 3

    sudo apt install python3-gi python3-bs4 python3-lxml python3-requests python3-tz python3-pil python3-dateutil gir1.2-webkit2-4.0 lgogdownloader x11-xserver-utils curl p7zip-full


*Optional dependencies:*

    sudo apt install gksu xterm tar cabextract unshield ffmpeg megatools wine winetricks dosbox scummvm
    
#### Archlinux

'Games Nebula' available in [AUR](https://aur.archlinux.org/packages/games_nebula/), but that's unofficial package maintained by [mwohlert](https://github.com/mwohlert), so I can't guarantee that it's up-to-date.

*Mandatory dependencies:*

Python 2

    sudo pacman -S python2-gobject python2-beautifulsoup4 python2-lxml python2-pillow python2-requests python2-pytz python2-dateutil webkit2gtk xorg-xrandr curl p7zip

Python 3

    sudo pacman -S python-gobject python-beautifulsoup4 python-lxml python-pillow python-requests python3-pytz python-dateutil webkit2gtk xorg-xrandr curl p7zip

AUR: [htmlcxx](https://aur.archlinux.org/packages/htmlcxx/), [lgogdownloader](https://aur.archlinux.org/packages/lgogdownloader/)

*Optional dependencies:*

    sudo pacman -S gksu xterm tar cabextract unshield ffmpeg wine winetricks dosbox scummvm
    
AUR: [megatools](https://aur.archlinux.org/packages/megatools/)

#### Fedora

*Mandatory dependencies:*

Python 2

    sudo dnf install python python-gobject python2-pillow python-beautifulsoup4 python-requests pytz python-dateutil xorg-x11-server-utils curl p7zip p7zip-plugins

Python 3

    sudo dnf install python3 python3-gobject python3-pillow python3-beautifulsoup4 python3-requests pytz python3-dateutil xorg-x11-server-utils curl p7zip p7zip-plugins

Fedora CORP: [lgogdownloader](https://copr.fedorainfracloud.org/coprs/mmansell/lgogdownloader/)

*Optional dependencies:*

    sudo dnf install xterm tar cabextract unshield megatools wine winetricks dosbox scummvm

[RPM Fusion](https://rpmfusion.org/): ffmpeg

### 2. Install application
- download and extract, or clone **games_nebula (master branch)** anywhere you like
- run **setup.sh** in **terminal** (use **sudo** if you don't have write permission on a directory where you put GN)
- script will ask you a number of questions (press "y" or "n" to answer):
    * if you installing GN for the first time, you probably should answer "y" to the second question to install all components
    * if you answer "n" to the second question, script will give you option to select which components to install (or update)
    * finally you'll be asked if you'd like to create launcher

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
- [Scripts repository for gog games](https://github.com/yancharkin/games_nebula_goglib_scripts)
- [Scripts repository for non-gog games](https://github.com/yancharkin/games_nebula_mylib_scripts)
- [pygogapi](https://github.com/Yepoleb/pygogapi) by [Yepoleb](https://github.com/Yepoleb)
- My fork of [pygogapi](https://github.com/yancharkin/pygogapi) - works both in python 2 and 3 (at least partially)
