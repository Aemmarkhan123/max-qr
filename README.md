# QR Studio

A matte-black/off-white Python desktop app with an HTML/CSS/JavaScript interface. Paste a URL, generate a QR code, customize colors and error correction, preview it, and save a PNG through the native save dialog.

## Requirements

- Python 3.10 or newer
- macOS, Windows, or Linux desktop environment
- On Linux, pywebview may need a WebKitGTK runtime installed by your distribution

## Install

### macOS / Linux

```bash
cd qr-studio
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

### Windows (PowerShell)

```powershell
cd qr-studio
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

The app opens in a desktop window. It runs a local Flask server on `127.0.0.1:8765` for the UI and QR-generation endpoint. It does not upload links to a remote service. Keep port 8765 free while running the app.

## Use

1. Paste a URL (a domain such as `example.com` is accepted).
2. Pick the QR and background colors.
3. Select an error-correction level.
4. Click **Generate QR code**.
5. Click **Download PNG**, choose a destination and filename, and save.

## Project structure

```text
qr-studio/
├── app.py
├── requirements.txt
├── README.md
├── templates/
│   └── index.html
└── static/
    ├── app.js
    └── styles.css
```

## Optional: package as an executable

Install PyInstaller in the same virtual environment:

```bash
pip install pyinstaller
```

Packaging a pywebview application can require platform-specific WebView/runtime configuration. First verify `python app.py` works on the target machine, then package and test on that same operating system.

## Notes

- URL validation checks for an HTTP(S) scheme and a plausible host. It does not verify that the destination website is online.
- For reliable scanning, use strong contrast and test the downloaded QR code before printing.
- Google Fonts are referenced by the stylesheet for typography; the application itself does not need them to function, and system fallback fonts are used offline.
