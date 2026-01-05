; Inno Setup script to package the VPN Profile Manager one-folder build.
; It expects the PyInstaller output in ../dist/VPNProfileManager with the
; OpenConnect/OpenVPN executables placed in the bin directory.

[Setup]
AppName=VPN Profile Manager
AppVersion=1.0.0
DefaultDirName={pf}\VPNProfileManager
DefaultGroupName=VPN Profile Manager
UninstallDisplayIcon={app}\VPNProfileManager.exe
OutputBaseFilename=VPNProfileManagerSetup
Compression=lzma
SolidCompression=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Files]
; Copy the entire PyInstaller one-folder output while keeping the bin layout
Source: "..\dist\VPNProfileManager\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\VPN Profile Manager"; Filename: "{app}\VPNProfileManager.exe"
Name: "{commondesktop}\VPN Profile Manager"; Filename: "{app}\VPNProfileManager.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked
