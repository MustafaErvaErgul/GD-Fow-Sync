; Path to the .ini file
iniFilePath := A_ScriptDir . "\gdfowsync.ini"  ; Assumes the .ini file is in the same directory as the AHK script

; Read paths from the .ini file
IniRead, grimDawnPath, %iniFilePath%, PATH, GD_EXE_PATH
IniRead, fowSyncPath, %iniFilePath%, PATH, GD_FOWSYNC_PATH

; Remove surrounding quotes from the paths (if present)
grimDawnPath := Trim(grimDawnPath, """")
fowSyncPath := Trim(fowSyncPath, """")

; Start Grim Dawn
Run, %grimDawnPath%, , Max

; Wait for Grim Dawn to fully load (adjust timing if needed)
Sleep, 10000

; Start Fog of War Sync tool
Run, %fowSyncPath%

; Wait until Grim Dawn closes
Process, WaitClose, Grim Dawn.exe

; When Grim Dawn is closed, kill the Fog of War Sync process
Process, Close, gdfowsync.exe

ExitApp