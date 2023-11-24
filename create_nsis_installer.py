nsis_script1 = """
Outfile "MyInstaller.exe"
RequestExecutionLevel admin
InstallDir $PROGRAMFILES\MyApp

Section
SetOutPath $INSTDIR
File /r "A:\\Users\\Ada\\GitHub\\BackupInspector\\private\\ada_build_tools\\builds\\BackupInspector.exe"
CreateShortCut "$DESKTOP\BackupInspector.lnk" "$INSTDIR\BackupInspector.exe"
SectionEnd
"""


nsis_script = """
!include MUI2.nsh

# Define the name of the installer executable
Outfile "MyInstaller.exe"

# Request execution level
RequestExecutionLevel admin

# Default installation directory
InstallDir $PROGRAMFILES\MyApp

# Modern UI configuration
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES

# Function to open a URL
Function OpenURL
  ExecShell "open" "$0"
FunctionEnd

# Directory page custom page
Page custom MyCustomPage

Section
  SetOutPath $INSTDIR
  File /r "A:\\Users\\Ada\\GitHub\\BackupInspector\\private\\ada_build_tools\\builds\\BackupInspector.exe"
SectionEnd
"""

### ADD THIS BACK TO ABOVE WHEN FIXED!!!
"""
Function MyCustomPage
  nsDialogs::Create 1018
  Pop $0

  # Create a link to the website
  ${NSD_CreateLink} 0 15u 100% 10u "Visit Website"
  Pop $1
  ${NSD_OnClick} $1 OpenURL "https://www.example.com"

  # Create a link to the release notes
  ${NSD_CreateLink} 0 30u 100% 10u "Release Notes"
  Pop $2
  ${NSD_OnClick} $2 OpenURL "https://example.com/release-notes"

  nsDialogs::Show
FunctionEnd

# Component page for creating a desktop shortcut
!define MUI_PAGE_CUSTOMFUNCTION_SHOW ComponentsPageShow
!insertmacro MUI_PAGE_COMPONENTS

Function ComponentsPageShow
  # Create a checkbox for the desktop shortcut
  !insertmacro MUI_HEADER_TEXT "Create Desktop Shortcut" "Select whether to create a desktop shortcut"
  ${NSD_CreateCheckbox} 0 30u 100% 10u "Create Desktop Shortcut"
  Pop $3
FunctionEnd
"""


with open('YourInstallerScript.nsi', 'w') as nsi_file:
    nsi_file.write(nsis_script)

import subprocess
import os

nsis_compiler = r"C:\Program Files (x86)\NSIS\makensis.exe"  # Replace with the actual path to makensis.exe
nsi_script_file = "YourInstallerScript.nsi"  # The NSIS script you generated

cmd = [nsis_compiler, nsi_script_file]
subprocess.run(cmd, shell=True)

# Remove the NSIS script file
os.remove(nsi_script_file)

