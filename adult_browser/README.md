# Adult Video Sidebar Desktop

A standalone desktop browser app with a custom dark interface, site shortcuts, address bar, back/forward/reload, and tabs. Websites load as top-level Chromium WebEngine pages—not inside extension iframes—so iframe `X-Frame-Options` / `frame-ancestors` blocking does not apply in the same way.

## Run on Windows
1. Install Python 3.10+ (64-bit).
2. Open PowerShell in this folder.
3. Run:
   ```powershell
   py -m pip install -r requirements.txt
   py adult_video_sidebar.py
   ```

## Build an EXE (optional)
```powershell
py -m pip install pyinstaller
py -m PyInstaller --noconsole --onedir --name AdultVideoSidebar adult_video_sidebar.py
```
Output is in `dist\AdultVideoSidebar`.

## Notes
- This is a standalone desktop browser, not an Opera extension.
- Some sites may still enforce login, age verification, anti-bot, or browser compatibility requirements.
- No frame-header bypass is performed; the sites are opened as top-level pages in the embedded Chromium engine.
