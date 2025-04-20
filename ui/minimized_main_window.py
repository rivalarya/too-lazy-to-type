import customtkinter as ctk


class MinimizedMainWindow:
    """Minimized window that shows recording status"""

    def __init__(self, master, on_open_main=None, on_close=None):
        """
        Initialize the minimized window

        Args:
            master: The parent/master window
            on_open_main: Callback function when "Open Main Window" button is clicked
            on_close: Callback function when the window is closed
        """
        self.master = master
        self.on_open_main_callback = on_open_main
        self.on_close_callback = on_close

        # Create the window
        self.window = ctk.CTkToplevel(master)
        self.window.title("Too Lazy to Type - Status")
        self.window.geometry("300x180")
        self.window.resizable(False, False)
        self.window.withdraw()  # Hide initially

        # Configure the window to always stay on top
        self.window.attributes("-topmost", True)

        # Build the UI
        self._setup_ui()

        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self._on_window_close)

    def _setup_ui(self):
        """Set up the user interface"""
        # Main frame with lighter color for better visibility
        self.main_frame = ctk.CTkFrame(self.window)
        self.main_frame.pack(padx=10, pady=10, fill=ctk.BOTH, expand=True)

        # App title
        title_label = ctk.CTkLabel(
            self.main_frame,
            text="Too Lazy to Type",
            font=("Roboto", 16, "bold")
        )
        title_label.pack(pady=(10, 15))

        # Recording status container (with circle and text)
        status_container = ctk.CTkFrame(
            self.main_frame, fg_color="transparent")
        status_container.pack(fill=ctk.X, pady=5)

        # Status indicator (circle)
        self.status_indicator = ctk.CTkLabel(
            status_container,
            text="⚫",  # Will change to 🔴 when recording
            font=("Arial", 24),  # Increased size
            text_color="gray"
        )
        self.status_indicator.pack(side=ctk.LEFT, padx=(80, 10))

        # Status text
        self.status_text = ctk.CTkLabel(
            status_container,
            text="Not Recording",
            font=("Roboto", 14)
        )
        self.status_text.pack(side=ctk.LEFT)

        # Transcription status
        self.transcription_status = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=("Roboto", 12),
            text_color="#3a86ff"
        )
        self.transcription_status.pack(pady=5)

        self.open_button = ctk.CTkButton(
            self.main_frame,
            text="Open Main Window",
            command=self._on_open_main,
            width=220,
            height=35,
            corner_radius=8,
            font=("Roboto", 13)
        )
        self.open_button.pack(pady=(0, 5))

    def show(self):
        """Show the minimized window"""
        self.window.deiconify()
        self.window.lift()

        self.window.update_idletasks()

    def hide(self):
        """Hide the minimized window"""
        self.window.withdraw()

    def update_recording_status(self, is_recording):
        """
        Update the recording status display

        Args:
            is_recording: Boolean indicating if recording is in progress
        """
        if is_recording:
            self.status_indicator.configure(text="🔴", text_color="#d32f2f")
            self.status_text.configure(text="Recording")
        else:
            self.status_indicator.configure(text="⚫", text_color="gray")
            self.status_text.configure(text="Not Recording")

    def update_transcription_status(self, is_transcribing, message=""):
        """
        Update the transcription status display

        Args:
            is_transcribing: Boolean indicating if transcription is in progress
            message: Optional status message to display
        """
        if is_transcribing:
            self.transcription_status.configure(
                text=message if message else "Transcribing... Please wait"
            )
        else:
            self.transcription_status.configure(text="")

    def _on_open_main(self):
        """Handle the Open Main Window button click"""
        if self.on_open_main_callback:
            self.on_open_main_callback()

    def _on_window_close(self):
        """Handle the window close event"""
        if self.on_close_callback:
            self.on_close_callback()
