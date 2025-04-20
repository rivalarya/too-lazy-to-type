import customtkinter as ctk
from pynput.keyboard import Controller
import pyperclip
import webbrowser
import threading

from ui.ui_helper import UIHelper
from ui.configuration_window import ConfigurationWindow
from utils.config_manager import ConfigManager
from utils.history_manager import HistoryManager
from utils.audio_recorder import AudioRecorder
from services.transcription_service import TranscriptionService
from utils.hotkey_manager import HotkeyManager
from utils.paste_text_manager import PasteTextManager
from ui.minimized_main_window import MinimizedMainWindow


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

        # Initialize managers and services
        self.config_manager = ConfigManager()
        self.history_manager = HistoryManager(self.config_manager)
        self.audio_recorder = AudioRecorder()
        self.transcription_service = TranscriptionService("")
        self.hotkey_manager = HotkeyManager()
        self.keyboard = Controller()
        self.paste_text_manager = PasteTextManager()

        # Load configuration
        self.config = self.config_manager.load_config()

        # Initialize tracking variables
        self.recording = False
        self.transcribing = False
        self.recording_thread = None
        self.history_items = []

        # Create the configuration window (not shown yet)
        self.config_window = ConfigurationWindow(
            self.root,
            self.config_manager,
            self.hotkey_manager,
            on_config_save=self._on_config_saved
        )

        # Create the minimized window (initially hidden)
        self.minimized_window = MinimizedMainWindow(
            self.root,
            on_open_main=self._show_window,
            on_close=self._on_minimized_window_close
        )

        # Setup UI components
        self._setup_ui()

        # Set up the hotkey based on current mode
        self._update_hotkey_binding()

        # Set up window close handler
        self.root.protocol("WM_DELETE_WINDOW", self._minimize_to_small_window)

        # Determine which window to show at startup
        self.root.after(100, self._handle_startup_window)

    def _handle_startup_window(self):
        """Determine which window to show at startup based on configuration"""
        if self.config.get("start_minimized", False):
            self.root.withdraw()
            self.minimized_window.show()
        # Otherwise the main window stays visible (default behavior)

    def run(self):
        """Run the application"""
        self.root.mainloop()

    def _setup_ui(self):
        """Set up the user interface"""
        # Main layout frames
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(side=ctk.RIGHT, fill=ctk.BOTH, expand=True)

        self.sidebar_frame = ctk.CTkFrame(self.root, width=250)
        self.sidebar_frame.pack(side=ctk.LEFT, fill=ctk.Y)

        # App title section
        self._setup_title_section()

        # Recording status section
        self._setup_status_section()

        # Sidebar sections
        self._setup_sidebar()

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

    def _setup_status_section(self):
        """Set up the recording status section"""
        status_frame = ctk.CTkFrame(self.main_frame)
        status_frame.pack(pady=15, padx=20, fill=ctk.X)

        # API key status
        api_status_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
        api_status_frame.pack(pady=10, fill=ctk.X)

        api_status_text = "API Key: " + \
            ("Configured ✓" if self.config.get("api_key") else "Not configured ✗")
        api_status_color = "#4CAF50" if self.config.get(
            "api_key") else "#FF5252"

        self.api_status_label = ctk.CTkLabel(
            api_status_frame,
            text=api_status_text,
            font=("Roboto", 14),
            text_color=api_status_color
        )
        self.api_status_label.pack(side=ctk.LEFT, padx=15)

        config_btn = ctk.CTkButton(
            api_status_frame,
            text="Open Settings",
            command=self._open_config_window,
            width=120
        )
        config_btn.pack(side=ctk.RIGHT, padx=15)

        # Separator
        separator = ctk.CTkFrame(status_frame, height=1, fg_color="#6c757d")
        separator.pack(fill=ctk.X, padx=15, pady=10)

        # Recording status
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

        # Hotkey reminder
        self.hotkey_reminder = ctk.CTkLabel(
            status_frame,
            text=f"Current hotkey: {self.config.get('record_hotkey', 'ctrl+shift')}",
            font=("Roboto", 13),
            text_color="#6c757d"
        )
        self.hotkey_reminder.pack(pady=(0, 10))

        # Transcription status label
        self.transcription_status = ctk.CTkLabel(
            status_frame,
            text="",
            font=("Roboto", 14),
            text_color="#3a86ff"
        )
        self.transcription_status.pack(pady=5)

    def _setup_sidebar(self):
        """Set up the sidebar"""
        # Sidebar title
        ctk.CTkLabel(
            self.sidebar_frame,
            text="Menu",
            font=("Roboto", 18, "bold")
        ).pack(pady=15)

        # History section - moved to top
        self._setup_history_section()

        # Spacer - smaller now
        small_spacer = ctk.CTkFrame(
            self.sidebar_frame, fg_color="transparent", height=10)
        small_spacer.pack(pady=5)

        # Sidebar buttons
        self._create_sidebar_button(
            "Settings",
            self._open_config_window,
            "⚙️"
        )

        self._create_sidebar_button(
            "Minimize",
            self._minimize_to_small_window,
            "🔽"
        )

        self._create_sidebar_button(
            "About",
            self._show_about,
            "ℹ️"
        )

        # Spacer frame to push exit button to bottom
        spacer = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        spacer.pack(fill=ctk.BOTH, expand=True)

        # Exit button at bottom
        exit_btn = ctk.CTkButton(
            self.sidebar_frame,
            text="Exit Application",
            command=self._confirm_exit,
            fg_color="#d32f2f",
            hover_color="#b71c1c",
            height=40
        )
        exit_btn.pack(pady=15, padx=20, fill=ctk.X)

    def _create_sidebar_button(self, text, command, icon="", state="normal"):
        """Create a standardized sidebar button"""
        btn_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        btn_frame.pack(fill=ctk.X, pady=5, padx=20)

        button = ctk.CTkButton(
            btn_frame,
            text=f"{icon} {text}" if icon else text,
            command=command,
            anchor="w",
            height=40,
            corner_radius=8,
            state=state
        )
        button.pack(fill=ctk.X)

        return button

    def _setup_history_section(self):
        """Set up the history section with improved scrolling"""
        # Create a parent frame to contain both history components
        history_parent_frame = ctk.CTkFrame(self.sidebar_frame)
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
        # Add mousewheel configuration for smoother scrolling
        self.history_scroll = ctk.CTkScrollableFrame(
            self.history_container, height=200, width=220)
        self.history_scroll.pack(fill=ctk.BOTH, expand=True)

        # History controls
        history_ctrl_frame = ctk.CTkFrame(
            history_parent_frame, fg_color="transparent")
        history_ctrl_frame.pack(pady=3, fill=ctk.X)

        # Clear History button
        self.clear_history_btn = ctk.CTkButton(
            history_ctrl_frame,
            text="Clear History",
            command=self._clear_history,
            fg_color="#d32f2f",
            hover_color="#b71c1c"
        )
        self.clear_history_btn.pack(pady=10, fill=ctk.X)

        # Update the history display
        self._update_history_display()

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

    def _open_config_window(self):
        """Open the configuration window"""
        self.config_window.show()

    def _on_config_saved(self):
        """Handle configuration save event"""
        # Reload configuration
        self.config = self.config_manager.load_config()

        # Update API key in transcription service
        self.transcription_service.set_api_key(self.config.get("api_key", ""))

        # Update hotkey binding
        self._update_hotkey_binding()

        # Update UI elements that display configuration values
        self._update_config_display()

    def _update_config_display(self):
        """Update UI elements that display configuration values"""
        # Update API status in the main window
        api_status_text = "API Key: " + \
            ("Configured ✓" if self.config.get("api_key") else "Not configured ✗")
        api_status_color = "#4CAF50" if self.config.get(
            "api_key") else "#FF5252"

        # Use direct references to UI elements
        if hasattr(self, 'api_status_label'):
            self.api_status_label.configure(
                text=api_status_text, text_color=api_status_color)

        if hasattr(self, 'hotkey_reminder'):
            self.hotkey_reminder.configure(
                text=f"Current hotkey: {self.config.get('record_hotkey', 'ctrl+shift')}")

    def _update_hotkey_binding(self):
        """Update hotkey binding based on current settings"""
        self.hotkey_manager.set_hotkey(
            self.config.get("record_hotkey", "ctrl+shift"),
            self.config.get("record_mode", "hold"),
            self._on_hotkey_press,
            self._on_hotkey_release if self.config.get(
                "record_mode", "hold") == "hold" else None
        )

    def _on_hotkey_press(self):
        """Handle hotkey press event - no event parameter needed"""
        if self.config.get("record_mode", "hold") == "hold":
            self._start_recording()
        else:
            self._toggle_recording()

    def _on_hotkey_release(self):
        """Handle hotkey release event - no event parameter needed"""
        if self.config.get("record_mode", "hold") == "hold" and self.recording:
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
            # Update main window status
            self.record_label.configure(text="Recording in progress...")
            self.status_indicator.configure(text="🔴", text_color="#d32f2f")

            # Update minimized window status
            self.minimized_window.update_recording_status(True)

            self.recording_thread = self.audio_recorder.start_recording()

    def _stop_recording(self):
        """Stop recording audio"""
        if self.recording:
            self.recording = False
            # Update main window status
            self.record_label.configure(text="Press hotkey to start recording")
            self.status_indicator.configure(text="⚫", text_color="gray")

            # Update minimized window status
            self.minimized_window.update_recording_status(False)

            # Stop recording and process the audio
            self.audio_recorder.stop_recording()
            if self.recording_thread:
                self.recording_thread.join()

            # Save and transcribe the audio
            filename = self.audio_recorder.save_audio()
            if filename:
                # Show transcribing status
                self.transcribing = True
                self.transcription_status.configure(
                    text="Transcribing... Please wait")

                # Update minimized window status
                self.minimized_window.update_transcription_status(True)

                # Start transcription in a separate thread
                threading.Thread(target=self._transcribe_audio_thread, args=(
                    filename,), daemon=True).start()

    def _transcribe_audio_thread(self, filename):
        """Transcribe audio in a separate thread to keep UI responsive"""
        try:
            # Get the selected model from config
            selected_model = self.config.get("stt_model", "whisper-1")

            # Set the API key and transcribe
            self.transcription_service.set_api_key(
                self.config.get("api_key", ""))
            transcription_text = self.transcription_service.transcribe(
                filename, selected_model)

            # Use after() to update UI from the main thread
            self.root.after(
                0, lambda: self._handle_transcription_result(transcription_text))

        except Exception as api_error:
            error_str = str(api_error)
            # Use after() to show error from the main thread
            if "401" in error_str and "invalid_api_key" in error_str:
                self.root.after(0, lambda: self._show_api_key_error(
                    "Your OpenAI API key appears to be invalid. Please check your API key."))
            else:
                self.root.after(0, lambda: self._show_error_window(
                    f"API Error: {error_str}"))

            # Clear transcribing status
            self.root.after(0, self._clear_transcription_status)

    def _handle_transcription_result(self, transcription_text):
        """Handle successful transcription result"""
        # Add to history and update display
        self.history_manager.add_entry(transcription_text)
        self._update_history_display()

        # Paste the text into the active application
        self._paste_text(transcription_text)

        # Clear transcribing status
        self._clear_transcription_status()

    def _clear_transcription_status(self):
        """Clear the transcription status message"""
        self.transcribing = False
        self.transcription_status.configure(text="")

        # Update minimized window status
        self.minimized_window.update_transcription_status(False)

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

    def _show_about(self):
        """Show about dialog"""
        about_window = UIHelper.create_modal_window(
            self.root, "About Too Lazy to Type", "400x300")

        # App logo
        logo_frame = ctk.CTkFrame(about_window, fg_color="transparent")
        logo_frame.pack(pady=(15, 5))

        logo_text = ctk.CTkLabel(
            logo_frame,
            text="Too Lazy to Type",
            font=("Arial", 24, "bold"),
            text_color="#3a86ff"
        )
        logo_text.pack()

        # Version
        ctk.CTkLabel(
            about_window,
            text="Version 1.1.0",
            font=("Roboto", 14)
        ).pack(pady=(0, 10))

        # Description
        ctk.CTkLabel(
            about_window,
            text="A simple speech-to-text application for when you're\ntoo lazy to type. Just press the hotkey and speak!",
            wraplength=350
        ).pack(pady=5)

        # Creator info
        ctk.CTkLabel(
            about_window,
            text="Created by rivalarya",
            font=("Roboto", 12)
        ).pack(pady=(10, 0))

        # GitHub link
        github_btn = ctk.CTkButton(
            about_window,
            text="Visit GitHub Repository",
            command=lambda: webbrowser.open(
                "https://github.com/rivalarya/too-lazy-to-type")
        )
        github_btn.pack(pady=10)

        # Close button
        ctk.CTkButton(
            about_window,
            text="Close",
            command=about_window.destroy
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

        open_config_button = ctk.CTkButton(
            btn_frame,
            text="Open Settings",
            command=lambda: (error_window.destroy(),
                             self._open_config_window()),
            width=120
        )
        open_config_button.pack(side=ctk.LEFT, padx=5)

        ok_button = ctk.CTkButton(
            btn_frame,
            text="OK",
            command=error_window.destroy,
            width=80
        )
        ok_button.pack(side=ctk.RIGHT, padx=20)

    def _confirm_exit(self):
        """Confirm before exiting the application"""
        UIHelper.show_confirmation(
            self.root,
            "Are you sure you want to exit the application?",
            on_confirm=self._on_close
        )

    def _show_window(self):
        """Show the main window"""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

        # Hide the minimized window
        self.minimized_window.hide()

    def _minimize_to_small_window(self):
        """Minimize the application to small status window"""
        self.config_manager.save_config(self.config)
        self.root.withdraw()

        # Show the minimized window and update its status
        self.minimized_window.update_recording_status(self.recording)
        self.minimized_window.update_transcription_status(
            self.transcribing,
            "Transcribing... Please wait" if self.transcribing else ""
        )
        self.minimized_window.show()

    def _on_minimized_window_close(self):
        """Handle minimized window close"""
        # Show a confirmation dialog
        UIHelper.show_confirmation(
            self.minimized_window.window,
            "Do you want to exit the application?",
            on_confirm=self._on_close,
            on_cancel=lambda: self.minimized_window.show()
        )

    def _on_close(self):
        """Handle window close event - fully exit the application"""
        self.config_manager.save_config(self.config)
        self.root.quit()
