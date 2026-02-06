#!/usr/bin/env python3
"""
Ollama availability checker with user-friendly GUI prompts.
Shows helpful dialogs if Ollama is not installed or running.
"""

import subprocess
import sys
import webbrowser


def is_ollama_installed() -> bool:
    """Check if Ollama is installed on the system."""
    try:
        result = subprocess.run(
            ["which", "ollama"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


def is_ollama_running() -> bool:
    """Check if Ollama server is running."""
    try:
        import urllib.request
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req, timeout=3) as response:
            return response.status == 200
    except Exception:
        return False


def show_ollama_not_installed_dialog() -> bool:
    """Show dialog when Ollama is not installed. Returns True if user wants to download."""
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()

        result = messagebox.askyesno(
            "Ollama Required",
            "Language Tutor requires Ollama to run AI models locally.\n\n"
            "Ollama is not installed on your system.\n\n"
            "Would you like to open the Ollama download page?\n\n"
            "After installing Ollama, please restart Language Tutor.",
            icon='warning'
        )

        root.destroy()
        return result
    except Exception:
        print("ERROR: Ollama is not installed.")
        print("Please download Ollama from: https://ollama.com/download")
        return False


def show_ollama_not_running_dialog() -> bool:
    """Show dialog when Ollama is installed but not running. Returns True if user wants to start it."""
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()

        result = messagebox.askyesno(
            "Start Ollama",
            "Language Tutor requires Ollama to be running.\n\n"
            "Ollama is installed but not currently running.\n\n"
            "Would you like to start Ollama now?",
            icon='info'
        )

        root.destroy()
        return result
    except Exception:
        print("ERROR: Ollama is not running.")
        print("Please start Ollama and try again.")
        return False


def start_ollama() -> bool:
    """Attempt to start Ollama. Returns True if successful."""
    try:
        # On macOS, try to open the Ollama app
        subprocess.Popen(
            ["open", "-a", "Ollama"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # Wait a bit for it to start
        import time
        for _ in range(10):
            time.sleep(1)
            if is_ollama_running():
                return True

        return False
    except Exception:
        return False


def show_ollama_started_dialog():
    """Show success dialog after Ollama starts."""
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()

        messagebox.showinfo(
            "Ollama Started",
            "Ollama is now running!\n\nStarting Language Tutor..."
        )

        root.destroy()
    except Exception:
        print("Ollama started successfully!")


def show_ollama_failed_to_start_dialog():
    """Show error dialog when Ollama fails to start."""
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()

        messagebox.showerror(
            "Failed to Start Ollama",
            "Could not start Ollama automatically.\n\n"
            "Please start Ollama manually from your Applications folder,\n"
            "then restart Language Tutor."
        )

        root.destroy()
    except Exception:
        print("ERROR: Could not start Ollama.")
        print("Please start Ollama manually and try again.")


def check_ollama_availability() -> bool:
    """
    Main function to check Ollama availability.
    Shows appropriate dialogs and attempts to resolve issues.

    Returns:
        True if Ollama is ready to use, False otherwise.
    """
    # Check if Ollama is running
    if is_ollama_running():
        return True

    # Check if Ollama is installed
    if not is_ollama_installed():
        if show_ollama_not_installed_dialog():
            webbrowser.open("https://ollama.com/download")
        return False

    # Ollama is installed but not running
    if show_ollama_not_running_dialog():
        if start_ollama():
            show_ollama_started_dialog()
            return True
        else:
            show_ollama_failed_to_start_dialog()
            return False

    return False


if __name__ == "__main__":
    # Test the checker
    if check_ollama_availability():
        print("Ollama is ready!")
    else:
        print("Ollama is not available.")
        sys.exit(1)
