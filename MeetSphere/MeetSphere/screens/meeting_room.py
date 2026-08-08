import customtkinter as ctk
from tkinter import messagebox

try:
    import cv2
    from PIL import Image, ImageTk
except ImportError:
    cv2 = None
    Image = None
    ImageTk = None


class MeetingRoomPage(ctk.CTkToplevel):

    def __init__(self, parent, meeting_data, username="Guest"):
        super().__init__(parent)

        self.parent = parent
        self.meeting_data = meeting_data
        self.username = username
        self.camera_allowed = False
        self.mic_allowed = False
        self.video_capture = None
        self.video_running = False
        self.video_photo = None
        self.camera_on = True
        self.is_muted = False

        self.title("MeetSphere - Meeting Room")
        self.geometry("1300x820")
        self.resizable(True, True)
        self.configure(fg_color="#F4F7FE")
        self.protocol("WM_DELETE_WINDOW", self.close_window)

        self.build_ui()
        self.ask_permissions()

    def build_ui(self):
        header = ctk.CTkFrame(self, height=70)
        header.pack(fill="x", padx=20, pady=(15, 10))
        header.pack_propagate(False)

        meeting_title = self.meeting_data[1] if len(self.meeting_data) > 1 else "Meeting"
        ctk.CTkLabel(
            header,
            text=f"📹 {meeting_title}",
            font=("Arial", 28, "bold")
        ).pack(side="left", padx=20)

        ctk.CTkButton(
            header,
            text="Leave Meeting",
            fg_color="#EF4444",
            hover_color="#DC2626",
            command=self.close_window
        ).pack(side="right", padx=20)

        meeting_info = ctk.CTkFrame(self, fg_color="#E5E7EB", corner_radius=15)
        meeting_info.pack(fill="x", padx=20, pady=(0, 10))
        meeting_info.pack_propagate(False)

        meeting_link = self.meeting_data[6] if len(self.meeting_data) > 6 else ""
        info_text = (
            f"Meeting: {meeting_title}   "
            f"Date: {self.meeting_data[2]}   "
            f"Time: {self.meeting_data[3]}   "
            f"Link: {meeting_link}"
        )

        ctk.CTkLabel(
            meeting_info,
            text=info_text,
            font=("Arial", 14),
            text_color="#111827",
            wraplength=1200,
            justify="left"
        ).pack(anchor="w", padx=20, pady=18)

        body = ctk.CTkFrame(self, fg_color="#F4F7FE")
        body.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        left_panel = ctk.CTkFrame(body, fg_color="white", corner_radius=15)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)

        local_label = ctk.CTkLabel(
            left_panel,
            text="Your Camera",
            font=("Arial", 18, "bold")
        )
        local_label.pack(anchor="w", padx=20, pady=(20, 10))

        self.video_frame = ctk.CTkFrame(
            left_panel,
            width=640,
            height=360,
            corner_radius=15,
            fg_color="#0F172A"
        )
        self.video_frame.pack(padx=20, pady=(0, 15))
        self.video_frame.pack_propagate(False)

        self.video_label = ctk.CTkLabel(
            self.video_frame,
            text="Camera preview will appear here.",
            font=("Arial", 16),
            text_color="gray"
        )
        self.video_label.pack(expand=True)

        self.status_label = ctk.CTkLabel(
            left_panel,
            text="Camera: waiting for permission...   Microphone: waiting for permission...",
            font=("Arial", 14),
            text_color="#374151",
            wraplength=600,
            justify="left"
        )
        self.status_label.pack(anchor="w", padx=20, pady=(10, 20))

        controls = ctk.CTkFrame(left_panel, fg_color="transparent")
        controls.pack(padx=20, pady=(0, 20))

        ctk.CTkButton(
            controls,
            text="🎤 Mute / Unmute",
            width=150,
            command=self.toggle_mute
        ).grid(row=0, column=0, padx=10, pady=10)

        ctk.CTkButton(
            controls,
            text="📷 Camera On/Off",
            width=150,
            command=self.toggle_camera
        ).grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkButton(
            controls,
            text="🖥 Share Screen",
            width=150,
            command=self.share_screen
        ).grid(row=0, column=2, padx=10, pady=10)

        right_panel = ctk.CTkFrame(body, fg_color="white", corner_radius=15)
        right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0), pady=10)

        ctk.CTkLabel(
            right_panel,
            text="Participants",
            font=("Arial", 18, "bold")
        ).pack(anchor="w", padx=20, pady=(20, 10))

        participant_grid = ctk.CTkFrame(right_panel, fg_color="#F8FAFC", corner_radius=15)
        participant_grid.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(
            participant_grid,
            text="Participant Cameras",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=15, pady=(12, 10))

        grid_body = ctk.CTkFrame(participant_grid, fg_color="transparent")
        grid_body.pack(fill="x", padx=15, pady=(0, 15))

        self.add_participant_tile(grid_body, "Alice", "Online", row=0, column=0)
        self.add_participant_tile(grid_body, "Michael", "Online", row=0, column=1)
        self.add_participant_tile(grid_body, "Sarah", "Online", row=1, column=0)
        self.add_participant_tile(grid_body, "David", "In a Meeting", row=1, column=1)

        self.participant_area = ctk.CTkScrollableFrame(right_panel, fg_color="transparent", corner_radius=0)
        self.participant_area.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.add_participant_tile(self.participant_area, "Alice", "Online")
        self.add_participant_tile(self.participant_area, "Michael", "Online")
        self.add_participant_tile(self.participant_area, "Sarah", "Online")
        self.add_participant_tile(self.participant_area, "David", "In a Meeting")

    def add_participant_tile(self, parent, name, status, row=None, column=None):
        frame = ctk.CTkFrame(parent, fg_color="#E5E7EB", corner_radius=15)
        if row is not None and column is not None:
            frame.grid(row=row, column=column, padx=8, pady=8, sticky="nsew")
            parent.grid_columnconfigure(column, weight=1)
            frame.grid_propagate(False)
            frame.configure(width=260, height=170)
        else:
            frame.pack(fill="x", pady=8)

        placeholder = ctk.CTkFrame(frame, fg_color="#0F172A", corner_radius=12, width=220, height=100)
        placeholder.pack(padx=15, pady=(15, 5))
        placeholder.pack_propagate(False)

        ctk.CTkLabel(
            placeholder,
            text="👤",
            font=("Arial", 30),
            text_color="white"
        ).pack(expand=True)

        ctk.CTkLabel(
            frame,
            text=f"{name}",
            font=("Arial", 15, "bold")
        ).pack(anchor="w", padx=15, pady=(5, 2))

        ctk.CTkLabel(
            frame,
            text=f"Status: {status}",
            font=("Arial", 13),
            text_color="#4B5563"
        ).pack(anchor="w", padx=15, pady=(0, 15))

    def ask_permissions(self):
        self.camera_allowed = messagebox.askyesno(
            "Camera Permission",
            "MeetSphere needs permission to use your camera. Allow camera access?"
        )

        self.mic_allowed = messagebox.askyesno(
            "Microphone Permission",
            "MeetSphere needs permission to use your microphone. Allow microphone access?"
        )

        self.update_status_label()

        if self.camera_allowed:
            self.start_camera()
        else:
            self.video_label.configure(text="Camera permission denied. Enable camera to start video.")

        if not self.mic_allowed:
            messagebox.showinfo(
                "Microphone",
                "Microphone permissions were not granted. You can still use the meeting UI without audio."
            )

    def update_status_label(self):
        camera_text = "Enabled" if self.camera_allowed and self.camera_on else "Disabled"
        mic_text = "Enabled" if self.mic_allowed and not self.is_muted else "Muted" if self.mic_allowed else "Disabled"
        self.status_label.configure(
            text=f"Camera: {camera_text}   Microphone: {mic_text}"
        )

    def start_camera(self):
        if cv2 is None or Image is None or ImageTk is None:
            self.video_label.configure(
                text="OpenCV / Pillow is not installed. Install opencv-python and pillow to enable camera preview."
            )
            return

        self.video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        if not self.video_capture.isOpened():
            self.video_label.configure(
                text="Unable to open the camera. Check your device and make sure it is connected."
            )
            return

        self.video_running = True
        self.update_camera()

    def update_camera(self):
        if not self.video_running or self.video_capture is None:
            return

        ret, frame = self.video_capture.read()
        if ret and self.camera_on:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (640, 360))
            image = Image.fromarray(frame)
            self.video_photo = ImageTk.PhotoImage(image)
            self.video_label.configure(image=self.video_photo, text="")
        else:
            if self.camera_on:
                self.video_label.configure(text="Waiting for camera feed...")

        self.after(30, self.update_camera)

    def toggle_camera(self):
        if not self.camera_allowed:
            self.ask_permissions()
            return

        self.camera_on = not self.camera_on
        self.update_status_label()

        if self.camera_on and self.video_capture is None:
            self.start_camera()
        elif not self.camera_on:
            self.video_label.configure(text="Camera is turned off.")

    def toggle_mute(self):
        if not self.mic_allowed:
            self.ask_permissions()
            return

        self.is_muted = not self.is_muted
        self.update_status_label()
        messagebox.showinfo(
            "Microphone",
            "Microphone muted." if self.is_muted else "Microphone unmuted."
        )

    def share_screen(self):
        messagebox.showinfo(
            "Share Screen",
            "Screen sharing started. In this demo, screen sharing is simulated in the meeting room."
        )

    def close_window(self):
        if self.video_capture is not None:
            try:
                self.video_running = False
                self.video_capture.release()
            except Exception:
                pass

        self.destroy()
