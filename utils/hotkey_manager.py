import keyboard


class HotkeyManager:
    """Manages keyboard hotkeys"""

    def __init__(self):
        self.current_hotkey = ""
        self.current_mode = "hold"

    def set_hotkey(self, hotkey, mode, press_callback, release_callback=None):
        """Set up a new hotkey"""
        # Remove any existing hotkey
        keyboard.unhook_all()

        self.current_hotkey = hotkey
        self.current_mode = mode

        # Set up hotkey based on current mode
        if mode == "hold":
            # For hold mode, we need both press and release callbacks
            # Wrap the callbacks to handle the event parameter
            def press_wrapper(e):
                if self._check_modifiers():
                    press_callback()

            def release_wrapper(e):
                if release_callback:
                    release_callback()

            # Set up the keyboard hooks
            key = hotkey.split('+')[-1]  # Last part is the non-modifier key
            keyboard.on_press_key(key, press_wrapper, suppress=False)
            keyboard.on_release_key(key, release_wrapper, suppress=False)

        else:  # toggle mode
            # For toggle mode, we only need the press callback
            def toggle_wrapper():
                press_callback()

            # Set up the toggle hotkey
            keyboard.add_hotkey(hotkey, toggle_wrapper)

        print(f"Hotkey '{hotkey}' set with mode: {mode}")

    def _check_modifiers(self):
        """Check if modifier keys in the hotkey are pressed"""
        hotkey_parts = self.current_hotkey.split('+')

        # Skip checking modifiers if there's only one part
        if len(hotkey_parts) <= 1:
            return True

        # Check if all modifier keys are in the correct state
        for mod in hotkey_parts[:-1]:  # All parts except the last one are modifiers
            if not keyboard.is_pressed(mod):
                return False

        return True
