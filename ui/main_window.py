import customtkinter as ctk
from pynput.keyboard import Controller
import pyperclip
import webbrowser

from ui.ui_helper import UIHelper
from utils.config_manager import ConfigManager
from utils.history_manager import HistoryManager
from utils.audio_recorder import AudioRecorder
from services.transcription_service import TranscriptionService
from utils.hotkey_manager import HotkeyManager
from utils.paste_text_manager import PasteTextManager


class MainApplication:
    """Main application class"""

    def __init__(self):
        # Initialize appearance
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # Create the root window FIRST
        self.root = ctk.CTk()
        self.root.title("Too Lazy to Type")
        self.root.geometry("800x650")

        # NOW initialize variables AFTER creating root window
        self.api_key = ctk.StringVar(self.root)
        self.balance = ctk.StringVar(self.root)
        self.record_hotkey = ctk.StringVar(self.root, value="ctrl+shift")
        self.record_mode = ctk.StringVar(self.root, value="hold")
        self._support_link = "https://www.buymeacoffee.com/TooLazyToType"

        # Initialize managers and services
        self.config_manager = ConfigManager()
        self.history_manager = HistoryManager(self.config_manager)
        self.audio_recorder = AudioRecorder()
        self.transcription_service = TranscriptionService("")
        self.hotkey_manager = HotkeyManager()
        self.keyboard = Controller()
        self.paste_text_manager = PasteTextManager()

        # Initialize tracking variables
        self.recording = False
        self.recording_thread = None
        self.history_items = []

        # Setup UI components
        self._setup_ui()

        # Load configuration
        self._load_config()

        # Setup systray
        self._setup_systray()

        # Set up the hotkey based on current mode
        self._update_hotkey_binding()

        # Set up window close handler
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def run(self):
        """Run the application"""
        self.root.mainloop()

    def _setup_ui(self):
        """Set up the user interface"""
        # Main layout frames
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(side=ctk.RIGHT, fill=ctk.BOTH, expand=True)

        self.config_frame = ctk.CTkFrame(self.root, width=250)
        self.config_frame.pack(side=ctk.LEFT, fill=ctk.Y)

        # App title section
        self._setup_title_section()

        # API Key section
        self._setup_api_section()

        # Recording status section
        self._setup_status_section()

        # Configuration panel
        self._setup_config_section()

        # History section
        self._setup_history_section()

        # Watermark section
        self._setup_watermark_section()

    def _setup_title_section(self):
        """Set up the application title section"""
        title_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        title_frame.pack(pady=20, fill=ctk.X)

        ctk.CTkLabel(
            title_frame,
            text="Too Lazy to Type",
            font=("Roboto", 28, "bold")
        ).pack()

        ctk.CTkLabel(
            title_frame,
            text="Created when I'm too lazy to type.",
            font=("Roboto", 14)
        ).pack()

    def _setup_api_section(self):
        """Set up the API key section"""
        api_frame = ctk.CTkFrame(self.main_frame)
        api_frame.pack(pady=20, padx=30, fill=ctk.X)

        # Improved label with better spacing and font
        ctk.CTkLabel(
            api_frame,
            text="OpenAI API Key:",
            anchor="w",
            font=("Roboto", 14)
        ).pack(pady=(15, 5), padx=15, anchor="w")

        # Improved entry field with more padding and rounded corners
        api_entry = ctk.CTkEntry(
            api_frame,
            textvariable=self.api_key,
            width=350,
            height=38,
            corner_radius=8,
            border_width=2
        )
        api_entry.pack(pady=10, padx=15)

        # Button frame with increased spacing
        button_frame = ctk.CTkFrame(api_frame, fg_color="transparent")
        button_frame.pack(pady=15, fill=ctk.X, padx=15)

        ctk.CTkButton(
            button_frame,
            text="Save API Key",
            command=self._save_config
        ).pack(side=ctk.LEFT, padx=10)

        ctk.CTkButton(
            button_frame,
            text="Check Balance",
            command=self._check_balance
        ).pack(side=ctk.LEFT, padx=10)

    def _setup_status_section(self):
        """Set up the recording status section"""
        status_frame = ctk.CTkFrame(self.main_frame)
        status_frame.pack(pady=15, padx=20, fill=ctk.X)

        self.record_label = ctk.CTkLabel(
            status_frame,
            text="Press hotkey to start recording",
            font=("Roboto", 16)
        )
        self.record_label.pack(pady=15)

        # Status indicator (red/black dot)
        self.status_indicator = ctk.CTkLabel(
            status_frame,
            text="⚫",  # Will change to 🔴 when recording
            font=("Arial", 24),
            text_color="gray"
        )
        self.status_indicator.pack(pady=5)

    def _setup_config_section(self):
        """Set up the configuration section"""
        ctk.CTkLabel(
            self.config_frame,
            text="Configuration",
            font=("Roboto", 18, "bold")
        ).pack(pady=15)

        # Hotkey configuration
        hotkey_frame = ctk.CTkFrame(self.config_frame)
        hotkey_frame.pack(padx=10, pady=5, fill=ctk.X)

        ctk.CTkLabel(hotkey_frame, text="Record Hotkey:",
                     anchor="w").pack(pady=5, padx=10, anchor="w")
        hotkey_entry = ctk.CTkEntry(
            hotkey_frame, textvariable=self.record_hotkey)
        hotkey_entry.pack(padx=10, pady=5, fill=ctk.X)

        ctk.CTkButton(
            hotkey_frame,
            text="Apply Hotkey",
            command=self._update_hotkey_binding
        ).pack(pady=10, padx=10, fill=ctk.X)

        # Record mode configuration
        mode_frame = ctk.CTkFrame(self.config_frame)
        mode_frame.pack(padx=10, pady=10, fill=ctk.X)

        ctk.CTkLabel(mode_frame, text="Record Mode:", anchor="w").pack(
            pady=5, padx=10, anchor="w")
        record_mode_menu = ctk.CTkOptionMenu(
            mode_frame,
            values=["hold", "toggle"],
            variable=self.record_mode,
            command=self._on_record_mode_change
        )
        record_mode_menu.pack(pady=5, padx=10, fill=ctk.X)

        mode_help = ctk.CTkLabel(
            mode_frame,
            text="Hold: Record while pressing hotkey\nToggle: Press once to start/stop",
            justify="left",
            font=("Roboto", 12)
        )
        mode_help.pack(pady=5, padx=10, anchor="w")

    def _setup_history_section(self):
        """Set up the history section"""
        # Create a parent frame to contain both history components
        history_parent_frame = ctk.CTkFrame(self.config_frame)
        history_parent_frame.pack(padx=10, pady=5, fill=ctk.BOTH, expand=True)

        # History section label (in the parent frame)
        ctk.CTkLabel(
            history_parent_frame,
            text="Transcription History",
            font=("Roboto", 18, "bold")
        ).pack(pady=7)

        # Create a frame to contain history items (in the parent frame)
        self.history_container = ctk.CTkFrame(history_parent_frame)
        self.history_container.pack(padx=0, pady=3, fill=ctk.BOTH, expand=True)

        # Create a scrollable frame with FIXED HEIGHT for history items
        self.history_scroll = ctk.CTkScrollableFrame(
            self.history_container, height=100, width=220)
        self.history_scroll.pack(fill=ctk.BOTH, expand=True)

        # History controls (in the parent frame AFTER the container)
        history_ctrl_frame = ctk.CTkFrame(
            history_parent_frame, fg_color="transparent")
        history_ctrl_frame.pack(pady=3, fill=ctk.X)

        # The Clear History button is now in the history_parent_frame
        self.clear_history_btn = ctk.CTkButton(
            history_ctrl_frame,
            text="Clear History",
            command=self._clear_history,
            fg_color="#d32f2f",
            hover_color="#b71c1c"
        )
        self.clear_history_btn.pack(pady=10, fill=ctk.X)

    def _setup_watermark_section(self):
        """Set up the watermark section"""
        watermark_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        watermark_frame.pack(side=ctk.BOTTOM, pady=5, fill=ctk.X)

        ctk.CTkLabel(
            watermark_frame,
            text="Made with 🚬 by",
            font=("Roboto", 14, "bold")
        ).pack(pady=(0, 2))

        def open_github_profile():
            webbrowser.open("https://github.com/rivalarya")

        ctk.CTkButton(
            watermark_frame,
            text="rivalarya",
            command=open_github_profile,
            hover_color="black"
        ).pack(pady=(0, 10))

    def _setup_systray(self):
        """Set up system tray functionality"""
        self.systray_menu = ctk.CTkToplevel(self.root)
        self.systray_menu.geometry("200x100")
        self.systray_menu.withdraw()

        ctk.CTkLabel(
            self.systray_menu, text="Whisper AI is running in the background").pack(pady=10)
        ctk.CTkButton(self.systray_menu, text="Open",
                      command=self._show_window).pack(pady=5)
        ctk.CTkButton(self.systray_menu, text="Exit",
                      command=self._on_close).pack(pady=5)

    def _on_record_mode_change(self, _=None):
        """Handle record mode change"""
        self._update_hotkey_binding()

    def _update_hotkey_binding(self):
        """Update hotkey binding based on current settings"""
        self.hotkey_manager.set_hotkey(
            self.record_hotkey.get(),
            self.record_mode.get(),
            self._on_hotkey_press,  # No event parameter needed now
            self._on_hotkey_release if self.record_mode.get() == "hold" else None
        )

    def _on_hotkey_press(self):
        """Handle hotkey press event - no event parameter needed"""
        if self.record_mode.get() == "hold":
            self._start_recording()
        else:
            self._toggle_recording()

    def _on_hotkey_release(self):
        """Handle hotkey release event - no event parameter needed"""
        if self.record_mode.get() == "hold" and self.recording:
            self._stop_recording()

    def _toggle_recording(self):
        """Toggle recording state"""
        if not self.recording:
            self._start_recording()
        else:
            self._stop_recording()

    def _start_recording(self):
        """Start recording audio"""
        if not self.recording:
            self.recording = True
            self.record_label.configure(text="Recording in progress...")
            self.status_indicator.configure(text="🔴", text_color="#d32f2f")
            self.recording_thread = self.audio_recorder.start_recording()

    def _stop_recording(self):
        """Stop recording audio"""
        if self.recording:
            self.recording = False
            self.record_label.configure(text="Press hotkey to start recording")
            self.status_indicator.configure(text="⚫", text_color="gray")

            # Stop recording and process the audio
            self.audio_recorder.stop_recording()
            if self.recording_thread:
                self.recording_thread.join()

            # Save and transcribe the audio
            filename = self.audio_recorder.save_audio()
            if filename:
                self._transcribe_audio(filename)

    def _transcribe_audio(self, filename):
        """Transcribe recorded audio file"""
        try:
            # Get the selected model from config
            config = self.config_manager.load_config()
            selected_model = config.get("stt_model", "whisper-1")

            # Set the API key and transcribe
            self.transcription_service.set_api_key(self.api_key.get())
            transcription_text = self.transcription_service.transcribe(
                filename, selected_model)

            # Add to history and update display
            self.history_manager.add_entry(transcription_text)
            self._update_history_display()

            # Paste the text into the active application
            self._paste_text(transcription_text)

        except Exception as api_error:
            error_str = str(api_error)
            if "401" in error_str and "invalid_api_key" in error_str:
                self._show_api_key_error(
                    "Your OpenAI API key appears to be invalid. Please check your API key.")
            else:
                self._show_error_window(f"API Error: {error_str}")

    def _paste_text(self, text):
        self.paste_text_manager.paste_text(text)

    def _update_history_display(self):
        """Update the history display"""
        # Clear existing history items
        for item in self.history_items:
            item.destroy()
        self.history_items = []

        if not self.history_manager.history:
            no_history_label = ctk.CTkLabel(
                self.history_scroll, text="No transcriptions yet.")
            no_history_label.pack(pady=10)
            self.history_items.append(no_history_label)
            return

        # Add each history item with its own frame and copy button
        for i, entry in enumerate(self.history_manager.history):
            # Create a frame for this history item
            item_frame = ctk.CTkFrame(self.history_scroll)
            item_frame.pack(fill=ctk.X, padx=5, pady=2, expand=True)
            self.history_items.append(item_frame)

            # Format the display text (truncate if needed)
            max_display_chars = 30
            display_text = entry[:max_display_chars] + \
                "..." if len(entry) > max_display_chars else entry

            # Capture the current entry for the lambda
            current_entry = entry

            # Add copy button first (on the right)
            copy_btn = ctk.CTkButton(
                item_frame,
                text="Copy",
                width=60,
                height=25,
                command=lambda text=current_entry: self._copy_to_clipboard(
                    text)
            )
            # Pack button to the right
            copy_btn.pack(side=ctk.RIGHT, padx=5, pady=5)
            self.history_items.append(copy_btn)

            # Add the text label
            text_label = ctk.CTkLabel(
                item_frame,
                text=display_text,
                anchor="w",
                justify="left",
                cursor="hand2"  # Hand cursor to indicate clickable
            )
            text_label.pack(side=ctk.LEFT, fill=ctk.X,
                            expand=True, padx=5, pady=5)
            self.history_items.append(text_label)

            # Bind click event to the text label
            text_label.bind("<Button-1>", lambda e,
                            text=current_entry: self._show_full_text(text))

    def _clear_history(self):
        """Clear all history items"""
        UIHelper.show_confirmation(
            self.root,
            "Are you sure you want to clear all history?",
            on_confirm=lambda: (
                self.history_manager.clear_history(),
                self._update_history_display()
            )
        )

    def _copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        pyperclip.copy(text)
        UIHelper.show_notification(self.root, "Copied to clipboard!")

    def _show_full_text(self, text):
        """Show the full text of a history item"""
        details_window = UIHelper.create_modal_window(
            self.root, "Transcription Details", "500x300")

        # Text area with scrollbar
        text_box = ctk.CTkTextbox(details_window, wrap="word")
        text_box.pack(padx=10, pady=10, fill=ctk.BOTH, expand=True)
        text_box.insert("0.0", text)
        text_box.configure(state="disabled")  # Make it read-only

        # Button frame
        btn_frame = ctk.CTkFrame(details_window, fg_color="transparent")
        btn_frame.pack(pady=10, padx=10, fill=ctk.X)

        # Copy button
        ctk.CTkButton(
            btn_frame,
            text="Copy Text",
            command=lambda: self._copy_to_clipboard(text)
        ).pack(side=ctk.LEFT, padx=5)

        # Close button
        ctk.CTkButton(
            btn_frame,
            text="Close",
            command=details_window.destroy
        ).pack(side=ctk.RIGHT, padx=5)

    def _check_balance(self):
        """Check API balance"""
        info_window = UIHelper.create_modal_window(
            self.root, "Balance Information", "400x200")

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

    def _show_error_window(self, message):
        """Show error message"""
        UIHelper.show_error(self.root, message)

    def _show_api_key_error(self, message):
        """Show API key error with help information"""
        error_window = UIHelper.create_modal_window(
            self.root, "API Key Error", "450x250")

        # Error icon frame
        icon_frame = ctk.CTkFrame(error_window, fg_color="transparent")
        icon_frame.pack(pady=(15, 5))

        # Error symbol (using text as we don't have images)
        error_symbol = ctk.CTkLabel(
            icon_frame,
            text="🔑",
            font=("Arial", 32)
        )
        error_symbol.pack()

        # Error message with wrapping
        ctk.CTkLabel(
            error_window,
            text=message,
            wraplength=400,
            font=("Arial", 12, "bold")
        ).pack(padx=20, pady=10)

        # Help text
        ctk.CTkLabel(
            error_window,
            text="You can find or create your API key at:",
            font=("Arial", 12)
        ).pack(pady=(5, 0))

        # URL text (styled to look like a link)
        url_label = ctk.CTkLabel(
            error_window,
            text="https://platform.openai.com/account/api-keys",
            font=("Arial", 12, "underline"),
            text_color="#3a86ff",
            cursor="hand2"
        )
        url_label.pack(pady=(0, 10))

        # Bind click event to open the URL
        url_label.bind(
            "<Button-1>", lambda e: webbrowser.open("https://platform.openai.com/account/api-keys"))

        # Buttons frame
        btn_frame = ctk.CTkFrame(error_window, fg_color="transparent")
        btn_frame.pack(pady=5, fill=ctk.X)

        # Button layout
        open_button = ctk.CTkButton(
            btn_frame,
            text="Open API Keys Page",
            command=lambda: webbrowser.open(
                "https://platform.openai.com/account/api-keys"),
            width=150
        )
        open_button.pack(side=ctk.LEFT, padx=20)

        ok_button = ctk.CTkButton(
            btn_frame,
            text="OK",
            command=error_window.destroy,
            width=100
        )
        ok_button.pack(side=ctk.RIGHT, padx=20)

    def _show_window(self):
        """Show the main window"""
        self.root.deiconify()
        self.systray_menu.withdraw()

    def _load_config(self):
        """Load configuration from file"""
        config = self.config_manager.load_config()
        self.api_key.set(config.get("api_key", ""))
        self.record_hotkey.set(config.get("record_hotkey", "ctrl+shift"))
        self.record_mode.set(config.get("record_mode", "hold"))
        self._update_history_display()

    def _save_config(self):
        """Save configuration to file"""
        config = self.config_manager.load_config()
        config["api_key"] = self.api_key.get()
        config["record_hotkey"] = self.record_hotkey.get()
        config["record_mode"] = self.record_mode.get()
        self.config_manager.save_config(config)

        # Update the API key in the transcription service
        self.transcription_service.set_api_key(self.api_key.get())

        # Show confirmation
        UIHelper.show_notification(self.root, "Settings saved!")

    def _on_close(self):
        """Handle window close event"""
        self._save_config()
        self.root.quit()
