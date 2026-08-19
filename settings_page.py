import customtkinter as ctk
from tkinter import messagebox

from backend.database import get_user_settings, save_user_settings


class SettingsPage(ctk.CTkToplevel):

    def __init__(self, parent, username):
        super().__init__(parent)

        self.parent = parent
        self.username = username
        self.settings = get_user_settings(username) or ()

        mic_enabled = bool(self.settings[1]) if len(self.settings) > 1 else True
        camera_enabled = bool(self.settings[2]) if len(self.settings) > 2 else True
        notifications_enabled = bool(self.settings[3]) if len(self.settings) > 3 else True
        dark_mode = bool(self.settings[4]) if len(self.settings) > 4 else False
        display_name = self.settings[5] if len(self.settings) > 5 and self.settings[5] else ""
        email = self.settings[6] if len(self.settings) > 6 and self.settings[6] else ""

        self.title("MeetSphere - Settings")
        self.geometry("1200x700")
        self.resizable(False, False)

        self.configure(fg_color="#F4F7FE")

        # Do not hide Dashboard when opening this page
        self.protocol("WM_DELETE_WINDOW", self.close_window)

        header = ctk.CTkFrame(self, height=70)
        header.pack(fill="x", padx=20, pady=20)
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="⚙ Settings",
            font=("Arial", 28, "bold")
        ).pack(side="left", padx=20)

        ctk.CTkButton(
            header,
            text="← Back to Dashboard",
            command=self.close_window
        ).pack(side="right", padx=20)

        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            frame,
            text="General Settings",
            font=("Arial", 24, "bold")
        ).pack(anchor="w", padx=20, pady=20)

        self.mic = ctk.BooleanVar(value=mic_enabled)
        self.camera = ctk.BooleanVar(value=camera_enabled)
        self.notifications = ctk.BooleanVar(value=notifications_enabled)
        self.dark_mode = ctk.BooleanVar(value=dark_mode)

        ctk.CTkCheckBox(
            frame,
            text="Enable Microphone",
            variable=self.mic
        ).pack(anchor="w", padx=30, pady=10)

        ctk.CTkCheckBox(
            frame,
            text="Enable Camera",
            variable=self.camera
        ).pack(anchor="w", padx=30, pady=10)

        ctk.CTkCheckBox(
            frame,
            text="Enable Notifications",
            variable=self.notifications
        ).pack(anchor="w", padx=30, pady=10)

        self.dark_mode = ctk.CTkSwitch(
            frame,
            text="Dark Mode",
            variable=self.dark_mode,
            command=self.change_theme
        )
        self.dark_mode.pack(anchor="w", padx=30, pady=15)

        ctk.CTkLabel(
            frame,
            text="Display Name",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=30, pady=(20, 5))

        self.name = ctk.CTkEntry(
            frame,
            width=350,
            placeholder_text="Enter your display name"
        )
        self.name.pack(anchor="w", padx=30)
        self.name.insert(0, display_name)

        ctk.CTkLabel(
            frame,
            text="Email",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=30, pady=(20, 5))

        self.email = ctk.CTkEntry(
            frame,
            width=350,
            placeholder_text="Enter your email"
        )
        self.email.pack(anchor="w", padx=30)
        self.email.insert(0, email)

        ctk.CTkButton(
            frame,
            text="💾 Save Settings",
            width=180,
            command=self.save_settings
        ).pack(pady=30)

    def save_settings(self):
        display_name = self.name.get().strip()
        email = self.email.get().strip()

        if not display_name:
            messagebox.showerror("Error", "Display name cannot be empty.")
            return

        if not email:
            messagebox.showerror("Error", "Email cannot be empty.")
            return

        save_user_settings(
            self.username,
            self.mic.get(),
            self.camera.get(),
            self.notifications.get(),
            self.dark_mode.get(),
            display_name,
            email
        )

        messagebox.showinfo(
            "Settings",
            "Settings Saved Successfully!"
        )

    def change_theme(self):
        if self.dark_mode.get():
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")

    def close_window(self):
        # Do not deiconify parent; simply destroy this window
        self.destroy()


