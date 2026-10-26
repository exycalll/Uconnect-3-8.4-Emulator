import ctypes
from ctypes import wintypes
import time
import threading
import json
import os

HMI_TITLE = "Uconnect 8.4AN (RA4 17.43.01)"
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

MAP_HTML = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body, html { margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; background: #000; }
        iframe { width: 100%; height: 100%; border: 0; }
    </style>
</head>
<body>
    <iframe id="gmap" src="https://maps.google.com/maps?q=42.3314,-83.0458&z=14&output=embed"></iframe>
</body>
</html>
"""

def get_hmi_rect():
    u = ctypes.windll.user32
    hwnd = u.FindWindowW(None, HMI_TITLE)
    if not hwnd or not u.IsWindowVisible(hwnd):
        return None
    r = wintypes.RECT()
    pt = wintypes.POINT(0, 0)
    u.GetClientRect(hwnd, ctypes.byref(r))
    u.ClientToScreen(hwnd, ctypes.byref(pt))
    return pt.x, pt.y, r.right, r.bottom

def get_current_screen():
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f).get("lastScreen", "").lower()
    except Exception:
        pass
    return ""

def main():
    try:
        import webview
    except ImportError:
        print("Please run: pip install pywebview")
        return

    window = webview.create_window(
        "Nav Map Overlay", 
        html=MAP_HTML,
        frameless=True,
        transparent=True,
        on_top=True
    )
    
    is_visible = False

    def track_loop():
        nonlocal is_visible
        while True:
            screen = get_current_screen()
            is_nav_screen = any(keyword in screen for keyword in ["nav", "map"])
            
            rect = get_hmi_rect()
            if rect and is_nav_screen:
                x, y, w, h = rect
                
                map_x = x
                map_y = y + 95
                map_w = w
                map_h = h - 225
                
                try:
                    window.move(map_x, map_y)
                    window.resize(map_w, map_h)
                    if not is_visible:
                        window.show()
                        is_visible = True
                except Exception:
                    pass
            else:
                if is_visible:
                    try:
                        window.hide()
                        is_visible = False
                    except Exception:
                        pass
            time.sleep(0.1)

    threading.Thread(target=track_loop, daemon=True).start()
    webview.start()

if __name__ == "__main__":
    main()