# Lab demo videos (VS Code screen recordings)

`lab/vscode/index.html` is a VS Code window built from the parts VS Code itself uses: the Monaco editor engine
(same syntax colouring, cursor and line numbers) and the xterm terminal, with the Explorer, tabs, menus and status
bar laid out to match VS Code Dark. `lab/driver.js` drives it through Playwright like a person (mouse, new file,
typing paced to the narration, Ctrl+S, Terminal menu, compile, run, input) and records the screen; `lab/mix_lab.py`
lays the narration over the recording.

    cd lab/vscode && npm install monaco-editor@0.52.2 @xterm/xterm@5.5.0 @xterm/addon-fit@0.10.0 && http-server -p 8765 -s . &
    node lab/driver.js projects/lab-01 projects/lab-01/durations.json projects/lab-01/rec
    python3 lab/mix_lab.py projects/lab-01/rec projects/lab-01/voice projects/lab-01/output/lab-01.mp4
