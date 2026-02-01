Set WshShell = CreateObject("WScript.Shell")

' Get the directory where this script is located
Set FSO = CreateObject("Scripting.FileSystemObject")
ScriptDir = FSO.GetParentFolderName(WScript.ScriptFullName)

' Path to Python in virtual environment
PythonPath = ScriptDir & "\venv\Scripts\pythonw.exe"
LauncherScript = ScriptDir & "\start_movieflix.py"

' Check if pythonw.exe exists
If Not FSO.FileExists(PythonPath) Then
    MsgBox "Python not found in virtual environment!" & vbCrLf & vbCrLf & _
           "Please run setup first:" & vbCrLf & _
           "python -m venv venv" & vbCrLf & _
           "venv\Scripts\activate" & vbCrLf & _
           "pip install -r requirements.txt", _
           vbCritical, "MovieFlix Error"
    WScript.Quit
End If

' Launch MovieFlix (no console window)
' Using pythonw.exe ensures no console appears
WshShell.Run """" & PythonPath & """ """ & LauncherScript & """", 0, False

' Exit immediately
WScript.Quit
