import customtkinter as ctk
from tkinter import messagebox


class ScreenShareMeetingPage(ctk.CTkToplevel):

    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        self.title("MeetSphere - Screen Sharing")
        self.geometry("950x650")
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
            text="🖥 Screen Sharing",
            font=("Arial", 28, "bold")
        ).pack(side="left", padx=20)

        ctk.CTkButton(
            header,
            text="← Back to Dashboard",
            command=self.close_window
        ).pack(side="right", padx=20)

        # ==========================
        # SCREEN PREVIEW
        # ==========================

        preview = ctk.CTkFrame(
            self,
            width=850,
            height=300,
            corner_radius=15
        )
        preview.pack(padx=25, pady=15)
        preview.pack_propagate(False)

        ctk.CTkLabel(
            preview,
            text="🖥 Screen Preview",
            font=("Arial", 26, "bold")
        ).pack(expand=True)

        # ==========================
        # STATUS
        # ==========================

        self.status = ctk.CTkLabel(
            self,
            text="Status : Not Sharing",
            font=("Arial", 18, "bold"),
            text_color="red"
        )
        self.status.pack(pady=10)

        # ==========================
        # BUTTONS
        # ==========================

        buttons = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        buttons.pack(pady=20)

        ctk.CTkButton(
            buttons,
            text="▶ Start Sharing",
            width=180,
            command=self.start_share
        ).grid(row=0, column=0, padx=10)

        ctk.CTkButton(
            buttons,
            text="⏹ Stop Sharing",
            width=180,
            fg_color="#EF4444",
            hover_color="#DC2626",
            command=self.stop_share
        ).grid(row=0, column=1, padx=10)

        ctk.CTkButton(
            buttons,
            text="🖥 Select Screen",
            width=180,
            command=self.select_screen
        ).grid(row=1, column=0, padx=10, pady=15)

        ctk.CTkButton(
            buttons,
            text="🪟 Select Window",
            width=180,
            command=self.select_window
        ).grid(row=1, column=1, padx=10, pady=15)

    # ==========================
    # FUNCTIONS
    # ==========================

    def start_share(self):
        self.status.configure(
            text="Status : Sharing Screen",
            text_color="green"
        )

        messagebox.showinfo(
            "Screen Sharing",
            "Screen sharing started successfully!"
        )

    def stop_share(self):
        self.status.configure(
            text="Status : Not Sharing",
            text_color="red"
        )

        messagebox.showinfo(
            "Screen Sharing",
            "Screen sharing stopped."
        )

    def select_screen(self):
        messagebox.showinfo(
            "Select Screen",
            "Primary Screen selected."
        )

    def select_window(self):
        messagebox.showinfo(
            "Select Window",
            "Application Window selected."
        )

    # ==========================
    # CLOSE WINDOW
    # ==========================

    def close_window(self):
        # Do not deiconify parent; simply destroy this window
        self.destroy()


if __name__ == "__main__":
    root = ctk.CTk()
    root.withdraw()
    ScreenShareMeetingPage(root)
    root.mainloop()