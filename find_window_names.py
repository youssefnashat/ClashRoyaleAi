import win32gui

def list_window_names():
    print('SEARCHING FOR WINDOWS...')
    def winEnumHandler(hwnd, ctx):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title: # Only print if there is text
                print(f"FOUND: {title}")
    
    win32gui.EnumWindows(winEnumHandler, None)

if __name__ == "__main__":
    list_window_names()
