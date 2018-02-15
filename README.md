# Games Nebula
Unofficial Linux client for GOG.

- **[Features](https://github.com/yancharkin/games_nebula#features)**  
- **[Screenshots](https://github.com/yancharkin/games_nebula#screenshots)**  
- **[Installation](https://github.com/yancharkin/games_nebula#installation)**  
   * [Debian/Ubuntu](https://github.com/yancharkin/games_nebula#debianubuntu)  
   * [Archlinux](https://github.com/yancharkin/games_nebula#archlinux)  
   * [Fedora](https://github.com/yancharkin/games_nebula#fedora)  
- **[Shortcuts](https://github.com/yancharkin/games_nebula#shortcuts)**  
- **[Roadmap](https://github.com/yancharkin/games_nebula#roadmap)**  
- **[Troubleshooting](https://github.com/yancharkin/games_nebula#troubleshooting)**  
- **[Also...](https://github.com/yancharkin/games_nebula#also)**  


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
For **Archlinux** 'Games Nebula' available in [AUR](https://aur.archlinux.org/packages/games_nebula/) (thanks to [mwohlert](https://github.com/mwohlert)). For other distros there is no "proper" packages yet. But it's not that hard to install.
### 1. Install dependencies

- **Mandatory dependencies** - with this dependencies installed you can install and run native games only.
- **Optional dependencies**  - with this dependencies installed you can install all games from GOG catalog (but it doesn't necessarily mean all of them will work).

#### Debian/Ubuntu

*Mandatory dependencies:*

Python 2

    sudo apt install python-gi python-bs4 python-lxml python-pil lgogdownloader innoextract x11-xserver-utils

Python 3 (master branch only)

    sudo apt install python3-gi python3-bs4 python3-lxml python3-pil lgogdownloader innoextract x11-xserver-utils


*Optional dependencies:*

    sudo apt install gksu xterm curl tar p7zip-full cabextract unshield ffmpeg megatools wine winetricks dosbox scummvm
    
#### Archlinux

*Mandatory dependencies:*

Python 2

    sudo pacman -S python2-gobject python2-beautifulsoup4 python2-lxml python2-pillow innoextract xorg-xrandr

Python 3 (master branch only)

    sudo pacman -S python-gobject python-beautifulsoup4 python-lxml python-pillow innoextract xorg-xrandr

AUR: [htmlcxx](https://aur.archlinux.org/packages/htmlcxx/), [lgogdownloader](https://aur.archlinux.org/packages/lgogdownloader/)

*Optional dependencies:*

    sudo pacman -S gksu xterm curl tar p7zip cabextract unshield ffmpeg wine winetricks dosbox scummvm
    
AUR: [megatools](https://aur.archlinux.org/packages/megatools/)

#### Fedora

*Mandatory dependencies:*

Python 2

    sudo dnf install python python-gobject python2-pillow python-beautifulsoup4 innoextract xorg-x11-server-utils

Python 3 (master branch only)

    sudo dnf install python3 python3-gobject python3-pillow python3-beautifulsoup4 innoextract xorg-x11-server-utils

Fedora CORP: [lgogdownloader](https://copr.fedorainfracloud.org/coprs/mmansell/lgogdownloader/)

*Optional dependencies:*

    sudo dnf install xterm curl tar p7zip p7zip-plugins cabextract unshield megatools wine winetricks dosbox scummvm

[RPM Fusion](https://rpmfusion.org/): ffmpeg

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
- **RMB on game image** - add/edit tags

## Roadmap
While poorly coded, 'Games Nebula' has all features that I intended to include in it, so no new features planned.

**Things need to be done:**
- fix bugs
- organize code
- improve code quality
- ~~port to python3~~
- write replacement for lgogdownloader
- create proper packages

## Troubleshooting

**Problem.** ‘Games Nebula’ fails to launch / something wrong and I don’t know why  
**Solution.** Launch 'start.sh' in terminal to get more info

**Problem.** Login always fails  
**Solution.** Use lgogdownloader directly. If you’ll managed to login with it successfully it will works in ‘Games Nebula’ as well. The only thing ‘Games Nebula’ can help you with is exporting cookies (this feature helpful if you are using lgogdownloader 3.1 - 3.2 for git version it’s usless). To do it you have to open ‘GOG.COM’ tab (in ‘Games Nebuls’) and login. For [some people](https://github.com/Sude-/lgogdownloader/issues/129) it's impossible to login with lgogdownloader > 3.2. For now the only solution is to use lgogdownloader 3.2.

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
