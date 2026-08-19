import customtkinter as ctk


class NotificationPage(ctk.CTkToplevel):

    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        self.title("MeetSphere - Notifications")
        self.geometry("1000x650")
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
            text="🔔 Notifications",
            font=("Arial", 28, "bold")
        ).pack(side="left", padx=20)

        ctk.CTkButton(
            header,
            text="← Back to Dashboard",
            command=self.close_window
        ).pack(side="right", padx=20)

        # ==========================
        # NOTIFICATIONS
        # ==========================

        frame = ctk.CTkScrollableFrame(self)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        notifications = []

        for note in notifications:

            card = ctk.CTkFrame(
                frame,
                corner_radius=10
            )
            card.pack(fill="x", pady=8)

            ctk.CTkLabel(
                card,
                text=note,
                font=("Arial", 15),
                anchor="w"
            ).pack(anchor="w", padx=15, pady=15)

    # ==========================
    # CLOSE WINDOW
    # ==========================

    def close_window(self):
        # Do not deiconify parent; simply destroy this window
        self.destroy()


class NotificationsPanel(ctk.CTkFrame):

    def __init__(self, parent, dashboard=None, on_close=None):
        super().__init__(parent, fg_color="white", corner_radius=15)
        self.dashboard = dashboard
        self.on_close = on_close

        header = ctk.CTkFrame(self, height=70)
        header.pack(fill="x", padx=20, pady=20)
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="🔔 Notifications",
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

        frame = ctk.CTkScrollableFrame(self)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        notifications = []

        for note in notifications:
            card = ctk.CTkFrame(
                frame,
                corner_radius=10
            )
            card.pack(fill="x", pady=8)

            ctk.CTkLabel(
                card,
                text=note,
                font=("Arial", 15),
                anchor="w"
            ).pack(anchor="w", padx=15, pady=15)

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

    NotificationPage(root)

    root.mainloop()