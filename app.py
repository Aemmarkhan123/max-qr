import base64
import io
import threading
import time
import tkinter as tk
from tkinter import filedialog

import qrcode
import webview
from flask import Flask, jsonify, render_template, request
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H
from PIL import ImageColor

app = Flask(__name__)
ERROR_LEVELS = {
    "L": ERROR_CORRECT_L,
    "M": ERROR_CORRECT_M,
    "Q": ERROR_CORRECT_Q,
    "H": ERROR_CORRECT_H,
}


def normalize_url(value):
    value = (value or "").strip()
    if not value:
        raise ValueError("Paste a URL first.")
    if any(ch.isspace() for ch in value):
        raise ValueError("URLs cannot contain spaces.")
    if "://" not in value:
        value = "https://" + value
    from urllib.parse import urlparse
    parsed = urlparse(value)
    if parsed.scheme not in ("http", "https") or not parsed.netloc or "." not in parsed.netloc:
        raise ValueError("Enter a valid website URL, such as https://example.com.")
    return value


def make_qr(payload):
    url = normalize_url(payload.get("url"))
    foreground = payload.get("foreground", "#111111")
    background = payload.get("background", "#F7F5EF")
    level = payload.get("errorCorrection", "M")
    try:
        ImageColor.getrgb(foreground)
        ImageColor.getrgb(background)
    except ValueError:
        raise ValueError("Choose valid foreground and background colors.")
    if foreground.lower() == background.lower():
        raise ValueError("Foreground and background colors must be different.")

    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_LEVELS.get(level, ERROR_CORRECT_M),
        box_size=12,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    image = qr.make_image(fill_color=foreground, back_color=background).convert("RGB")
    output = io.BytesIO()
    image.save(output, format="PNG")
    encoded = base64.b64encode(output.getvalue()).decode("ascii")
    return url, encoded, image.size


class DesktopAPI:
    def save_qr(self, data_url, suggested_name="qr-studio.png"):
        try:
            if not data_url.startswith("data:image/png;base64,"):
                return {"ok": False, "message": "The QR image data was not recognized."}
            image_bytes = base64.b64decode(data_url.split(",", 1)[1], validate=True)
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            path = filedialog.asksaveasfilename(
                parent=root,
                title="Save QR code",
                initialfile=suggested_name or "qr-studio.png",
                defaultextension=".png",
                filetypes=[("PNG image", "*.png")],
            )
            root.destroy()
            if not path:
                return {"ok": False, "cancelled": True, "message": "Save cancelled."}
            with open(path, "wb") as file:
                file.write(image_bytes)
            return {"ok": True, "path": path, "message": "QR code saved successfully."}
        except Exception as exc:
            return {"ok": False, "message": f"Could not save the image: {exc}"}


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/generate")
def generate():
    try:
        payload = request.get_json(silent=True) or {}
        url, encoded, size = make_qr(payload)
        return jsonify({
            "ok": True,
            "url": url,
            "image": "data:image/png;base64," + encoded,
            "dimensions": f"{size[0]} × {size[1]} px",
        })
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    except Exception:
        app.logger.exception("QR generation failed")
        return jsonify({"ok": False, "error": "Something went wrong while generating the QR code."}), 500


def main():
    server = threading.Thread(
        target=lambda: app.run(host="127.0.0.1", port=8765, debug=False, use_reloader=False),
        daemon=True,
    )
    server.start()
    time.sleep(0.6)
    webview.create_window(
        "QR Studio",
        "http://127.0.0.1:8765",
        js_api=DesktopAPI(),
        width=1180,
        height=800,
        min_size=(900, 650),
        background_color="#111111",
    )
    webview.start()


if __name__ == "__main__":
    main()
