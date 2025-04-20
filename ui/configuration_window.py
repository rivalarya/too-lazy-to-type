import customtkinter as ctk
import webbrowser

from ui.ui_helper import UIHelper


class ConfigurationWindow:
    """Configuration window for the application"""

    def __init__(self, master, config_manager, hotkey_manager, on_config_save=None):
        """
        Initialize the configuration window

        Args:
            master: The parent/master window
            config_manager: The configuration manager instance
            hotkey_manager: The hotkey manager instance
            on_config_save: Callback function when configuration is saved
        """
        self.master = master
        self.config_manager = config_manager
        self.hotkey_manager = hotkey_manager
        self.on_config_save_callback = on_config_save

        # Load current configuration
        self.config = self.config_manager.load_config()

        # Create window variables
        self.window = None
        self.api_key = ctk.StringVar()
        self.record_hotkey = ctk.StringVar()
        self.record_mode = ctk.StringVar()
        self.start_minimized = ctk.BooleanVar()

        # Set default values
        self.api_key.set(self.config.get("api_key", ""))
        self.record_hotkey.set(self.config.get("record_hotkey", "ctrl+shift"))
        self.record_mode.set(self.config.get("record_mode", "hold"))
        self.start_minimized.set(self.config.get("start_minimized", False))

    def show(self):
        """Show the configuration window"""
        if self.window is not None:
            self.window.destroy()

        # Create the window
        self.window = ctk.CTkToplevel(self.master)
        self.window.title("Too Lazy to Type - Configuration")
        self.window.geometry("500x600")
        self.window.resizable(True, True)

        # Make it modal
        self.window.transient(self.master)
        self.window.grab_set()

        # Setup UI
        self._setup_ui()

        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self.window.destroy)

        # Focus the window
        self.window.focus_set()

    def _setup_ui(self):
        """Set up the configuration user interface"""
        # Main container
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(padx=20, pady=20, fill=ctk.BOTH, expand=True)

        # Title
        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(fill=ctk.X, pady=(0, 20))

        ctk.CTkLabel(
            title_frame,
            text="Application Configuration",
            font=("Roboto", 22, "bold")
        ).pack()

        # Create scrollable frame for all settings
        settings_frame = ctk.CTkScrollableFrame(main_frame)
        settings_frame.pack(fill=ctk.BOTH, expand=True, padx=5, pady=5)

        # API Key section
        self._setup_api_section(settings_frame)

        # Recording configuration
        self._setup_recording_section(settings_frame)

        # Startup configuration
        self._setup_startup_section(settings_frame)

        # Advanced options
        # self._setup_advanced_section(settings_frame)

        # Buttons frame
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill=ctk.X, pady=(20, 0))

        ctk.CTkButton(
            buttons_frame,
            text="Save Configuration",
            command=self._save_config,
            width=200,
            height=40,
            corner_radius=8,
            font=("Roboto", 14)
        ).pack(side=ctk.LEFT, padx=5)

        ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            command=self.window.destroy,
            width=100,
            height=40,
            corner_radius=8,
            fg_color="#6c757d",
            hover_color="#495057",
            font=("Roboto", 14)
        ).pack(side=ctk.RIGHT, padx=5)

    def _setup_api_section(self, parent):
        """Set up the API key section"""
        section_frame = self._create_section_frame(
            parent, "OpenAI API Configuration")

        # API Key entry
        ctk.CTkLabel(
            section_frame,
            text="API Key:",
            anchor="w",
            font=("Roboto", 14)
        ).pack(pady=(10, 5), padx=10, anchor="w")

        api_entry = ctk.CTkEntry(
            section_frame,
            textvariable=self.api_key,
            width=400,
            height=38,
            corner_radius=8,
            border_width=2,
            placeholder_text="Enter your OpenAI API key here"
        )
        api_entry.pack(pady=5, padx=10, fill=ctk.X)

        ctk.CTkLabel(
            section_frame,
            text="Your API key is needed for the speech-to-text functionality.",
            font=("Roboto", 12),
            text_color="#6c757d"
        ).pack(pady=(0, 5), padx=10, anchor="w")

        # API key link
        link_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        link_frame.pack(fill=ctk.X, padx=10, pady=(0, 10))

        get_api_btn = ctk.CTkButton(
            link_frame,
            text="Get API Key",
            command=lambda: webbrowser.open(
                "https://platform.openai.com/account/api-keys"),
            width=150,
            fg_color="#6c757d",
            hover_color="#495057"
        )
        get_api_btn.pack(side=ctk.LEFT)

        check_balance_btn = ctk.CTkButton(
            link_frame,
            text="Check Balance",
            command=self._check_balance,
            width=150,
            fg_color="#6c757d",
            hover_color="#495057"
        )
        check_balance_btn.pack(side=ctk.LEFT, padx=10)

    def _setup_recording_section(self, parent):
        """Set up the recording configuration section"""
        section_frame = self._create_section_frame(
            parent, "Recording Configuration")

        # Hotkey configuration
        ctk.CTkLabel(
            section_frame,
            text="Record Hotkey:",
            anchor="w",
            font=("Roboto", 14)
        ).pack(pady=(10, 5), padx=10, anchor="w")

        hotkey_entry = ctk.CTkEntry(
            section_frame,
            textvariable=self.record_hotkey,
            width=400,
            height=38,
            corner_radius=8,
            border_width=2,
            placeholder_text="e.g., ctrl+shift"
        )
        hotkey_entry.pack(pady=5, padx=10, fill=ctk.X)

        ctk.CTkLabel(
            section_frame,
            text="Use keyboard combinations like 'ctrl+shift', 'alt+r', etc.",
            font=("Roboto", 12),
            text_color="#6c757d"
        ).pack(pady=(0, 15), padx=10, anchor="w")

        # Record mode configuration
        ctk.CTkLabel(
            section_frame,
            text="Recording Mode:",
            anchor="w",
            font=("Roboto", 14)
        ).pack(pady=(5, 5), padx=10, anchor="w")

        mode_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        mode_frame.pack(fill=ctk.X, padx=10, pady=5)

        record_mode_menu = ctk.CTkOptionMenu(
            mode_frame,
            values=["hold", "toggle"],
            variable=self.record_mode,
            width=150,
            height=35,
            corner_radius=8
        )
        record_mode_menu.pack(side=ctk.LEFT)

        # Mode description
        ctk.CTkLabel(
            section_frame,
            text="Hold: Record while pressing hotkey\nToggle: Press once to start/stop",
            justify="left",
            font=("Roboto", 12),
            text_color="#6c757d"
        ).pack(pady=(0, 10), padx=10, anchor="w")

    def _setup_startup_section(self, parent):
        """Set up the startup configuration section"""
        section_frame = self._create_section_frame(
            parent, "Startup Configuration")

        # Startup mode
        ctk.CTkLabel(
            section_frame,
            text="Startup Mode:",
            anchor="w",
            font=("Roboto", 14)
        ).pack(pady=(10, 5), padx=10, anchor="w")

        startup_checkbox = ctk.CTkCheckBox(
            section_frame,
            text="Start application in minimized mode",
            variable=self.start_minimized,
            onvalue=True,
            offvalue=False,
            corner_radius=6,
            height=30,
            font=("Roboto", 13)
        )
        startup_checkbox.pack(pady=5, padx=10, anchor="w")

        ctk.CTkLabel(
            section_frame,
            text="When checked, the application will start in a minimized state\ninstead of showing the full window at startup.",
            justify="left",
            font=("Roboto", 12),
            text_color="#6c757d"
        ).pack(pady=(0, 10), padx=10, anchor="w")

    def _create_section_frame(self, parent, title):
        """Create a framed section with title"""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill=ctk.X, padx=0, pady=10, ipady=5)

        # Section title
        ctk.CTkLabel(
            frame,
            text=title,
            font=("Roboto", 16, "bold"),
            anchor="w"
        ).pack(fill=ctk.X, padx=10, pady=(10, 5))

        # Separator
        separator = ctk.CTkFrame(frame, height=2, fg_color="#6c757d")
        separator.pack(fill=ctk.X, padx=10, pady=(0, 10))

        return frame

    def _save_config(self):
        """Save configuration and close the window"""
        # Get the current configuration
        self.config = self.config_manager.load_config()

        # Update with new values
        self.config["api_key"] = self.api_key.get()
        self.config["record_hotkey"] = self.record_hotkey.get()
        self.config["record_mode"] = self.record_mode.get()
        self.config["start_minimized"] = self.start_minimized.get()

        # Save to file
        self.config_manager.save_config(self.config)

        # Call the callback if provided
        if self.on_config_save_callback:
            self.on_config_save_callback()

        # Show confirmation
        UIHelper.show_notification(self.master, "Settings saved successfully!")

        # Close the window
        self.window.destroy()

    def _check_balance(self):
        """Show OpenAI balance information"""
        info_window = UIHelper.create_modal_window(
            self.window, "Balance Information", "400x200")

        ctk.CTkLabel(
            info_window,
            text="The OpenAI balance information can only be accessed through a browser.",
            wraplength=350
        ).pack(pady=10)

        ctk.CTkLabel(
            info_window,
            text="Please visit the OpenAI dashboard to check your current balance."
        ).pack(pady=5)

        def open_dashboard():
            webbrowser.open("https://platform.openai.com/account/usage")
            info_window.destroy()

        ctk.CTkButton(
            info_window,
            text="Open Dashboard",
            command=open_dashboard
        ).pack(pady=10)

        ctk.CTkButton(
            info_window,
            text="Close",
            command=info_window.destroy
        ).pack(pady=5)