class SettingsPanel(ctk.CTkFrame):

    def __init__(self, parent, username, dashboard=None, on_close=None):
        super().__init__(parent, fg_color="white", corner_radius=15)
        self.username = username
        self.dashboard = dashboard
        self.on_close = on_close
        self.settings = get_user_settings(username) or ()

        mic_enabled = bool(self.settings[1]) if len(self.settings) > 1 else True
        camera_enabled = bool(self.settings[2]) if len(self.settings) > 2 else True
        notifications_enabled = bool(self.settings[3]) if len(self.settings) > 3 else True
        dark_mode = bool(self.settings[4]) if len(self.settings) > 4 else False
        display_name = self.settings[5] if len(self.settings) > 5 and self.settings[5] else ""
        email = self.settings[6] if len(self.settings) > 6 and self.settings[6] else ""

        header = ctk.CTkFrame(self, height=70)
        header.pack(fill="x", padx=20, pady=20)
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="⚙ Settings",
            font=("Arial", 28, "bold")
        ).pack(side="left", padx=20)

        ctk.CTkButton(
            header,
            text="Close",
            width=120,
            fg_color="#EF4444",
            hover_color="#DC2626",
            command=self.close
        ).pack(side="right", padx=20)

        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            frame,
            text="General Settings",
            font=("Arial", 24, "bold")
        ).pack(anchor="w", padx=20, pady=20)

        self.mic = ctk.BooleanVar(value=mic_enabled)
        self.camera = ctk.BooleanVar(value=camera_enabled)
        self.notifications = ctk.BooleanVar(value=notifications_enabled)
        self.dark_mode = ctk.BooleanVar(value=dark_mode)

        ctk.CTkCheckBox(
            frame,
            text="Enable Microphone",
            variable=self.mic
        ).pack(anchor="w", padx=30, pady=10)

        ctk.CTkCheckBox(
            frame,
            text="Enable Camera",
            variable=self.camera
        ).pack(anchor="w", padx=30, pady=10)

        ctk.CTkCheckBox(
            frame,
            text="Enable Notifications",
            variable=self.notifications
        ).pack(anchor="w", padx=30, pady=10)

        self.dark_mode_switch = ctk.CTkSwitch(
            frame,
            text="Dark Mode",
            variable=self.dark_mode,
            command=self.change_theme
        )
        self.dark_mode_switch.pack(anchor="w", padx=30, pady=15)

        ctk.CTkLabel(
            frame,
            text="Display Name",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=30, pady=(20, 5))

        self.name = ctk.CTkEntry(
            frame,
            width=350,
            placeholder_text="Enter your display name"
        )
        self.name.pack(anchor="w", padx=30)
        self.name.insert(0, display_name)

        ctk.CTkLabel(
            frame,
            text="Email",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=30, pady=(20, 5))

        self.email = ctk.CTkEntry(
            frame,
            width=350,
            placeholder_text="Enter your email"
        )
        self.email.pack(anchor="w", padx=30)
        self.email.insert(0, email)

        ctk.CTkButton(
            frame,
            text="💾 Save Settings",
            width=180,
            command=self.save_settings
        ).pack(pady=30)

    def save_settings(self):
        display_name = self.name.get().strip()
        email = self.email.get().strip()

        if not display_name:
            messagebox.showerror("Error", "Display name cannot be empty.")
            return

        if not email:
            messagebox.showerror("Error", "Email cannot be empty.")
            return

        save_user_settings(
            self.username,
            self.mic.get(),
            self.camera.get(),
            self.notifications.get(),
            self.dark_mode.get(),
            display_name,
            email
        )

        messagebox.showinfo(
            "Settings",
            "Settings Saved Successfully!"
        )

    def change_theme(self):
        if self.dark_mode.get():
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")

    def close(self):
        try:
            self.destroy()
        except Exception:
            pass
        if callable(self.on_close):
            self.on_close()


if __name__ == "__main__":
    root = ctk.CTk()
    root.withdraw()
    SettingsPage(root, "johndoe")
    root.mainloop()
