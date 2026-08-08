import customtkinter as ctk
from tkinter import ttk, messagebox

from backend.database import get_all_meetings
from screens.create_meeting import (
    CreateMeetingPage,
    CreateMeetingPanel,
    show_meeting_link_dialog
)
from screens.join_meeting import (
    JoinMeetingPage,
    JoinMeetingPanel
)
from screens.meeting_room import MeetingRoomPage


class MeetingsPage(ctk.CTkToplevel):

    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        self.title("MeetSphere - Meetings")
        self.geometry("1100x700")
        self.resizable(False, False)

        self.configure(fg_color="#F4F7FE")

        # Register this page
        try:
            from screens import register_page
            register_page("meetings", self)
        except Exception:
            pass

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self.close_window)

        # ==========================
        # TITLE
        # ==========================

        title = ctk.CTkLabel(
            self,
            text="Meetings",
            font=("Arial", 30, "bold")
        )
        title.pack(pady=20)

        # ==========================
        # BUTTONS
        # ==========================

        btn_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        btn_frame.pack(pady=10)

        ctk.CTkButton(
            btn_frame,
            text="Create Meeting",
            width=180,
            command=self.create_meeting
        ).grid(row=0, column=0, padx=10)

        ctk.CTkButton(
            btn_frame,
            text="Join Meeting",
            width=180,
            command=self.join_meeting
        ).grid(row=0, column=1, padx=10)

        ctk.CTkButton(
            btn_frame,
            text="Show Link",
            width=150,
            command=self.show_meeting_link
        ).grid(row=0, column=2, padx=10)

        ctk.CTkButton(
            btn_frame,
            text="Open Room",
            width=150,
            command=self.open_meeting_room
        ).grid(row=0, column=3, padx=10)

        ctk.CTkButton(
            btn_frame,
            text="Refresh",
            width=150,
            command=self.refresh
        ).grid(row=0, column=4, padx=10)

        # ==========================
        # TABLE
        # ==========================

        table_frame = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=10
        )
        table_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        self.table = ttk.Treeview(
            table_frame,
            columns=(
                "Title",
                "Date",
                "Time",
                "Duration",
                "Description"
            ),
            show="headings",
            height=15
        )

        self.table.heading(
            "Title",
            text="Meeting Title"
        )

        self.table.heading(
            "Date",
            text="Date"
        )

        self.table.heading(
            "Time",
            text="Time"
        )

        self.table.heading(
            "Duration",
            text="Duration"
        )

        self.table.heading(
            "Description",
            text="Description"
        )

        self.table.column(
            "Title",
            width=250
        )

        self.table.column(
            "Date",
            width=120
        )

        self.table.column(
            "Time",
            width=120
        )

        self.table.column(
            "Duration",
            width=120
        )

        self.table.column(
            "Description",
            width=350
        )

        self.table.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        # Load meetings
        self.refresh()

        # ==========================
        # BACK BUTTON
        # ==========================

        ctk.CTkButton(
            self,
            text="Back to Dashboard",
            width=220,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=self.close_window
        ).pack(pady=20)

    # ==========================
    # CREATE MEETING
    # ==========================

    def create_meeting(self):
        try:
            panel = CreateMeetingPanel(
                self,
                on_close=self.refresh
            )

            panel.pack(
                fill="x",
                padx=20,
                pady=10
            )

        except Exception as e:
            messagebox.showerror(
                "Create Meeting Error",
                f"Unable to open Create Meeting.\n\n{e}"
            )

    # ==========================
    # JOIN MEETING
    # ==========================

    def join_meeting(self):

        selected = self.table.selection()

        if not selected:
            messagebox.showwarning(
                "Join Meeting",
                "Please select a meeting."
            )
            return

        meeting_id = selected[0]

        values = self.table.item(
            meeting_id,
            "values"
        )

        if not values:
            messagebox.showerror(
                "Join Meeting",
                "Unable to read the selected meeting."
            )
            return

        meeting_title = values[0]

        try:
            JoinMeetingPage(
                self,
                meeting_id=meeting_id,
                meeting_title=meeting_title
            )

        except Exception as e:
            messagebox.showerror(
                "Join Meeting Error",
                f"Unable to open Join Meeting.\n\n{e}"
            )

    # ==========================
    # REFRESH TABLE
    # ==========================

    def refresh(self):

        try:
            # Remove existing rows
            self.table.delete(
                *self.table.get_children()
            )

            # Get meetings from database
            meetings = get_all_meetings()

            if meetings is None:
                return

            for meeting in meetings:

                # Make sure the row has enough fields
                title = meeting[1] if len(meeting) > 1 else ""
                date = meeting[2] if len(meeting) > 2 else ""
                time = meeting[3] if len(meeting) > 3 else ""
                duration = meeting[4] if len(meeting) > 4 else ""
                description = meeting[5] if len(meeting) > 5 else ""

                self.table.insert(
                    "",
                    "end",
                    iid=str(meeting[0]),
                    values=(
                        title,
                        date,
                        time,
                        duration,
                        description
                    )
                )

        except Exception as e:
            messagebox.showerror(
                "Refresh Error",
                f"Unable to load meetings.\n\n{e}"
            )

    # ==========================
    # SHOW MEETING LINK
    # ==========================

    def show_meeting_link(self):

        selected = self.table.selection()

        if not selected:
            messagebox.showwarning(
                "Meeting Link",
                "Please select a meeting."
            )
            return

        try:
            meeting_id = int(selected[0])

        except ValueError:
            messagebox.showerror(
                "Meeting Link",
                "Invalid meeting ID."
            )
            return

        try:
            meetings = get_all_meetings()

            meeting_row = next(
                (
                    row
                    for row in meetings
                    if int(row[0]) == meeting_id
                ),
                None
            )

        except Exception as e:
            messagebox.showerror(
                "Meeting Link Error",
                f"Unable to find the meeting.\n\n{e}"
            )
            return

        if not meeting_row:
            messagebox.showerror(
                "Meeting Link",
                "Meeting not found."
            )
            return

        # Link is expected at index 6
        meeting_link = (
            meeting_row[6]
            if len(meeting_row) > 6
            else ""
        )

        if not meeting_link:
            messagebox.showerror(
                "Meeting Link",
                "No link is available for this meeting."
            )
            return

        meeting_title = (
            meeting_row[1]
            if len(meeting_row) > 1
            else "Meeting"
        )

        try:
            show_meeting_link_dialog(
                meeting_link,
                title=meeting_title
            )

        except Exception as e:
            messagebox.showerror(
                "Meeting Link Error",
                f"Unable to show meeting link.\n\n{e}"
            )

    # ==========================
    # OPEN MEETING ROOM
    # ==========================

    def open_meeting_room(self):

        selected = self.table.selection()

        if not selected:
            messagebox.showwarning(
                "Open Meeting Room",
                "Please select a meeting."
            )
            return

        try:
            meeting_id = int(selected[0])

        except ValueError:
            messagebox.showerror(
                "Open Meeting Room",
                "Invalid meeting ID."
            )
            return

        try:
            meetings = get_all_meetings()

            meeting_row = next(
                (
                    row
                    for row in meetings
                    if int(row[0]) == meeting_id
                ),
                None
            )

        except Exception as e:
            messagebox.showerror(
                "Open Meeting Room Error",
                f"Unable to find the meeting.\n\n{e}"
            )
            return

        if not meeting_row:
            messagebox.showerror(
                "Open Meeting Room",
                "Meeting not found."
            )
            return

        try:
            MeetingRoomPage(
                self,
                meeting_row
            )

        except Exception as e:
            messagebox.showerror(
                "Open Meeting Room Error",
                f"Unable to open the meeting room.\n\n{e}"
            )

    # ==========================
    # CLOSE WINDOW
    # ==========================

    def close_window(self):

        try:
            from screens import unregister_page
            unregister_page("meetings")

        except Exception:
            pass

        try:
            self.destroy()

        except Exception:
            pass


