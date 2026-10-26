import ctypes
from ctypes import wintypes
import time
import threading
import webview

HMI_TITLE = "Uconnect 8.4AN (RA4 17.43.01)"

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

def get_uconnect_rect():
    u = ctypes.windll.user32
    found = [None]
    
    @ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    def cb(hwnd, lparam):
        if u.IsWindowVisible(hwnd):
            length = u.GetWindowTextLengthW(hwnd)
            if length > 0:
                buf = ctypes.create_unicode_buffer(length + 1)
                u.GetWindowTextW(hwnd, buf, length + 1)
                if "uconnect" in buf.value.lower():
                    found[0] = hwnd
                    return False
        return True

    u.EnumWindows(cb, 0)
    hwnd = found[0]
    if not hwnd:
        return None
        
    r = wintypes.RECT()
    u.GetWindowRect(hwnd, ctypes.byref(r))
    return r.left, r.top, r.right - r.left, r.bottom - r.top

def main():

    window = webview.create_window(
        "Nav Map Overlay", 
        html=MAP_HTML,
        frameless=True,
        transparent=True,
        on_top=True,
        hidden=True,
        width=400,
        height=300
    )

    is_visible = False

    def global_hotkey_listener():
        nonlocal is_visible
        import keyboard  # simple library: pip install keyboard
        

        while True:
            if keyboard.is_pressed('F5'):
                rect = get_uconnect_rect()
                if rect:
                    x, y, w, h = rect
                    # Snap to the exact screen bounds inside the radio frame
                    window.move(x + 14, y + 72)
                    window.resize(w - 28, h - 145)
                    
                    if is_visible:
                        window.hide()
                        is_visible = False
                    else:
                        window.show()
                        is_visible = True
                time.sleep(0.5) # debounce delay
            time.sleep(0.05)


    try:
        import keyboard
        threading.Thread(target=global_hotkey_listener, daemon=True).start()
    except ImportError:
        print("Tip: run 'pip install keyboard' if you want a keyboard hotkey to toggle it.")

    webview.start()

if __name__ == "__main__":
    main()