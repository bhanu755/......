import customtkinter as ctk
from tkinter import messagebox


class ParticipantsPage(ctk.CTkToplevel):

    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        self.title("MeetSphere - Participants")
        self.geometry("1200x700")
        self.resizable(False, False)

        self.configure(fg_color="#F4F7FE")

        # Do not hide Dashboard when opening this page

        # Restore Dashboard when X button is clicked
        self.protocol("WM_DELETE_WINDOW", self.close_window)

        # ==========================
        # HEADER
        # ==========================

        header = ctk.CTkFrame(self, height=70)
        header.pack(fill="x", padx=20, pady=20)
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="👥 Participants",
            font=("Arial", 28, "bold")
        ).pack(side="left", padx=20)

        ctk.CTkButton(
            header,
            text="← Back to Dashboard",
            command=self.close_window
        ).pack(side="right", padx=20)

        # ==========================
        # PARTICIPANTS LIST
        # ==========================

        body = ctk.CTkScrollableFrame(self)
        body.pack(fill="both", expand=True, padx=20, pady=10)

        participants = []

        for icon, name, role, status in participants:

            row = ctk.CTkFrame(body)
            row.pack(fill="x", padx=10, pady=8)

            ctk.CTkLabel(
                row,
                text=icon,
                font=("Arial", 26)
            ).pack(side="left", padx=15)

            info = ctk.CTkFrame(
                row,
                fg_color="transparent"
            )
            info.pack(side="left", padx=10)

            ctk.CTkLabel(
                info,
                text=name,
                font=("Arial", 16, "bold")
            ).pack(anchor="w")

            ctk.CTkLabel(
                info,
                text=role,
                text_color="gray"
            ).pack(anchor="w")

            ctk.CTkLabel(
                row,
                text=status,
                text_color="green",
                font=("Arial", 14)
            ).pack(side="right", padx=20)

        # ==========================
        # ACTION BUTTONS
        # ==========================

        bottom = ctk.CTkFrame(self)
        bottom.pack(fill="x", padx=20, pady=15)

        ctk.CTkButton(
            bottom,
            text="➕ Add Participant",
            width=180,
            command=self.add_participant
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            bottom,
            text="📨 Invite Participant",
            width=180,
            command=self.invite_participant
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            bottom,
            text="❌ Remove Participant",
            width=180,
            fg_color="red",
            hover_color="#B91C1C",
            command=self.remove_participant
        ).pack(side="left", padx=10)

    # ==========================
    # BUTTON FUNCTIONS
    # ==========================

    def add_participant(self):
        messagebox.showinfo(
            "Participants",
            "New participant added successfully."
        )

    def invite_participant(self):
        messagebox.showinfo(
            "Participants",
            "Invitation sent successfully."
        )

    def remove_participant(self):
        messagebox.showinfo(
            "Participants",
            "Participant removed successfully."
        )

    # ==========================
    # CLOSE WINDOW
    # ==========================

    def close_window(self):
        # Do not deiconify parent; simply destroy this window
        self.destroy()


class ParticipantsPanel(ctk.CTkFrame):

    def __init__(self, parent, dashboard=None, on_close=None):
        super().__init__(parent, fg_color="white", corner_radius=15)
        self.dashboard = dashboard
        self.on_close = on_close

        header = ctk.CTkFrame(self, height=70)
        header.pack(fill="x", padx=20, pady=20)
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="👥 Participants",
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

        body = ctk.CTkScrollableFrame(self)
        body.pack(fill="both", expand=True, padx=20, pady=10)

        participants = []

        for icon, name, role, status in participants:
            row = ctk.CTkFrame(body)
            row.pack(fill="x", padx=10, pady=8)

            ctk.CTkLabel(
                row,
                text=icon,
                font=("Arial", 26)
            ).pack(side="left", padx=15)

            info = ctk.CTkFrame(
                row,
                fg_color="transparent"
            )
            info.pack(side="left", padx=10)

            ctk.CTkLabel(
                info,
                text=name,
                font=("Arial", 16, "bold")
            ).pack(anchor="w")

            ctk.CTkLabel(
                info,
                text=role,
                text_color="gray"
            ).pack(anchor="w")

            ctk.CTkLabel(
                row,
                text=status,
                text_color="green",
                font=("Arial", 14)
            ).pack(side="right", padx=20)

        bottom = ctk.CTkFrame(self)
        bottom.pack(fill="x", padx=20, pady=15)

        ctk.CTkButton(
            bottom,
            text="➕ Add Participant",
            width=180,
            command=self.add_participant
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            bottom,
            text="📨 Invite Participant",
            width=180,
            command=self.invite_participant
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            bottom,
            text="❌ Remove Participant",
            width=180,
            fg_color="red",
            hover_color="#B91C1C",
            command=self.remove_participant
        ).pack(side="left", padx=10)

    def add_participant(self):
        messagebox.showinfo(
            "Participants",
            "New participant added successfully."
        )

    def invite_participant(self):
        messagebox.showinfo(
            "Participants",
            "Invitation sent successfully."
        )

    def remove_participant(self):
        messagebox.showinfo(
            "Participants",
            "Participant removed successfully."
        )

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

    ParticipantsPage(root)

    root.mainloop()