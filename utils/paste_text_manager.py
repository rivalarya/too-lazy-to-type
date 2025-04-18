import pyperclip
import time
from pynput.keyboard import Controller, Key


class PasteTextManager:
    """Manages pasting of text using the clipboard."""

    def __init__(self):
        self.keyboard = Controller()

    def paste_text(self, text):
        """Paste text using clipboard (most reliable method)."""
        # Copy text to clipboard
        pyperclip.copy(text)
        time.sleep(0.1)  # Small delay to ensure clipboard is updated

        # Press Ctrl+V to paste
        with self.keyboard.pressed(Key.ctrl):
            self.keyboard.press('v')
            self.keyboard.release('v')

        time.sleep(0.1)  # Small delay after pasting
