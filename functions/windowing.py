"""
Windowing module for listing and selecting available windows.
This module provides functionality to enumerate all visible windows
and return the selected window for recording by the vision module.
"""

import win32gui  # type: ignore


def get_all_windows():
    """
    Enumerate all visible windows on the system.
    
    Returns:
        list: List of tuples (hwnd, title) for each visible window
    """
    windows = []
    
    def callback(hwnd, extra):
        """Callback function for EnumWindows."""
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:  # Only include windows with titles
                windows.append((hwnd, title))
    
    win32gui.EnumWindows(callback, None)
    return windows


def display_windows(windows):
    """
    Display available windows in a numbered list.
    
    Args:
        windows (list): List of tuples (hwnd, title) from get_all_windows()
    """
    print(f"\nFound {len(windows)} visible windows:\n")
    print("-" * 80)
    for i, (hwnd, title) in enumerate(windows, 1):
        print(f"{i:3d}. {title}")
    print("-" * 80)


def select_window(windows):
    """
    Prompt user to select a window from the list.
    
    Args:
        windows (list): List of tuples (hwnd, title) from get_all_windows()
    
    Returns:
        tuple: (hwnd, title) of the selected window, or (None, None) if cancelled
    """
    while True:
        try:
            choice = input("\nEnter the window number to select (or 'q' to cancel): ").strip()
            
            if choice.lower() == 'q':
                print("Selection cancelled.")
                return None, None
            
            num = int(choice)
            if 1 <= num <= len(windows):
                hwnd, title = windows[num - 1]
                print(f"\n✓ Selected: {title}")
                return hwnd, title
            else:
                print(f"Invalid selection. Please enter a number between 1 and {len(windows)}")
        except ValueError:
            print("Invalid input. Please enter a number or 'q'.")


def list_and_select_window():
    """
    Main function to list all windows and allow user selection.
    
    Returns:
        tuple: (hwnd, title) of the selected window, or (None, None) if cancelled
    """
    print("=" * 80)
    print("WINDOW SELECTOR FOR RECORDING")
    print("=" * 80)
    
    windows = get_all_windows()
    
    if not windows:
        print("\nNo visible windows found on the system.")
        return None, None
    
    display_windows(windows)
    hwnd, title = select_window(windows)
    
    if hwnd:
        print(f"\nWindow handle (hwnd): {hwnd}")
        print("This window will be recorded by the vision module.")
    
    return hwnd, title


if __name__ == "__main__":
    # Interactive mode for testing
    list_and_select_window()
