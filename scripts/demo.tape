Output assets/demo.gif
Set FontSize 16
Set Width 1280
Set Height 720
Set Theme "Catppuccin Mocha"
Set Padding 24

Type "cd bookskill-studio"
Enter
Sleep 500ms
Type "python3 -m bookskill_studio demo --output demo-output"
Enter
Sleep 2s
Type "python3 -m bookskill_studio validate demo-output"
Enter
Sleep 2s
Type "python3 -m bookskill_studio open-report demo-output"
Enter
Sleep 1s
