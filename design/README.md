# FigCraft design file

Open `khonnai.figcraft` in FigCraft. Its Pages, top-level screen frames, prototype flows, and layers use ASCII English names because FigCraft's sidebar font on this machine displays Thai node names as square glyphs. The Thai copy on the screen canvases remains Thai.

Examples: `02 Onboarding and Receiving` → `01 Sign Up`, `02 Log In`, `03 Create Shop`; `04 Bills and Reservations` → `17 Create Bill`, `23 Create Reservation`.

`khonnai.figcraft` is the only current FigCraft file. The name-normalization step changes internal labels while preserving visible Thai copy.

After regenerating any page with `build_design_system.py` or `build_screens_02.py` through `build_screens_05.py`, the scripts call `normalize_figcraft_names.py` to keep the sidebar names readable. It can also be run directly:

```powershell
& 'C:\Users\BANK\AppData\Local\Programs\Python\Python315\python.exe' design\normalize_figcraft_names.py
```

Close and reopen the FigCraft file after an external edit to load its updated sidebar names.

The click-through paths for receiving, bills, stock history, and reservations are completed by `refine_figcraft_flows.py`. It adds edit/cancelled receipt states and edit/cancelled reservation states, makes saved-detail back buttons return to the relevant list/home, and pins working bottom navigation to all 30 store screens. Each bottom menu sits after the content on the design canvas and uses a bottom constraint to stay on screen in the player. All four app pages use one fixed 375 × 812 prototype viewport; longer frames scroll within it. The postprocessor also switches text styles to Windows' Leelawadee UI, which renders Thai in FigCraft. The page builders call this postprocessor after export; it can also be run directly with Python. Reopen FigCraft after an external edit to refresh the prototype.

Run `python design/smoke_check_flows.py` to check the saved archive's key destinations and bottom menu links. The cloned FigCraft screens are click-through examples; use the web prototype to test real quantity edits and stock rules.

Current FigCraft CLI renders of the corrected layout are in `design/preview/` (home, receiving, reservation). They are visual checks of this `.figcraft` file, not separate editable versions.