# ============================================================
# MEETINGS PANEL
# ============================================================

class MeetingsPanel(ctk.CTkFrame):

    def __init__(
        self,
        parent,
        dashboard=None,
        on_close=None
    ):

        super().__init__(
            parent,
            fg_color="white",
            corner_radius=15
        )

        self.dashboard = dashboard
        self.on_close = on_close

        # Register page
        try:
            from screens import register_page
            register_page("meetings", self)

        except Exception:
            pass

        # ==========================
        # HEADER
        # ==========================

        header = ctk.CTkFrame(
            self,
            height=70
        )

        header.pack(
            fill="x",
            padx=20,
            pady=20
        )

        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="Meetings",
            font=("Arial", 30, "bold")
        ).pack(
            side="left",
            padx=20
        )

        # ==========================
        # BUTTONS
        # ==========================

        btn_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        btn_frame.pack(pady=10)

        ctk.CTkButton(
            btn_frame,
            text="Create Meeting",
            width=180,
            command=self.create_meeting
        ).grid(
            row=0,
            column=0,
            padx=10
        )

        ctk.CTkButton(
            btn_frame,
            text="Join Meeting",
            width=180,
            command=self.join_meeting
        ).grid(
            row=0,
            column=1,
            padx=10
        )

        ctk.CTkButton(
            btn_frame,
            text="Show Link",
            width=150,
            command=self.show_meeting_link
        ).grid(
            row=0,
            column=2,
            padx=10
        )

        ctk.CTkButton(
            btn_frame,
            text="Open Room",
            width=150,
            command=self.open_meeting_room
        ).grid(
            row=0,
            column=3,
            padx=10
        )

        ctk.CTkButton(
            btn_frame,
            text="Refresh",
            width=150,
            command=self.refresh
        ).grid(
            row=0,
            column=4,
            padx=10
        )

        # ==========================
        # TABLE
        # ==========================

        table_frame = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=10
        )

        table_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        self.table = ttk.Treeview(
            table_frame,
            columns=(
                "Title",
                "Date",
                "Time",
                "Duration",
                "Description"
            ),
            show="headings",
            height=15
        )

        self.table.heading(
            "Title",
            text="Meeting Title"
        )

        self.table.heading(
            "Date",
            text="Date"
        )

        self.table.heading(
            "Time",
            text="Time"
        )

        self.table.heading(
            "Duration",
            text="Duration"
        )

        self.table.heading(
            "Description",
            text="Description"
        )

        self.table.column(
            "Title",
            width=250
        )

        self.table.column(
            "Date",
            width=120
        )

        self.table.column(
            "Time",
            width=120
        )

        self.table.column(
            "Duration",
            width=120
        )

        self.table.column(
            "Description",
            width=350
        )

        self.table.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        # Load meetings
        self.refresh()

        # ==========================
        # BACK BUTTON
        # ==========================

        ctk.CTkButton(
            self,
            text="Back to Dashboard",
            width=220,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=self.close
        ).pack(pady=20)

    # ==========================
    # CREATE MEETING
    # ==========================

    def create_meeting(self):

        if self.dashboard:

            try:
                self.dashboard.show_panel(
                    CreateMeetingPanel
                )

            except Exception as e:
                messagebox.showerror(
                    "Create Meeting Error",
                    f"Unable to open Create Meeting.\n\n{e}"
                )

        else:

            try:
                panel = CreateMeetingPanel(
                    self,
                    on_close=self.refresh
                )

                panel.pack(
                    fill="x",
                    padx=20,
                    pady=10
                )

            except Exception as e:
                messagebox.showerror(
                    "Create Meeting Error",
                    f"Unable to open Create Meeting.\n\n{e}"
                )

    # ==========================
    # JOIN MEETING
    # ==========================

    def join_meeting(self):

        selected = self.table.selection()

        if not selected:
            messagebox.showwarning(
                "Join Meeting",
                "Please select a meeting."
            )
            return

        meeting_id = selected[0]

        values = self.table.item(
            meeting_id,
            "values"
        )

        if not values:
            messagebox.showerror(
                "Join Meeting",
                "Unable to read the selected meeting."
            )
            return

        meeting_title = values[0]

        if self.dashboard:

            try:
                self.dashboard.show_panel(
                    JoinMeetingPanel,
                    meeting_id=meeting_id,
                    meeting_title=meeting_title
                )

            except Exception as e:
                messagebox.showerror(
                    "Join Meeting Error",
                    f"Unable to open Join Meeting.\n\n{e}"
                )

        else:

            try:
                JoinMeetingPage(
                    self,
                    meeting_id=meeting_id,
                    meeting_title=meeting_title
                )

            except Exception as e:
                messagebox.showerror(
                    "Join Meeting Error",
                    f"Unable to open Join Meeting.\n\n{e}"
                )

    # ==========================
    # REFRESH
    # ==========================

    def refresh(self):

        try:
            self.table.delete(
                *self.table.get_children()
            )

            meetings = get_all_meetings()

            if meetings is None:
                return

            for meeting in meetings:

                title = meeting[1] if len(meeting) > 1 else ""
                date = meeting[2] if len(meeting) > 2 else ""
                time = meeting[3] if len(meeting) > 3 else ""
                duration = meeting[4] if len(meeting) > 4 else ""
                description = meeting[5] if len(meeting) > 5 else ""

                self.table.insert(
                    "",
                    "end",
                    iid=str(meeting[0]),
                    values=(
                        title,
                        date,
                        time,
                        duration,
                        description
                    )
                )

        except Exception as e:
            messagebox.showerror(
                "Refresh Error",
                f"Unable to load meetings.\n\n{e}"
            )

    # ==========================
    # SHOW MEETING LINK
    # ==========================

    def show_meeting_link(self):

        selected = self.table.selection()

        if not selected:
            messagebox.showwarning(
                "Meeting Link",
                "Please select a meeting."
            )
            return

        try:
            meeting_id = int(selected[0])

            meetings = get_all_meetings()

            meeting_row = next(
                (
                    row
                    for row in meetings
                    if int(row[0]) == meeting_id
                ),
                None
            )

        except Exception as e:
            messagebox.showerror(
                "Meeting Link Error",
                f"Unable to find the meeting.\n\n{e}"
            )
            return

        if not meeting_row:
            messagebox.showerror(
                "Meeting Link",
                "Meeting not found."
            )
            return

        meeting_link = (
            meeting_row[6]
            if len(meeting_row) > 6
            else ""
        )

        if not meeting_link:
            messagebox.showerror(
                "Meeting Link",
                "No link is available for this meeting."
            )
            return

        meeting_title = (
            meeting_row[1]
            if len(meeting_row) > 1
            else "Meeting"
        )

        try:
            show_meeting_link_dialog(
                meeting_link,
                title=meeting_title
            )

        except Exception as e:
            messagebox.showerror(
                "Meeting Link Error",
                f"Unable to show meeting link.\n\n{e}"
            )

    # ==========================
    # OPEN MEETING ROOM
    # ==========================

    def open_meeting_room(self):

        selected = self.table.selection()

        if not selected:
            messagebox.showwarning(
                "Open Meeting Room",
                "Please select a meeting."
            )
            return

        try:
            meeting_id = int(selected[0])

            meetings = get_all_meetings()

            meeting_row = next(
                (
                    row
                    for row in meetings
                    if int(row[0]) == meeting_id
                ),
                None
            )

        except Exception as e:
            messagebox.showerror(
                "Open Meeting Room Error",
                f"Unable to find the meeting.\n\n{e}"
            )
            return

        if not meeting_row:
            messagebox.showerror(
                "Open Meeting Room",
                "Meeting not found."
            )
            return

        try:
            MeetingRoomPage(
                self,
                meeting_row
            )

        except Exception as e:
            messagebox.showerror(
                "Open Meeting Room Error",
                f"Unable to open the meeting room.\n\n{e}"
            )

    # ==========================
    # CLOSE PANEL
    # ==========================

    def close(self):

        try:
            from screens import unregister_page
            unregister_page("meetings")

        except Exception:
            pass

        try:
            self.destroy()

        except Exception:
            pass

        if callable(self.on_close):

            try:
                self.on_close()

            except Exception:
                pass


# ============================================================
# TEST / STANDALONE EXECUTION
# ============================================================

if __name__ == "__main__":

    root = ctk.CTk()

    root.withdraw()

    MeetingsPage(root)

    root.mainloop()