import customtkinter as ctk
from tkinter import messagebox

from backend.database import (
    get_user,
    get_user_settings,
    update_user,
    update_user_password,
    save_user_settings,
    verify_password
)


class ProfilePage(ctk.CTkToplevel):

    def __init__(self, parent, username):
        super().__init__(parent)

        self.parent = parent
        self.username = username
        self.user = get_user(username) or ()
        self.settings = get_user_settings(username) or ()

        display_name = self.settings[5] if len(self.settings) > 5 and self.settings[5] else (self.user[1] if len(self.user) > 1 else "")
        email = self.settings[6] if len(self.settings) > 6 and self.settings[6] else (self.user[2] if len(self.user) > 2 else "")

        self.title("MeetSphere - Profile")
        self.geometry("1000x700")
        self.resizable(False, False)

        self.configure(fg_color="#F4F7FE")

        # Do not hide Dashboard when opening this page
        self.protocol("WM_DELETE_WINDOW", self.close_window)

        header = ctk.CTkFrame(self, height=70)
        header.pack(fill="x", padx=20, pady=20)
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="👤 My Profile",
            font=("Arial", 28, "bold")
        ).pack(side="left", padx=20)

        ctk.CTkButton(
            header,
            text="← Back to Dashboard",
            command=self.close_window
        ).pack(side="right", padx=20)

        content = ctk.CTkFrame(self)
        content.pack(fill="both", expand=True, padx=30, pady=10)

        left_frame = ctk.CTkFrame(content, width=360, fg_color="white", corner_radius=20)
        left_frame.pack(side="left", fill="y", padx=(0, 15), pady=10)
        left_frame.pack_propagate(False)

        ctk.CTkLabel(
            left_frame,
            text="👤",
            font=("Arial", 80)
        ).pack(pady=25)

        ctk.CTkLabel(
            left_frame,
            text="Profile Overview",
            font=("Arial", 22, "bold")
        ).pack(pady=(0, 15))

        ctk.CTkLabel(
            left_frame,
            text=f"Username: {self.username}",
            font=("Arial", 16)
        ).pack(anchor="w", padx=25, pady=5)

        ctk.CTkLabel(
            left_frame,
            text=f"Email: {email}",
            font=("Arial", 16)
        ).pack(anchor="w", padx=25, pady=5)

        ctk.CTkLabel(
            left_frame,
            text="Role: User",
            font=("Arial", 16)
        ).pack(anchor="w", padx=25, pady=5)

        right_frame = ctk.CTkFrame(content, fg_color="white", corner_radius=20)
        right_frame.pack(side="left", fill="both", expand=True, pady=10)

        ctk.CTkLabel(
            right_frame,
            text="Edit Profile",
            font=("Arial", 24, "bold")
        ).pack(anchor="w", padx=30, pady=(25, 10))

        ctk.CTkLabel(
            right_frame,
            text="Full Name",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=30, pady=(10, 5))

        self.name_entry = ctk.CTkEntry(
            right_frame,
            width=420,
            placeholder_text="Full Name"
        )
        self.name_entry.pack(anchor="w", padx=30)
        self.name_entry.insert(0, display_name)

        ctk.CTkLabel(
            right_frame,
            text="Email",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=30, pady=(20, 5))

        self.email_entry = ctk.CTkEntry(
            right_frame,
            width=420,
            placeholder_text="Email"
        )
        self.email_entry.pack(anchor="w", padx=30)
        self.email_entry.insert(0, email)

        ctk.CTkButton(
            right_frame,
            text="Save Profile",
            width=180,
            command=self.save_profile
        ).pack(anchor="w", padx=30, pady=25)

        ctk.CTkFrame(right_frame, height=2, fg_color="#E5E7EB").pack(fill="x", padx=30, pady=(10, 20))

        ctk.CTkLabel(
            right_frame,
            text="Change Password",
            font=("Arial", 24, "bold")
        ).pack(anchor="w", padx=30, pady=(10, 10))

        ctk.CTkLabel(
            right_frame,
            text="Current Password",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=30, pady=(10, 5))

        self.current_password = ctk.CTkEntry(
            right_frame,
            width=420,
            placeholder_text="Current Password",
            show="*"
        )
        self.current_password.pack(anchor="w", padx=30)

        ctk.CTkLabel(
            right_frame,
            text="New Password",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=30, pady=(20, 5))

        self.new_password = ctk.CTkEntry(
            right_frame,
            width=420,
            placeholder_text="New Password",
            show="*"
        )
        self.new_password.pack(anchor="w", padx=30)

        ctk.CTkLabel(
            right_frame,
            text="Confirm New Password",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=30, pady=(20, 5))

        self.confirm_password = ctk.CTkEntry(
            right_frame,
            width=420,
            placeholder_text="Confirm New Password",
            show="*"
        )
        self.confirm_password.pack(anchor="w", padx=30)

        ctk.CTkButton(
            right_frame,
            text="Update Password",
            width=180,
            command=self.change_password
        ).pack(anchor="w", padx=30, pady=25)

    def save_profile(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()

        if not name:
            messagebox.showerror("Error", "Full name cannot be empty.")
            return

        if not email:
            messagebox.showerror("Error", "Email cannot be empty.")
            return

        update_user(self.username, name, email)

        mic = bool(self.settings[1]) if len(self.settings) > 1 else True
        camera = bool(self.settings[2]) if len(self.settings) > 2 else True
        notifications = bool(self.settings[3]) if len(self.settings) > 3 else True
        dark_mode = bool(self.settings[4]) if len(self.settings) > 4 else False

        save_user_settings(
            self.username,
            mic,
            camera,
            notifications,
            dark_mode,
            name,
            email
        )

        messagebox.showinfo("Success", "Profile saved successfully.")

    def change_password(self):
        current = self.current_password.get().strip()
        new_password = self.new_password.get().strip()
        confirm = self.confirm_password.get().strip()

        if not current:
            messagebox.showerror("Error", "Please enter your current password.")
            return

        if not new_password:
            messagebox.showerror("Error", "Please enter a new password.")
            return

        if new_password != confirm:
            messagebox.showerror("Error", "New passwords do not match.")
            return

        stored_password = self.user[4] if len(self.user) > 4 else None
        if not stored_password or not verify_password(current, stored_password):
            messagebox.showerror("Error", "Current password is incorrect.")
            return

        update_user_password(self.username, new_password)

        self.current_password.delete(0, "end")
        self.new_password.delete(0, "end")
        self.confirm_password.delete(0, "end")

        messagebox.showinfo("Success", "Password updated successfully.")

    def close_window(self):
        # Do not deiconify parent; simply destroy this window
        self.destroy()


class ProfilePanel(ctk.CTkFrame):

    def __init__(self, parent, username, dashboard=None, on_close=None):
        super().__init__(parent, fg_color="white", corner_radius=15)
        self.username = username
        self.dashboard = dashboard
        self.on_close = on_close
        self.user = get_user(username) or ()
        self.settings = get_user_settings(username) or ()

        display_name = self.settings[5] if len(self.settings) > 5 and self.settings[5] else (self.user[1] if len(self.user) > 1 else "")
        email = self.settings[6] if len(self.settings) > 6 and self.settings[6] else (self.user[2] if len(self.user) > 2 else "")

        header = ctk.CTkFrame(self, height=70)
        header.pack(fill="x", padx=20, pady=20)
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="👤 My Profile",
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

        content = ctk.CTkFrame(self)
        content.pack(fill="both", expand=True, padx=30, pady=10)

        left_frame = ctk.CTkFrame(content, width=360, fg_color="white", corner_radius=20)
        left_frame.pack(side="left", fill="y", padx=(0, 15), pady=10)
        left_frame.pack_propagate(False)

        ctk.CTkLabel(
            left_frame,
            text="👤",
            font=("Arial", 80)
        ).pack(pady=25)

        ctk.CTkLabel(
            left_frame,
            text="Profile Overview",
            font=("Arial", 22, "bold")
        ).pack(pady=(0, 15))

        ctk.CTkLabel(
            left_frame,
            text=f"Username: {self.username}",
            font=("Arial", 16)
        ).pack(anchor="w", padx=25, pady=5)

        ctk.CTkLabel(
            left_frame,
            text=f"Email: {email}",
            font=("Arial", 16)
        ).pack(anchor="w", padx=25, pady=5)

        ctk.CTkLabel(
            left_frame,
            text="Role: User",
            font=("Arial", 16)
        ).pack(anchor="w", padx=25, pady=5)

        right_frame = ctk.CTkFrame(content, fg_color="white", corner_radius=20)
        right_frame.pack(side="left", fill="both", expand=True, pady=10)

        ctk.CTkLabel(
            right_frame,
            text="Edit Profile",
            font=("Arial", 24, "bold")
        ).pack(anchor="w", padx=30, pady=(25, 10))

        ctk.CTkLabel(
            right_frame,
            text="Full Name",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=30, pady=(10, 5))

        self.name_entry = ctk.CTkEntry(
            right_frame,
            width=420,
            placeholder_text="Full Name"
        )
        self.name_entry.pack(anchor="w", padx=30)
        self.name_entry.insert(0, display_name)

        ctk.CTkLabel(
            right_frame,
            text="Email",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=30, pady=(20, 5))

        self.email_entry = ctk.CTkEntry(
            right_frame,
            width=420,
            placeholder_text="Email"
        )
        self.email_entry.pack(anchor="w", padx=30)
        self.email_entry.insert(0, email)

        ctk.CTkButton(
            right_frame,
            text="Save Profile",
            width=180,
            command=self.save_profile
        ).pack(anchor="w", padx=30, pady=25)

        ctk.CTkFrame(right_frame, height=2, fg_color="#E5E7EB").pack(fill="x", padx=30, pady=(10, 20))

        ctk.CTkLabel(
            right_frame,
            text="Change Password",
            font=("Arial", 24, "bold")
        ).pack(anchor="w", padx=30, pady=(10, 10))

        ctk.CTkLabel(
            right_frame,
            text="Current Password",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=30, pady=(10, 5))

        self.current_password = ctk.CTkEntry(
            right_frame,
            width=420,
            placeholder_text="Current Password",
            show="*"
        )
        self.current_password.pack(anchor="w", padx=30)

        ctk.CTkLabel(
            right_frame,
            text="New Password",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=30, pady=(20, 5))

        self.new_password = ctk.CTkEntry(
            right_frame,
            width=420,
            placeholder_text="New Password",
            show="*"
        )
        self.new_password.pack(anchor="w", padx=30)

        ctk.CTkLabel(
            right_frame,
            text="Confirm New Password",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=30, pady=(20, 5))

        self.confirm_password = ctk.CTkEntry(
            right_frame,
            width=420,
            placeholder_text="Confirm New Password",
            show="*"
        )
        self.confirm_password.pack(anchor="w", padx=30)

        ctk.CTkButton(
            right_frame,
            text="Update Password",
            width=180,
            command=self.change_password
        ).pack(anchor="w", padx=30, pady=25)

    def save_profile(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()

        if not name:
            messagebox.showerror("Error", "Full name cannot be empty.")
            return

        if not email:
            messagebox.showerror("Error", "Email cannot be empty.")
            return

        update_user(self.username, name, email)

        mic = bool(self.settings[1]) if len(self.settings) > 1 else True
        camera = bool(self.settings[2]) if len(self.settings) > 2 else True
        notifications = bool(self.settings[3]) if len(self.settings) > 3 else True
        dark_mode = bool(self.settings[4]) if len(self.settings) > 4 else False

        save_user_settings(
            self.username,
            mic,
            camera,
            notifications,
            dark_mode,
            name,
            email
        )

        messagebox.showinfo("Success", "Profile saved successfully.")

    def change_password(self):
        current = self.current_password.get().strip()
        new_password = self.new_password.get().strip()
        confirm = self.confirm_password.get().strip()

        if not current:
            messagebox.showerror("Error", "Please enter your current password.")
            return

        if not new_password:
            messagebox.showerror("Error", "Please enter a new password.")
            return

        if new_password != confirm:
            messagebox.showerror("Error", "New passwords do not match.")
            return

        stored_password = self.user[4] if len(self.user) > 4 else None
        if not stored_password or not verify_password(current, stored_password):
            messagebox.showerror("Error", "Current password is incorrect.")
            return

        update_user_password(self.username, new_password)

        self.current_password.delete(0, "end")
        self.new_password.delete(0, "end")
        self.confirm_password.delete(0, "end")

        messagebox.showinfo("Success", "Password updated successfully.")

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
    ProfilePage(root, "johndoe")
    root.mainloop()
