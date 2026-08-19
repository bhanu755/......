import customtkinter as ctk
from tkinter import messagebox

from backend.database import get_meeting_by_id, get_all_meetings
from screens.meeting_room import MeetingRoomPage


class JoinMeetingPage(ctk.CTkToplevel):

    def __init__(self, parent, meeting_id=None, meeting_title=None, meeting_date=None, meeting_time=None):
        super().__init__(parent)

        self.parent = parent
        self.meeting_id_value = meeting_id
        self.meeting_title = meeting_title
        self.meeting_date = meeting_date
        self.meeting_time = meeting_time

        self.title("Join Meeting")
        self.geometry("900x600")
        self.resizable(True, True)
        try:
            self.minsize(520, 400)
        except Exception:
            pass

        self.configure(fg_color="#F4F7FE")

        # Do not hide Dashboard when opening this page

        # Restore Dashboard when closed
        self.protocol("WM_DELETE_WINDOW", self.close_window)

        # ==========================
        # Header
        # ==========================

        header = ctk.CTkFrame(self, height=70)
        header.pack(fill="x", padx=20, pady=20)
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="📹 Join Meeting",
            font=("Arial", 28, "bold")
        ).pack(side="left", padx=20)

        ctk.CTkButton(
            header,
            text="← Back",
            command=self.close_window
        ).pack(side="right", padx=20)

        # ==========================
        # Join Form
        # ==========================

        # Scrollable content to ensure bottom controls reachable on small screens
        frame = ctk.CTkScrollableFrame(self, corner_radius=8)
        frame.pack(fill="both", expand=True, padx=30, pady=20)

        ctk.CTkLabel(
            frame,
            text="Meeting ID",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=25, pady=(30, 5))

        self.meeting_id = ctk.CTkEntry(
            frame,
            width=450,
            placeholder_text="Enter Meeting ID"
        )
        self.meeting_id.pack(anchor="w", padx=25)

        if self.meeting_id_value:
            self.meeting_id.insert(0, self.meeting_id_value)

        if self.meeting_title:
            ctk.CTkLabel(
                frame,
                text=f"Joining: {self.meeting_title}",
                font=("Arial", 14, "italic"),
                text_color="gray"
            ).pack(anchor="w", padx=25, pady=(8, 10))

        if self.meeting_date and self.meeting_time:
            ctk.CTkLabel(
                frame,
                text=f"Scheduled for: {self.meeting_date} at {self.meeting_time}",
                font=("Arial", 14),
                text_color="gray"
            ).pack(anchor="w", padx=25, pady=(0, 10))

        ctk.CTkLabel(
            frame,
            text="Your Name",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=25, pady=(20, 5))

        self.username = ctk.CTkEntry(
            frame,
            width=450,
            placeholder_text="Enter Your Name"
        )
        self.username.pack(anchor="w", padx=25)

        ctk.CTkLabel(
            frame,
            text="Password (Optional)",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=25, pady=(20, 5))

        self.password = ctk.CTkEntry(
            frame,
            width=450,
            show="*",
            placeholder_text="Meeting Password"
        )
        self.password.pack(anchor="w", padx=25)

        ctk.CTkButton(
            frame,
            text="Join Meeting",
            width=180,
            height=40,
            command=self.join
        ).pack(pady=40)

    # ==========================
    # Join Meeting
    # ==========================

    def join(self):

        meeting = self.meeting_id.get().strip()
        user = self.username.get().strip()

        if meeting == "" or user == "":
            messagebox.showerror(
                "Error",
                "Please fill all required fields."
            )
            return

        meeting_data = None

        if meeting.isdigit():
            meeting_data = get_meeting_by_id(int(meeting))
        else:
            all_meetings = get_all_meetings()
            for meeting_row in all_meetings:
                if meeting.lower() == meeting_row[1].lower():
                    meeting_data = meeting_row
                    break

        if meeting_data is None:
            messagebox.showerror(
                "Error",
                "Meeting not found. Please check the meeting ID or title."
            )
            return

        MeetingRoomPage(self, meeting_data, username=user)
        self.close()

    # ==========================
    # Close Window
    # ==========================

    def close_window(self):
        # Do not deiconify parent; simply destroy this window
        self.destroy()


