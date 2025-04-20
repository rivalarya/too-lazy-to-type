[Setup]
AppName=TooLazyToType
AppPublisher=Rival Arya Pirmansah
AppPublisherURL=https://github.com/rivalarya/too-lazy-to-type.git
AppVersion=1.1.0
DefaultDirName={localappdata}\TooLazyToType
DefaultGroupName=TooLazyToType
OutputDir=installer_output
OutputBaseFilename=TooLazyToTypeInstaller
Compression=lzma
SolidCompression=yes
Uninstallable=yes
UninstallDisplayIcon={app}\TooLazyToType.exe
PrivilegesRequired=lowest
 
[Files]
; Main executable from PyInstaller
Source: "dist\TooLazyToType.exe"; DestDir: "{app}"; Flags: ignoreversion
 
[Icons]
Name: "{group}\TooLazyToType"; Filename: "{app}\TooLazyToType.exe"
Name: "{commondesktop}\TooLazyToType"; Filename: "{app}\TooLazyToType.exe"
 
[Run]
Filename: "{app}\TooLazyToType.exe"; Description: "Launch application"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: files; Name: "{app}\recording.wav"
Type: files; Name: "{app}\config.json"
Type: dirifempty; Name: "{app}"