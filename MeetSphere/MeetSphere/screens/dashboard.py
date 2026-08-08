import customtkinter as ctk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from backend.database import get_all_meetings, get_user, get_user_settings
from screens.meetings import MeetingsPanel
from screens.calendar_page import CalendarPanel
from screens.messages import MessagesPanel
from screens.screenshare import ScreenSharePanel
from screens.participants import ParticipantsPanel
from screens.analytics import AnalyticsPanel
from screens.settings_page import SettingsPanel
from screens.profile import ProfilePanel
from screens.notifications import NotificationsPanel
from screens.create_meeting import CreateMeetingPanel
from screens.join_meeting import JoinMeetingPanel
from screens.invite_members import InviteMembersPanel

class Dashboard(ctk.CTk):

    # ===========================
    # CONSTRUCTOR
    # ===========================
    def __init__(self, username="John Doe"):
        super().__init__()
        self.title("MeetSphere Dashboard")
        # Default window size
        self.geometry("1450x850")
        self.resizable(False, False)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.configure(fg_color="#F4F7FE")
        self.username = username
        self.is_muted = False
        self.camera_on = True

        # ==========================
        # SIDEBAR
        # ==========================
        sidebar = ctk.CTkFrame(
            self,
            width=220,
            fg_color="#0B1F3A",
            corner_radius=0
        )
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ctk.CTkLabel(
            sidebar,
            text="MeetSphere",
            font=("Arial", 28, "bold"),
            text_color="white"
        ).pack(pady=(25, 30))

        commands = {
            "🏠 Dashboard": self.dashboard_page,
            "📹 Meetings": self.meetings_page,
            "📅 Calendar": self.calendar_page,
            "💬 Messages": self.messages_page,
            "🖥 Screen Share": self.screenshare_page,
            "👥 Participants": self.participants_page,
            "📊 Analytics": self.analytics_page,
            "⚙ Settings": self.settings_page
        }

        for item, cmd in commands.items():
            ctk.CTkButton(
                sidebar,
                text=item,
                width=180,
                height=42,
                fg_color="#12386A",
                hover_color="#2563EB",
                anchor="w",
                command=cmd
            ).pack(pady=6)

        # Logout Button
        logout = ctk.CTkButton(
            sidebar,
            text="🚪 Logout",
            fg_color="#EF4444",
            hover_color="#DC2626",
            width=180,
            height=40,
            command=self.logout
        )
        logout.pack(side="bottom", pady=20)

        # Profile Frame in Sidebar
        profile_frame = ctk.CTkFrame(
            sidebar,
            fg_color="#1F2A44",
            corner_radius=10,
            width=180,
            height=80
        )
        profile_frame.pack(side="bottom", pady=15, padx=10)
        profile_frame.pack_propagate(False)

        avatar = ctk.CTkLabel(
            profile_frame,
            text="👤",
            font=("Arial", 30)
        )
        avatar.pack(side="left", padx=10)

        user_info = ctk.CTkFrame(
            profile_frame,
            fg_color="transparent"
        )
        user_info.pack(side="left", pady=10)

        ctk.CTkLabel(
            user_info,
            text=username,
            font=("Arial", 14, "bold"),
            text_color="white"
        ).pack(anchor="w")

        ctk.CTkLabel(
            user_info,
            text="john@example.com",
            font=("Arial", 11),
            text_color="#D1D5DB"
        ).pack(anchor="w")

        # ==========================
        # MAIN FRAME & SCROLL AREA
        # ==========================
        self.main_container = ctk.CTkFrame(
            self,
            fg_color="#F4F7FE"
        )
        self.main_container.pack(
            side="right",
            expand=True,
            fill="both"
        )

        # Top Bar (Fixed)
        topbar = ctk.CTkFrame(
            self.main_container,
            height=70,
            fg_color="white",
            corner_radius=15
        )
        topbar.pack(fill="x", padx=20, pady=(5, 10))
        topbar.pack_propagate(False)

        search = ctk.CTkEntry(
            topbar,
            width=350,
            height=40,
            placeholder_text="🔍 Search meetings..."
        )
        search.pack(side="left", padx=20, pady=15)
        self.search_entry = search

        ctk.CTkButton(
            topbar,
            text="Search",
            width=80,
            command=self.search_meeting
        ).pack(side="left", padx=10)

        profile_btn = ctk.CTkButton(
            topbar,
            text="👤",
            width=40,
            fg_color="transparent",
            text_color="black",
            command=self.profile
        )
        profile_btn.pack(side="right")

        settings_btn = ctk.CTkButton(
            topbar,
            text="⚙",
            width=40,
            fg_color="transparent",
            text_color="black",
            command=self.settings_page
        )
        settings_btn.pack(side="right")

        notify_btn = ctk.CTkButton(
            topbar,
            text="🔔",
            width=40,
            fg_color="transparent",
            text_color="black",
            command=self.notification
        )
        notify_btn.pack(side="right", padx=10)

        # Maximize / Restore (middle) button
        maximize_btn = ctk.CTkButton(
            topbar,
            text="▢",
            width=40,
            fg_color="transparent",
            text_color="black",
            command=self.toggle_maximize
        )
        maximize_btn.pack(side="right", padx=6)

        # Scrollable View for Dashboard Content
        self.main = ctk.CTkScrollableFrame(
            self.main_container,
            fg_color="#F4F7FE"
        )
        self.main.pack(fill="both", expand=True, padx=10, pady=(0, 0))

        # area where embedded panels will be placed
        self.panel_holder = ctk.CTkFrame(self.main, fg_color="transparent")
        self.panel_holder.pack(fill="both", expand=False, padx=20, pady=(0, 10))

        self.dashboard_content = ctk.CTkFrame(self.main, fg_color="#F4F7FE")
        self.dashboard_content.pack(fill="both", expand=True, padx=0, pady=0)

        self._embedded_panel = None

        # Welcome Section
        ctk.CTkLabel(
            self.dashboard_content,
            text=f"Good Morning, {username}! 👋",
            font=("Arial", 30, "bold"),
            text_color="#1F2937"
        ).pack(anchor="w", padx=30)

        ctk.CTkLabel(
            self.dashboard_content,
            text="Here's what's happening with your team today.",
            font=("Arial", 15),
            text_color="gray"
        ).pack(anchor="w", padx=30, pady=(0, 20))

        # ===========================
        # QUICK ACTIONS
        # ===========================
        action_frame = ctk.CTkFrame(
            self.dashboard_content,
            fg_color="white",
            corner_radius=15
        )
        action_frame.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            action_frame,
            text="Quick Actions",
            font=("Arial", 22, "bold")
        ).pack(pady=15)

        button_frame = ctk.CTkFrame(
            action_frame,
            fg_color="transparent"
        )
        button_frame.pack(pady=10)

        ctk.CTkButton(
            button_frame,
            text="➕ Create Meeting",
            width=180,
            command=self.create_meeting
        ).grid(row=0, column=0, padx=10, pady=8)

        ctk.CTkButton(
            button_frame,
            text="📹 Join Meeting",
            width=180,
            command=self.join_meeting
        ).grid(row=0, column=1, padx=10, pady=8)

        ctk.CTkButton(
            button_frame,
            text="🖥 Share Screen",
            width=180,
            command=self.share_screen
        ).grid(row=1, column=0, padx=10, pady=8)

        ctk.CTkButton(
            button_frame,
            text="👥 Invite Members",
            width=180,
            command=self.invite_members
        ).grid(row=1, column=1, padx=10, pady=8)

        # ===========================
        # RECENT ACTIVITY
        # ===========================
        activity_frame = ctk.CTkFrame(
            self.dashboard_content,
            fg_color="white",
            corner_radius=15
        )
        activity_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            activity_frame,
            text="📝 Recent Activity",
            font=("Arial", 20, "bold"),
            text_color="black"
        ).pack(anchor="w", padx=20, pady=(15, 10))

        activities = [
            "✅ Project Review meeting completed",
            "📹 Team Standup meeting created",
            "👤 Rahul joined Client Meeting",
            "🖥 Screen sharing started",
            "📄 Meeting report downloaded",
            "🔔 Reminder sent to participants",
            "🎥 Recording uploaded successfully",
            "👥 New participant added"
        ]

        for activity in activities:
            ctk.CTkLabel(
                activity_frame,
                text=activity,
                font=("Arial", 15),
                text_color="gray20"
            ).pack(anchor="w", padx=30, pady=3)

        # ===========================
        # VIDEO CONFERENCE CONTROLS
        # ===========================
        video_frame = ctk.CTkFrame(
            self.dashboard_content,
            fg_color="white",
            corner_radius=15
        )
        video_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            video_frame,
            text="🎥 Video Conference Controls",
            font=("Arial", 20, "bold")
        ).pack(pady=10)

        controls = ctk.CTkFrame(video_frame, fg_color="transparent")
        controls.pack(pady=10)

        ctk.CTkButton(
            controls,
            text="🎤 Mute",
            width=130,
            command=self.toggle_mute
        ).grid(row=0, column=0, padx=10)

        ctk.CTkButton(
            controls,
            text="📷 Camera",
            width=130,
            command=self.toggle_camera
        ).grid(row=0, column=1, padx=10)

        ctk.CTkButton(
            controls,
            text="🖥 Share Screen",
            width=150,
            command=self.share_screen
        ).grid(row=0, column=2, padx=10)

        ctk.CTkButton(
            controls,
            text="📞 End Call",
            fg_color="red",
            hover_color="#B91C1C",
            width=130,
            command=self.end_call
        ).grid(row=0, column=3, padx=10)

        # ===========================
        # LIVE CHAT PANEL
        # ===========================
        chat_frame = ctk.CTkFrame(
            self.dashboard_content,
            fg_color="white",
            corner_radius=15
        )
        chat_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            chat_frame,
            text="💬 Live Meeting Chat",
            font=("Arial", 20, "bold")
        ).pack(pady=10)

        chat_box = ctk.CTkTextbox(
            chat_frame,
            width=900,
            height=180
        )
        chat_box.pack(padx=20, pady=10)

        chat_box.insert(
            "end",
            "John: Good Morning Everyone!\n\n"
            "Sarah: Presentation is ready.\n\n"
            "Michael: Waiting for client.\n\n"
            "Emily: Meeting starts in 5 minutes.\n"
        )

        message = ctk.CTkEntry(
            chat_frame,
            placeholder_text="Type a message..."
        )
        message.pack(fill="x", padx=20, pady=10)

        ctk.CTkButton(
            chat_frame,
            text="Send Message"
        ).pack(pady=10)

        # ===========================
        # SCREEN SHARING STATUS
        # ===========================
        screen_frame = ctk.CTkFrame(
            self.dashboard_content,
            fg_color="white",
            corner_radius=15
        )
        screen_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            screen_frame,
            text="🖥 Screen Sharing",
            font=("Arial", 20, "bold")
        ).pack(pady=10)

        ctk.CTkLabel(
            screen_frame,
            text="Current Presenter : John Doe",
            font=("Arial", 16)
        ).pack()

        ctk.CTkProgressBar(
            screen_frame,
            width=500
        ).pack(pady=15)

        # ======================================================
        # CALENDAR
        # ======================================================
        calendar_frame = ctk.CTkFrame(
            self.dashboard_content,
            fg_color="white",
            corner_radius=15
        )
        calendar_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            calendar_frame,
            text="📅 Meeting Calendar",
            font=("Arial", 20, "bold")
        ).pack(pady=10)

        calendar_text = (
            "01 - Project Review\n"
            "03 - Client Meeting\n"
            "07 - Team Standup\n"
            "12 - Product Demo\n"
            "18 - Sprint Planning\n"
            "25 - HR Meeting"
        )

        ctk.CTkLabel(
            calendar_frame,
            text=calendar_text,
            justify="left",
            font=("Arial", 15)
        ).pack(anchor="w", padx=20, pady=10)

        # ======================================================
        # NOTIFICATIONS
        # ======================================================
        notification_frame = ctk.CTkFrame(
            self.dashboard_content,
            fg_color="white",
            corner_radius=15
        )
        notification_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            notification_frame,
            text="🔔 Notifications",
            font=("Arial", 20, "bold")
        ).pack(pady=10)

        notifications = [
            "✔ Team meeting starts in 15 minutes",
            "✔ Sarah shared her screen",
            "✔ John uploaded Meeting Notes",
            "✔ Client Meeting scheduled at 4:30 PM"
        ]

        for note in notifications:
            ctk.CTkLabel(
                notification_frame,
                text=note,
                font=("Arial", 15)
            ).pack(anchor="w", padx=20, pady=3)

        # ======================================================
        # USER PROFILE PANEL
        # ======================================================
        user_profile_frame = ctk.CTkFrame(
            self.dashboard_content,
            fg_color="white",
            corner_radius=15
        )
        user_profile_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            user_profile_frame,
            text="👤 User Profile Details",
            font=("Arial", 20, "bold")
        ).pack(pady=10)

        user = get_user(username) or ()
        user_settings = get_user_settings(username) or ()
        user_email = user_settings[6] if len(user_settings) > 6 and user_settings[6] else (user[2] if len(user) > 2 else "admin@meetsphere.com")

        ctk.CTkLabel(
            user_profile_frame,
            text=f"Name : {username}",
            font=("Arial", 15)
        ).pack(anchor="w", padx=20)

        ctk.CTkLabel(
            user_profile_frame,
            text=f"Email : {user_email}",
            font=("Arial", 15)
        ).pack(anchor="w", padx=20)

        ctk.CTkLabel(
            user_profile_frame,
            text="Role : Administrator",
            font=("Arial", 15)
        ).pack(anchor="w", padx=20, pady=(0, 10))

        # ======================================================
        # SETTINGS PANEL
        # ======================================================
        settings_frame = ctk.CTkFrame(
            self.dashboard_content,
            fg_color="white",
            corner_radius=15
        )
        settings_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            settings_frame,
            text="⚙ Settings",
            font=("Arial", 20, "bold")
        ).pack(pady=10)

        mic_var = ctk.BooleanVar(value=True)
        cam_var = ctk.BooleanVar(value=True)

        ctk.CTkCheckBox(
            settings_frame,
            text="Enable Microphone",
            variable=mic_var
        ).pack(anchor="w", padx=20)

        ctk.CTkCheckBox(
            settings_frame,
            text="Enable Camera",
            variable=cam_var
        ).pack(anchor="w", padx=20)

        theme_switch = ctk.CTkSwitch(
            settings_frame,
            text="Dark Mode"
        )
        theme_switch.pack(anchor="w", padx=20, pady=10)

        # ===========================
        # UPCOMING MEETINGS
        # ===========================
        meeting_frame = ctk.CTkFrame(
            self.dashboard_content,
            fg_color="white",
            corner_radius=15
        )
        meeting_frame.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            meeting_frame,
            text="Upcoming Meetings",
            font=("Arial", 22, "bold")
        ).pack(anchor="w", padx=20, pady=10)

        meeting_data = [
            ("👨", "Project Review", "9:00 AM - 10:00 AM"),
            ("👩", "Team Standup", "11:00 AM - 11:30 AM"),
            ("👨", "Client Presentation", "2:00 PM - 3:00 PM"),
            ("👩", "Design Discussion", "4:00 PM - 5:00 PM")
        ]

        for icon, title, time_slot in meeting_data:
            row = ctk.CTkFrame(
                meeting_frame,
                fg_color="transparent"
            )
            row.pack(fill="x", padx=15, pady=6)

            ctk.CTkLabel(
                row,
                text=icon,
                font=("Arial", 24)
            ).pack(side="left")

            info = ctk.CTkFrame(
                row,
                fg_color="transparent"
            )
            info.pack(side="left", padx=10)

            ctk.CTkLabel(
                info,
                text=title,
                font=("Arial", 15, "bold")
            ).pack(anchor="w")

            ctk.CTkLabel(
                info,
                text=time_slot,
                text_color="gray"
            ).pack(anchor="w")

            ctk.CTkButton(
                row,
                text="Join",
                width=70,
                height=30,
                command=self.join_meeting
            ).pack(side="right")

        # ===========================
        # RECENT MEETINGS TABLE
        # ===========================
        table_frame = ctk.CTkFrame(
            self.dashboard_content,
            fg_color="white",
            corner_radius=15
        )
        table_frame.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            table_frame,
            text="Recent Meetings",
            font=("Arial", 22, "bold")
        ).pack(anchor="w", padx=20, pady=15)

        table = ttk.Treeview(
            table_frame,
            columns=("Meeting", "Date", "Participants", "Duration", "Action"),
            show="headings",
            height=5
        )

        table.heading("Meeting", text="Meeting Name")
        table.heading("Date", text="Date")
        table.heading("Participants", text="Participants")
        table.heading("Duration", text="Duration")
        table.heading("Action", text="Action")

        table.column("Meeting", width=250, anchor="center")
        table.column("Date", width=150, anchor="center")
        table.column("Participants", width=120, anchor="center")
        table.column("Duration", width=120, anchor="center")
        table.column("Action", width=100, anchor="center")

        meetings = [
            ("Project Review", "May 24, 2024", "8", "45 min", "View"),
            ("Team Standup", "May 24, 2024", "6", "30 min", "View"),
            ("Client Presentation", "May 23, 2024", "12", "60 min", "View"),
            ("Design Discussion", "May 23, 2024", "5", "40 min", "View")
        ]

        for meeting in meetings:
            table.insert("", "end", values=meeting)

        table.pack(fill="x", padx=15, pady=10)

        # ===========================
        # TEAM MEMBERS ONLINE
        # ===========================
        members_frame = ctk.CTkFrame(
            self.dashboard_content,
            fg_color="white",
            corner_radius=15
        )
        members_frame.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            members_frame,
            text="Team Members Online",
            font=("Arial", 22, "bold")
        ).pack(anchor="w", padx=20, pady=15)

        members = [
            ("👩", "Sarah Johnson", "Online", "🟢"),
            ("👨", "Michael Brown", "Online", "🟢"),
            ("👩", "Emily Davis", "Online", "🟢"),
            ("👨", "David Wilson", "In a Meeting", "🟢")
        ]

        for avatar_icon, name, status, dot in members:
            row = ctk.CTkFrame(
                members_frame,
                fg_color="transparent"
            )
            row.pack(fill="x", padx=15, pady=8)

            ctk.CTkLabel(
                row,
                text=avatar_icon,
                font=("Arial", 24)
            ).pack(side="left")

            info = ctk.CTkFrame(
                row,
                fg_color="transparent"
            )
            info.pack(side="left", padx=10)

            ctk.CTkLabel(
                info,
                text=name,
                font=("Arial", 15, "bold")
            ).pack(anchor="w")

            ctk.CTkLabel(
                info,
                text=status,
                text_color="gray",
                font=("Arial", 12)
            ).pack(anchor="w")

            ctk.CTkLabel(
                row,
                text=dot,
                text_color="green",
                font=("Arial", 18)
            ).pack(side="right", padx=10)

        ctk.CTkButton(
            members_frame,
            text="View All",
            width=120,
            height=35,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=self.participants_page
        ).pack(pady=15)

    # ===========================
    # BUTTON FUNCTIONS
    # ===========================
    def create_meeting(self):
        self.show_panel(CreateMeetingPanel)

    def join_meeting(self):
        self.show_panel(JoinMeetingPanel)

    def share_screen(self):
        self.show_panel(ScreenSharePanel)

    def invite_members(self):
        self.show_panel(InviteMembersPanel)

    def dashboard_page(self):
        self.clear_panel()

    def meetings_page(self):
        self.show_panel(MeetingsPanel)

    def calendar_page(self):
        self.show_panel(CalendarPanel)

    def messages_page(self):
        self.show_panel(MessagesPanel)

    def screenshare_page(self):
        self.show_panel(ScreenSharePanel)

    def participants_page(self):
        self.show_panel(ParticipantsPanel)

    def analytics_page(self):
        self.show_panel(AnalyticsPanel)

    def settings_page(self):
        self.show_panel(SettingsPanel, username=self.username)

    def profile(self):
        self.show_panel(ProfilePanel, username=self.username)

    def notification(self):
        self.show_panel(NotificationsPanel)

    def logout(self):
        from screens.login import LoginPage

        self.destroy()
        LoginPage().mainloop()

    def show_panel(self, panel_class, **kwargs):
        self.clear_panel()
        self.dashboard_content.pack_forget()
        self.panel_holder.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        panel = panel_class(self.panel_holder, dashboard=self, on_close=self.clear_panel, **kwargs)
        panel.pack(fill="both", expand=True, padx=0, pady=0)
        self._embedded_panel = panel

    def clear_panel(self):
        if self._embedded_panel:
            try:
                self._embedded_panel.destroy()
            except Exception:
                pass
            self._embedded_panel = None
        self.dashboard_content.pack(fill="both", expand=True, padx=0, pady=0)

    def search_meeting(self):
        query = self.search_entry.get().strip()

        if query == "":
            messagebox.showinfo(
                "Search",
                "Please enter a meeting title to search."
            )
            return

        meetings = get_all_meetings()
        results = [meeting for meeting in meetings if query.lower() in meeting[1].lower()]

        if not results:
            messagebox.showinfo(
                "Search Results",
                "No meetings found."
            )
            return

        result_text = "\n".join(
            f"{meeting[0]} - {meeting[1]} ({meeting[2]} at {meeting[3]})"
            for meeting in results
        )

        messagebox.showinfo(
            "Search Results",
            result_text
        )

    def toggle_mute(self):
        self.is_muted = not self.is_muted
        status = "Muted" if self.is_muted else "Unmuted"

        messagebox.showinfo(
            "Microphone",
            f"Microphone {status}."
        )

    def toggle_camera(self):
        self.camera_on = not self.camera_on
        status = "Enabled" if self.camera_on else "Disabled"

        messagebox.showinfo(
            "Camera",
            f"Camera {status}."
        )

    def end_call(self):
        messagebox.showinfo(
            "Call",
            "Call ended."
        )

    def toggle_maximize(self):
        # Toggle between maximized and normal window states.
        try:
            if str(self.state()) == 'zoomed':
                self.state('normal')
            else:
                self.state('zoomed')
        except Exception:
            # Fallback: toggle between default geometry and current
            try:
                if hasattr(self, '_is_max') and self._is_max:
                    self.geometry('1450x850')
                    self._is_max = False
                else:
                    self._prev_geom = self.geometry()
                    self.state('zoomed')
                    self._is_max = True
            except Exception:
                pass

if __name__ == "__main__":
    app = Dashboard(username="John Doe")
    app.mainloop()