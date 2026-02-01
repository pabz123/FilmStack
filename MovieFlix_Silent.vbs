Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")

' Get the directory where this script is located
ScriptDir = FSO.GetParentFolderName(WScript.ScriptFullName)

' Path to the complete launcher batch file
LauncherPath = ScriptDir & "\start_movieflix_silent.bat"

' Check if launcher exists
If Not FSO.FileExists(LauncherPath) Then
    MsgBox "Launcher not found!" & vbCrLf & vbCrLf & _
           "Expected: " & LauncherPath, _
           vbCritical, "MovieFlix Error"
    WScript.Quit
End If

' Run the launcher completely hidden (no window at all)
' Window style 0 = hidden, False = don't wait for completion
WshShell.Run """" & LauncherPath & """", 0, False

' Exit immediately
WScript.Quit
