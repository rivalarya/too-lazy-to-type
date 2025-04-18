import customtkinter as ctk


class UIHelper:
    """Helper class for common UI operations"""

    @staticmethod
    def create_modal_window(parent, title, size="400x200"):
        """Create a modal window"""
        window = ctk.CTkToplevel(parent)
        window.title(title)
        window.geometry(size)
        window.grab_set()  # Make the window modal

        # Center the window
        window.update_idletasks()
        width, height = map(int, size.split('x'))
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

        return window

    @staticmethod
    def show_notification(parent, message, duration=1000):
        """Show a temporary notification"""
        notification = ctk.CTkToplevel(parent)
        notification.geometry("200x50")
        notification.overrideredirect(True)  # Remove window decorations
        notification.attributes("-topmost", True)

        # Center the notification
        notification.update_idletasks()
        width = notification.winfo_width()
        height = notification.winfo_height()
        x = (notification.winfo_screenwidth() // 2) - (width // 2)
        y = (notification.winfo_screenheight() // 2) - (height // 2)
        notification.geometry(f"{width}x{height}+{x}+{y}")

        # Add notification text
        ctk.CTkLabel(notification, text=message).pack(
            expand=True, fill=ctk.BOTH)

        # Auto close after specified duration
        notification.after(duration, notification.destroy)

    @staticmethod
    def show_confirmation(parent, message, on_confirm, on_cancel=None, title="Confirm"):
        """Show a confirmation dialog"""
        confirm = UIHelper.create_modal_window(parent, title, "350x150")

        # Add confirmation message
        ctk.CTkLabel(
            confirm,
            text=message,
            font=("Roboto", 14)
        ).pack(pady=20)

        # Button frame
        btn_frame = ctk.CTkFrame(confirm, fg_color="transparent")
        btn_frame.pack(pady=10, fill=ctk.X)

        # Yes button
        def confirm_action():
            if on_confirm:
                on_confirm()
            confirm.destroy()

        ctk.CTkButton(
            btn_frame,
            text="Yes",
            command=confirm_action,
            fg_color="#d32f2f",
            hover_color="#b71c1c"
        ).pack(side=ctk.LEFT, padx=20, pady=5, expand=True)

        # No button
        def cancel_action():
            if on_cancel:
                on_cancel()
            confirm.destroy()

        ctk.CTkButton(
            btn_frame,
            text="No",
            command=cancel_action
        ).pack(side=ctk.RIGHT, padx=20, pady=5, expand=True)

    @staticmethod
    def show_error(parent, message, title="Error"):
        """Show an error dialog"""
        error_window = UIHelper.create_modal_window(parent, title, "400x180")

        # Error icon frame
        icon_frame = ctk.CTkFrame(error_window, fg_color="transparent")
        icon_frame.pack(pady=(15, 5))

        # Error symbol
        error_symbol = ctk.CTkLabel(
            icon_frame,
            text="⚠️",
            font=("Arial", 24)
        )
        error_symbol.pack()

        # Error message with wrapping
        ctk.CTkLabel(
            error_window,
            text=message,
            wraplength=350,
            font=("Arial", 12)
        ).pack(padx=20, pady=10)

        # Buttons frame
        btn_frame = ctk.CTkFrame(error_window, fg_color="transparent")
        btn_frame.pack(pady=10, fill=ctk.X)

        # OK button
        ctk.CTkButton(
            btn_frame,
            text="OK",
            command=error_window.destroy,
            width=100
        ).pack(pady=5)
