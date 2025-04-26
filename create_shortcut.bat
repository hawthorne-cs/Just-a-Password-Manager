@echo off
echo Creating desktop shortcut...
powershell "$s=(New-Object -COM WScript.Shell).CreateShortcut('%userprofile%\Desktop\Password Manager.lnk');$s.TargetPath='%~dp0dist\Password Manager\Password Manager.exe';$s.IconLocation='%~dp0key.ico';$s.Save()"
echo Done!
pause 