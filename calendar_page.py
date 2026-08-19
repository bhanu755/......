import customtkinter as ctk
from screens.join_meeting import JoinMeetingPage, JoinMeetingPanel
from backend.database import get_all_meetings
from screens import register_page, unregister_page


class CalendarPage(ctk.CTkToplevel):

    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        self.title("MeetSphere - Calendar")
        self.geometry("1200x700")
        self.resizable(False, False)

        self.configure(fg_color="#F4F7FE")

        # Do not hide Dashboard when opening this page
        # (previously called parent.withdraw)

        # Register this page so other pages can trigger a refresh
        try:
            register_page('calendar', self)
        except Exception:
            pass

        # Close only this window when X is clicked
        self.protocol("WM_DELETE_WINDOW", self.close_window)
        # ==========================
        # HEADER
        # ==========================
        header = ctk.CTkFrame(self, height=70)
        header.pack(fill="x", padx=20, pady=20)
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="📅 Meeting Calendar",
            font=("Arial", 28, "bold")
        ).pack(side="left", padx=20)

        ctk.CTkButton(
            header,
            text="← Back to Dashboard",
            command=self.close_window
        ).pack(side="right", padx=20)

        # ==========================
        # UPCOMING EVENTS
        # ==========================

        body = ctk.CTkFrame(self)
        body.pack(fill="both", expand=True, padx=20, pady=10)

        meetings = get_all_meetings()

        for m in meetings:
            # meeting tuple: (id, title, meeting_date, meeting_time, duration, description)
            date = m[2]
            meeting = m[1]
            time = m[3]

            row = ctk.CTkFrame(body)
            row.pack(fill="x", padx=10, pady=8)

            ctk.CTkLabel(
                row,
                text=date,
                width=180,
                font=("Arial", 15, "bold")
            ).pack(side="left", padx=10)

            ctk.CTkLabel(
                row,
                text=meeting,
                width=350,
                anchor="w",
                font=("Arial", 15)
            ).pack(side="left")

            ctk.CTkLabel(
                row,
                text=time,
                width=150
            ).pack(side="left")

            ctk.CTkButton(
                row,
                text="Join",
                width=80,
                command=lambda m=meeting, d=date, t=time: self.join_meeting(m, d, t)
            ).pack(side="right", padx=10)

    # ==========================
    # FUNCTIONS
    # ==========================

    def join_meeting(self, meeting, date, time):
        self.close_window()
        JoinMeetingPage(self.parent, meeting_title=meeting, meeting_date=date, meeting_time=time)

    def refresh(self):
        # Rebuild the events area by destroying and recreating widgets
        for child in self.winfo_children():
            child.destroy()
        # Re-initialize UI by calling __init__ body again: simplest is to recreate
        self.__init__(self.parent)

    def close_window(self):
        try:
            unregister_page('calendar')
        except Exception:
            pass
        self.destroy()


class CalendarPanel(ctk.CTkFrame):

    def __init__(self, parent, dashboard=None, on_close=None):
        super().__init__(parent, fg_color="white", corner_radius=15)
        self.dashboard = dashboard
        self.on_close = on_close

        try:
            register_page('calendar', self)
        except Exception:
            pass

        header = ctk.CTkFrame(self, height=70)
        header.pack(fill="x", padx=20, pady=20)
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="📅 Meeting Calendar",
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

        self.body = ctk.CTkScrollableFrame(self)
        self.body.pack(fill="both", expand=True, padx=20, pady=10)

        self.refresh()

    def join_meeting(self, meeting, date, time):
        if self.dashboard:
            self.dashboard.show_panel(
                JoinMeetingPanel,
                meeting_title=meeting,
                meeting_date=date,
                meeting_time=time
            )

    def refresh(self):
        for child in self.body.winfo_children():
            child.destroy()

        meetings = get_all_meetings()

        if not meetings:
            ctk.CTkLabel(
                self.body,
                text="No upcoming meetings found.",
                font=("Arial", 16),
                text_color="gray"
            ).pack(pady=20)
            return

        for m in meetings:
            date = m[2]
            meeting = m[1]
            time = m[3]

            row = ctk.CTkFrame(self.body)
            row.pack(fill="x", padx=10, pady=8)

            ctk.CTkLabel(
                row,
                text=date,
                width=180,
                font=("Arial", 15, "bold")
            ).pack(side="left", padx=10)

            ctk.CTkLabel(
                row,
                text=meeting,
                width=350,
                anchor="w",
                font=("Arial", 15)
            ).pack(side="left")

            ctk.CTkLabel(
                row,
                text=time,
                width=150
            ).pack(side="left")

            ctk.CTkButton(
                row,
                text="Join",
                width=80,
                command=lambda m=meeting, d=date, t=time: self.join_meeting(m, d, t)
            ).pack(side="right", padx=10)

    def close(self):
        try:
            unregister_page('calendar')
        except Exception:
            pass
        try:
            self.destroy()
        except Exception:
            pass
        if callable(self.on_close):
            self.on_close()
