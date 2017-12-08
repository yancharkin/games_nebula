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
For **Archlinux** 'Games Nebula' available in [AUR](https://aur.archlinux.org/packages/games_nebula/) (thanks to [mwohlert](https://github.com/mwohlert)). For other distros there is no "proper" packages yet. But it's not that hard to install.
### 1. Install dependencies

#### Debian/Ubuntu

*Mandatory dependencies:*

    sudo apt install python-gi python-bs4 python-lxml python-pil lgogdownloader innoextract

*Optional (but highly recommended) dependencies:*

    sudo apt install gksu xterm curl tar p7zip-full cabextract unshield ffmpeg megatools wine winetricks dosbox scummvm
    
#### Archlinux
If you want to install it yourself.

*Mandatory dependencies:*

    sudo pacman -S python2-gobject python2-beautifulsoup4 python2-lxml python2-pillow innoextract

*AUR: [htmlcxx](https://aur.archlinux.org/packages/htmlcxx/), [lgogdownloader](https://aur.archlinux.org/packages/lgogdownloader/)*

*Optional (but highly recommended) dependencies:*

    sudo pacman -S gksu xterm curl tar p7zip cabextract unshield ffmpeg wine winetricks dosbox scummvm
    
*AUR: [megatools](https://aur.archlinux.org/packages/megatools/)*

#### Fedora

*Mandatory dependencies:*

    sudo dnf install python python-gobject python2-pillow python-beautifulsoup4 innoextract

*You have to compile [lgogdownloader](https://github.com/Sude-/lgogdownloader) yourself*

*Optional (but highly recommended) dependencies:*

    sudo dnf install xterm curl tar p7zip p7zip-plugins cabextract unshield megatools wine winetricks dosbox scummvm

*[RPM Fusion](https://rpmfusion.org/): ffmpeg*

### 2. Install application
- Download the [latest release](https://github.com/yancharkin/games_nebula/releases) and extract it anywhere you like.
- Run **setup.sh**. It will create shortcut in main menu.
- It's highly recommended to configure lgogdownloader **BEFORE** launching 'Games Nebula'. I tried to make login more user friendly, but it not always work. And for versions < 3.2 it's a mandatory.

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

## Troubleshooting

**Problem.** ‘Games Nebula’ fails to launch / something wrong and I don’t know why  
**Solution.** Launch 'start.sh' in terminal to get more info

**Problem.** Login always fails  
**Solution.** Use lgogdownloader directly. If you’ll managed to login with it successfully it will works in ‘Games Nebula’ as well. The only thing ‘Games Nebula’ can help you with is exporting cookies (this feature helpful if you are using lgogdownloader 3.1 - 3.2 for git version it’s usless). To do it you have to open ‘GOG.COM’ tab (in ‘Games Nebuls’) and login.

**Problem.** Windows game crashes even though 'Games Nebula' has installation script for it  
**Solution.** A lot of things can go wrong with Windows games :)
- Your hardware may be not good enough (even if game works in Windows, it needs more resources when using Wine)
- If you're using one wine prefix for all games, some dlls may conflict with each other. Usually it's better to use a separate prefix for every game (can be enabled in main settings or in the launcher)
- Some games won't  work if you are enable virtual desktop

**Problem.** Native Linux game fails to launch  
**Solution.** Check GOG store page, maybe you need to install additional libraries. Check terminal output.

## Also...
- [Scripts repository for gog games](https://github.com/yancharkin/games_nebula_goglib_scripts)
- [Scripts repository for non-gog games](https://github.com/yancharkin/games_nebula_mylib_scripts)
