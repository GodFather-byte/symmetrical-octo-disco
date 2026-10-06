#define AppName "Recibo PIX"
#define AppVersion "1.0.0"
#define EnvVersion GetEnv("APP_VERSION")
#if EnvVersion != ""
  #undef AppVersion
  #define AppVersion EnvVersion
#endif

[Setup]
AppId={{6F1B2C0E-4A7D-4B8E-9C55-0A1B2C3D4E5F}
AppName={#AppName}
AppVersion={#AppVersion}
DefaultDirName={autopf}\ReciboPix
DefaultGroupName={#AppName}
OutputDir=..\dist-installer
OutputBaseFilename=ReciboPix-Setup
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
UninstallDisplayIcon={app}\ReciboPix.exe

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na Área de Trabalho"; Flags: checkedonce

[Files]
Source: "..\dist\ReciboPix.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\ReciboPix.exe"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\ReciboPix.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\ReciboPix.exe"; Description: "Abrir o programa"; Flags: nowait postinstall skipifsilent
