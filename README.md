# Introduction

This Python program creates an .exe that automatically syncs your fog of war (.fow) discovery across all Grim Dawn characters.

It monitors the game's save directory and detects the .fow file with the largest size—since more map discovery results in a bigger file—then copies it to all characters.

For convenience, you can use the included .ahk script to launch both Grim Dawn and gdfowsync.exe with a single click. Otherwise, start the game first, then run gdfowsync.exe.

Update "gdfowsync.ini" with your custom Grim Dawn paths before use.

# Installation

You can package the .exe yourself using the python code or just head to the releases and download the latest .exe from there. 

Make sure to update the .ini file with the correct paths for your system.

[Download the latest release](https://github.com/MustafaErvaErgul/GD-Fow-Sync/releases)

# Packaging

To create the .exe yourself, use PyInstaller:

With console (for debugging):
* python -m PyInstaller --onefile gdfowsync.py

Without console (for general use):
* python -m PyInstaller --onefile --noconsole gdfowsync.py
