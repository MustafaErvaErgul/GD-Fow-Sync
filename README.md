# Introduction
Python code that lets you generate a ".exe" that syncs your fog of war discovery between Grim Dawn characters.

The program watches for changes in the Grim Dawn save directory and syncs the most updated .fow file across all characters.

It does this by checking for the .fow file with the largest file size since in Grim Dawn the more you discover the map the bigger the .fow file gets.

You can use the .ahk file in this repository to run both Grim Dawn and this "gdfowsync.exe" with a single file click. Its just for convenience. If you'd prefer not to use it, start the game first and than run "gdfowsync.exe".

Search for "USERPATH" in the project to see where you need to change to suit your own installation.

# Packaging

Creating the .exe with console for debugging purposes
* python -m PyInstaller --onefile gdfowsync.py

Creating the .exe without console for general use
* python -m PyInstaller --onefile --noconsole gdfowsync.py