class JoinMeetingPanel(ctk.CTkFrame):
    """Embedded join-meeting panel to show inside the Dashboard main view."""

    def __init__(self, parent, dashboard=None, meeting_id=None, meeting_title=None, meeting_date=None, meeting_time=None, on_close=None, **kwargs):
        super().__init__(parent, fg_color="white", corner_radius=8)
        self.parent = parent
        self.dashboard = dashboard
        self.meeting_id_value = meeting_id
        self.meeting_title = meeting_title
        self.meeting_date = meeting_date
        self.meeting_time = meeting_time
        self.on_close = on_close

        header = ctk.CTkFrame(self, height=60)
        header.pack(fill="x", padx=10, pady=10)
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="📹 Join Meeting",
            font=("Arial", 20, "bold")
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            header,
            text="Close",
            width=100,
            fg_color="#EF4444",
            hover_color="#DC2626",
            command=self.close
        ).pack(side="right", padx=8)

        body = ctk.CTkScrollableFrame(self, corner_radius=8)
        body.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        ctk.CTkLabel(
            body,
            text="Meeting ID",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=8, pady=(6, 3))

        self.meeting_id = ctk.CTkEntry(
            body,
            width=450,
            placeholder_text="Enter Meeting ID"
        )
        self.meeting_id.pack(anchor="w", padx=8)

        if self.meeting_id_value:
            self.meeting_id.insert(0, self.meeting_id_value)

        if self.meeting_title:
            ctk.CTkLabel(
                body,
                text=f"Joining: {self.meeting_title}",
                font=("Arial", 12, "italic"),
                text_color="gray"
            ).pack(anchor="w", padx=8, pady=(8, 10))

        if self.meeting_date and self.meeting_time:
            ctk.CTkLabel(
                body,
                text=f"Scheduled for: {self.meeting_date} at {self.meeting_time}",
                font=("Arial", 12),
                text_color="gray"
            ).pack(anchor="w", padx=8, pady=(0, 10))

        ctk.CTkLabel(
            body,
            text="Your Name",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=8, pady=(6, 3))

        self.username = ctk.CTkEntry(
            body,
            width=450,
            placeholder_text="Enter Your Name"
        )
        self.username.pack(anchor="w", padx=8)

        ctk.CTkLabel(
            body,
            text="Password (Optional)",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=8, pady=(6, 3))

        self.password = ctk.CTkEntry(
            body,
            width=450,
            show="*",
            placeholder_text="Meeting Password"
        )
        self.password.pack(anchor="w", padx=8)

        ctk.CTkButton(
            body,
            text="Join Meeting",
            width=180,
            height=40,
            command=self.join
        ).pack(pady=20)

    def join(self):
        meeting = self.meeting_id.get().strip()
        user = self.username.get().strip()

        if meeting == "" or user == "":
            messagebox.showerror("Error", "Please fill all required fields.")
            return

        meeting_data = None

        if meeting.isdigit():
            meeting_data = get_meeting_by_id(int(meeting))
        else:
            all_meetings = get_all_meetings()
            for meeting_row in all_meetings:
                if meeting.lower() == meeting_row[1].lower():
                    meeting_data = meeting_row
                    break

        if meeting_data is None:
            messagebox.showerror("Error", "Meeting not found. Please check the meeting ID or title.")
            return

        messagebox.showinfo("Success", f"{user} joined '{meeting_data[1]}' on {meeting_data[2]} at {meeting_data[3]}")

        self.close()

    def close(self):
        try:
            self.destroy()
        except Exception:
            pass
        if callable(self.on_close):
            try:
                self.on_close()
            except Exception:
                pass