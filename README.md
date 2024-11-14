# Games Nebula

Unofficial (Linux) CLI and GUI (WIP) client for GOG.

## Important Disclaimer

**The application is only partially functional (more info below), and its development is currently on hold. The original plan was to release it in 2022, but *unforeseen circumstances* delayed progress, and I have had different priorities since then. As of writing this, I've found some time to piece together the already written code and create a somewhat usable application.**

**The previous (prototype) version is available [here](https://github.com/yancharkin/games_nebula/tree/prototype) and likely still works.**

## Differences from the prototype version:

- Much better code quality (though still not necessarily perfect)
- Qt instead of GTK
- Both CLI and GUI clients
- Very few dependencies
- Not fully functional yet :)

## What it is and what it is not

It is a simple application for listing, downloading, installing, and playing games from GOG - nothing more. One notable feature is that, with the app, you can make an offline copy of your GOG library without having to install every single game. I'd also like to add most (but not all) features from the [prototype](https://github.com/yancharkin/games_nebula/tree/prototype), so you can check it out to get an idea of what to expect. However, in general, I’d like to keep it even simpler.

It is **not** a full-featured client like GOG Galaxy, both because it’s impossible for someone outside of CD Projekt to create one, and because I don’t want to.

## CLI
Mostly complete. There may still be a few bugs here and there, but it should be usable. It can be used in both interactive (shell-like) mode and non-interactive mode (like a simpler version of [lgogdownloader](https://github.com/Sude-/lgogdownloader)).

<p align="center">
        <img src="https://github.com/yancharkin/games_nebula/blob/main/screenshots/screenshot_cli.webp" width="80%">
</p>

## GUI (WIP)

Almost nothing works yet. It's possible to view and sort your library, and launch games that were installed using the CLI client. Also, the first launch will take some time, as the app needs to download images for all the games in the library, and right now it is implemented in a less-than-ideal way.

<p align="center">
        <img src="https://github.com/yancharkin/games_nebula/blob/main/screenshots/screenshot_gui.webp" width="80%">
</p>


## Dependencies

Nothing(?) for CLI, PyQt and PyQtWebEngine 5 or 6 for GUI

## Installation

- There is no need to install the app. After installing the dependencies, you can launch it by executing the 'games_nebula' file in the 'bin' directory.

 - A PKGBUILD file is included to create an Arch Linux package.

 - Any other method for building and installing a Python package should also work, but the app expects certain files to be placed in system directories. Since it's not a good idea to install files there without a package manager, I recommend sticking to the first method if you're not on an Arch-based system, or creating a package for your distro.

## Running the app

- Type 'games_nebula' (without any arguments) in the terminal to run the interactive CLI app.
- Type 'games_nebula --help' in the terminal to see which arguments can be used with the non-interactive CLI app.
- Type 'games_nebula --gui'  in the terminal to run the GUI version of the app.

## More OSes

Originally, I planned to make the app cross-platform, so with a little extra work, it should be possible to run it on most desktop OSes. However, this task is currently a very low priority.

## Future of the project

Actually, I think most of the work is already done, and it shouldn't be too hard to implement the rest. However, I currently lack both the time and motivation to continue. Hopefully, this will change, as I'd prefer not to abandon the project.
