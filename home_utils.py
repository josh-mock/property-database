from tkinter import *


def center_window(window, width, height):
    # Get the screen dimensions
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calculate the x and y coordinates for the Tk window
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    # Set the geometry of the window
    window.geometry(f"{width}x{height}+{x}+{y}")


def clear_current_window(root):
    for widget in root.winfo_children():
        widget.destroy()


