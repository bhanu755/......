import customtkinter as ctk
from tkinter import messagebox


class InviteMembersPage(ctk.CTkToplevel):

    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        self.title("Invite Members")
        self.geometry("900x650")
        self.resizable(False, False)

        self.configure(fg_color="#F4F7FE")

        # Do not hide Dashboard when opening this page

        # Restore Dashboard when X is clicked
        self.protocol("WM_DELETE_WINDOW", self.close_window)

        # ==========================
        # Header
        # ==========================

        header = ctk.CTkFrame(self, height=70)
        header.pack(fill="x", padx=20, pady=20)
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="👥 Invite Members",
            font=("Arial", 28, "bold")
        ).pack(side="left", padx=20)

        ctk.CTkButton(
            header,
            text="← Back to Dashboard",
            command=self.close_window
        ).pack(side="right", padx=20)

        # ==========================
        # Form
        # ==========================

        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=30, pady=20)

        ctk.CTkLabel(
            frame,
            text="Member Name",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=25, pady=(20, 5))

        self.name = ctk.CTkEntry(
            frame,
            width=500,
            placeholder_text="Enter Member Name"
        )
        self.name.pack(anchor="w", padx=25)

        ctk.CTkLabel(
            frame,
            text="Email Address",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=25, pady=(20, 5))

        self.email = ctk.CTkEntry(
            frame,
            width=500,
            placeholder_text="Enter Email"
        )
        self.email.pack(anchor="w", padx=25)

        ctk.CTkLabel(
            frame,
            text="Role",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=25, pady=(20, 5))

        self.role = ctk.CTkComboBox(
            frame,
            width=250,
            values=[
                "Host",
                "Co-Host",
                "Presenter",
                "Participant"
            ]
        )
        self.role.set("Participant")
        self.role.pack(anchor="w", padx=25)

        ctk.CTkButton(
            frame,
            text="Send Invitation",
            width=180,
            height=40,
            command=self.send_invite
        ).pack(pady=40)

    # ==========================
    # SEND INVITE
    # ==========================

    def send_invite(self):

        name = self.name.get().strip()
        email = self.email.get().strip()

        if name == "" or email == "":
            messagebox.showerror(
                "Error",
                "Please fill all fields."
            )
            return

        messagebox.showinfo(
            "Invitation Sent",
            f"Invitation sent successfully to\n{name}"
        )

    # ==========================
    # CLOSE WINDOW
    # ==========================

    def close_window(self):
        # Do not deiconify parent; simply destroy this window
        self.destroy()


class InviteMembersPanel(ctk.CTkFrame):

    def __init__(self, parent, dashboard=None, on_close=None):
        super().__init__(parent, fg_color="white", corner_radius=15)
        self.dashboard = dashboard
        self.on_close = on_close

        header = ctk.CTkFrame(self, height=60)
        header.pack(fill="x", padx=20, pady=15)
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="👥 Invite Members",
            font=("Arial", 24, "bold")
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            header,
            text="Close",
            width=120,
            fg_color="#EF4444",
            hover_color="#DC2626",
            command=self.close
        ).pack(side="right", padx=10)

        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=30, pady=20)

        ctk.CTkLabel(
            frame,
            text="Member Name",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=25, pady=(20, 5))

        self.name = ctk.CTkEntry(
            frame,
            width=500,
            placeholder_text="Enter Member Name"
        )
        self.name.pack(anchor="w", padx=25)

        ctk.CTkLabel(
            frame,
            text="Email Address",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=25, pady=(20, 5))

        self.email = ctk.CTkEntry(
            frame,
            width=500,
            placeholder_text="Enter Email"
        )
        self.email.pack(anchor="w", padx=25)

        ctk.CTkLabel(
            frame,
            text="Role",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=25, pady=(20, 5))

        self.role = ctk.CTkComboBox(
            frame,
            width=250,
            values=[
                "Host",
                "Co-Host",
                "Presenter",
                "Participant"
            ]
        )
        self.role.set("Participant")
        self.role.pack(anchor="w", padx=25)

        ctk.CTkButton(
            frame,
            text="Send Invitation",
            width=180,
            height=40,
            command=self.send_invite
        ).pack(pady=40)

    def send_invite(self):
        name = self.name.get().strip()
        email = self.email.get().strip()

        if name == "" or email == "":
            messagebox.showerror(
                "Error",
                "Please fill all fields."
            )
            return

        messagebox.showinfo(
            "Invitation Sent",
            f"Invitation sent successfully to\n{name}"
        )

    def close(self):
        try:
            self.destroy()
        except Exception:
            pass
        if callable(self.on_close):
            self.on_close()