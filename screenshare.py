import customtkinter as ctk
from tkinter import messagebox


class ScreenSharePage(ctk.CTkToplevel):

    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        self.title("MeetSphere - Screen Sharing")
        self.geometry("1200x700")
        self.resizable(False, False)

        self.configure(fg_color="#F4F7FE")

        # Do not hide Dashboard when opening this page

        # Restore Dashboard when window is closed
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
            width=1000,
            height=420,
            corner_radius=15
        )
        preview.pack(pady=20)
        preview.pack_propagate(False)

        ctk.CTkLabel(
            preview,
            text="🖥 Live Screen Preview",
            font=("Arial", 24, "bold")
        ).pack(pady=30)

        ctk.CTkLabel(
            preview,
            text="(Screen preview will appear here)",
            font=("Arial", 18),
            text_color="gray"
        ).pack()

        # ==========================
        # CONTROL BUTTONS
        # ==========================

        controls = ctk.CTkFrame(self)
        controls.pack(pady=20)

        ctk.CTkButton(
            controls,
            text="▶ Start Sharing",
            width=170,
            command=self.start_share
        ).grid(row=0, column=0, padx=10)

        ctk.CTkButton(
            controls,
            text="⏸ Pause",
            width=170,
            command=self.pause_share
        ).grid(row=0, column=1, padx=10)

        ctk.CTkButton(
            controls,
            text="⏹ Stop Sharing",
            width=170,
            fg_color="red",
            hover_color="#B91C1C",
            command=self.stop_share
        ).grid(row=0, column=2, padx=10)

        # ==========================
        # STATUS
        # ==========================

        self.status_label = ctk.CTkLabel(
            self,
            text="Status : Not Sharing",
            font=("Arial", 16, "bold"),
            text_color="gray"
        )
        self.status_label.pack(pady=10)

    # ==========================
    # BUTTON FUNCTIONS
    # ==========================

    def start_share(self):
        self.status_label.configure(
            text="Status : Sharing Screen",
            text_color="green"
        )

        messagebox.showinfo(
            "Screen Sharing",
            "Screen Sharing Started Successfully!"
        )

    def pause_share(self):
        self.status_label.configure(
            text="Status : Sharing Paused",
            text_color="orange"
        )

        messagebox.showinfo(
            "Screen Sharing",
            "Screen Sharing Paused."
        )

    def stop_share(self):
        self.status_label.configure(
            text="Status : Not Sharing",
            text_color="gray"
        )

        messagebox.showinfo(
            "Screen Sharing",
            "Screen Sharing Stopped."
        )

    # ==========================
    # CLOSE WINDOW
    # ==========================

    def close_window(self):
        # Do not deiconify parent; simply destroy this window
        self.destroy()


class ScreenSharePanel(ctk.CTkFrame):

    def __init__(self, parent, dashboard=None, on_close=None):
        super().__init__(parent, fg_color="white", corner_radius=15)
        self.dashboard = dashboard
        self.on_close = on_close

        header = ctk.CTkFrame(self, height=60)
        header.pack(fill="x", padx=20, pady=15)
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="🖥 Screen Sharing",
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

        preview = ctk.CTkFrame(
            self,
            width=1000,
            height=420,
            corner_radius=15
        )
        preview.pack(pady=20)
        preview.pack_propagate(False)

        ctk.CTkLabel(
            preview,
            text="🖥 Live Screen Preview",
            font=("Arial", 24, "bold")
        ).pack(pady=30)

        ctk.CTkLabel(
            preview,
            text="(Screen preview will appear here)",
            font=("Arial", 18),
            text_color="gray"
        ).pack()

        controls = ctk.CTkFrame(self)
        controls.pack(pady=20)

        ctk.CTkButton(
            controls,
            text="▶ Start Sharing",
            width=170,
            command=self.start_share
        ).grid(row=0, column=0, padx=10)

        ctk.CTkButton(
            controls,
            text="⏸ Pause",
            width=170,
            command=self.pause_share
        ).grid(row=0, column=1, padx=10)

        ctk.CTkButton(
            controls,
            text="⏹ Stop Sharing",
            width=170,
            fg_color="red",
            hover_color="#B91C1C",
            command=self.stop_share
        ).grid(row=0, column=2, padx=10)

        self.status_label = ctk.CTkLabel(
            self,
            text="Status : Not Sharing",
            font=("Arial", 16, "bold"),
            text_color="gray"
        )
        self.status_label.pack(pady=10)

    def start_share(self):
        self.status_label.configure(
            text="Status : Sharing Screen",
            text_color="green"
        )

        messagebox.showinfo(
            "Screen Sharing",
            "Screen Sharing Started Successfully!"
        )

    def pause_share(self):
        self.status_label.configure(
            text="Status : Sharing Paused",
            text_color="orange"
        )

        messagebox.showinfo(
            "Screen Sharing",
            "Screen Sharing Paused."
        )

    def stop_share(self):
        self.status_label.configure(
            text="Status : Not Sharing",
            text_color="gray"
        )

        messagebox.showinfo(
            "Screen Sharing",
            "Screen Sharing Stopped."
        )

    def close(self):
        try:
            self.destroy()
        except Exception:
            pass
        if callable(self.on_close):
            self.on_close()
