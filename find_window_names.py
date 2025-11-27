import win32gui
import os
import re

def update_config(window_title):
    """Update the config.py file with the selected window pattern."""
    config_path = os.path.join(os.path.dirname(__file__), 'src', 'config.py')
    
    # Extract a reasonable pattern (first word or first few words)
    words = window_title.split()[:2]
    pattern = words[0] if words else window_title
    
    try:
        with open(config_path, 'r') as f:
            content = f.read()
        
        # Replace the WINDOW_NAME_PATTERNS line
        new_content = re.sub(
            r'WINDOW_NAME_PATTERNS\s*=\s*\[.*?\]',
            f'WINDOW_NAME_PATTERNS = ["{pattern}"]',
            content
        )
        
        with open(config_path, 'w') as f:
            f.write(new_content)
        
        print(f"✓ Successfully updated config.py")
        print(f"  WINDOW_NAME_PATTERNS = [\"{pattern}\"]")
        return True
    except Exception as e:
        print(f"✗ Failed to update config.py: {e}")
        return False

def list_window_names():
    """List all visible windows and let user select one."""
    windows = []
    
    print('SEARCHING FOR WINDOWS...\n')
    
    def winEnumHandler(hwnd, ctx):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:  # Only include if there is text
                windows.append((hwnd, title))
    
    win32gui.EnumWindows(winEnumHandler, None)
    
    if not windows:
        print("No visible windows found.")
        return
    
    print(f"Found {len(windows)} windows:\n")
    
    # Display windows with numbering
    for i, (hwnd, title) in enumerate(windows, 1):
        print(f"{i:3d}. {title}")
    
    print("\n" + "="*80)
    
    # Let user select a window
    while True:
        try:
            choice = input("\nEnter the number of the window you want to use (or 'q' to quit): ").strip()
            
            if choice.lower() == 'q':
                print("Exiting...")
                return
            
            num = int(choice)
            if 1 <= num <= len(windows):
                hwnd, title = windows[num - 1]
                print(f"\nYou selected: {title}")
                print(f"Window Handle (hwnd): {hwnd}")
                
                # Automatically update config
                print("\nUpdating config.py...")
                if update_config(title):
                    print("\n✓ Configuration updated! You can now run main.py")
                else:
                    print("\n✗ Failed to update config. Please update manually:")
                    words = title.split()[:2]
                    pattern = words[0] if words else title
                    print(f'  WINDOW_NAME_PATTERNS = ["{pattern}"]')
                break
            else:
                print(f"Please enter a number between 1 and {len(windows)}")
        except ValueError:
            print("Invalid input. Please enter a number or 'q'.")

if __name__ == "__main__":
    list_window_names()
