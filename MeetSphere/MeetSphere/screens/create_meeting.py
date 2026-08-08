import customtkinter as ctk
from tkinter import messagebox

try:
    import qrcode
    from PIL import Image, ImageTk
except ImportError:
    qrcode = None
    Image = None
    ImageTk = None

from backend.database import add_meeting, add_meeting_with_id


def show_meeting_link_dialog(meeting_link, title="Meeting"):
    dialog = ctk.CTkToplevel()
    dialog.title(f"{title} Link & QR")
    dialog.geometry("600x520")
    dialog.resizable(False, False)
    dialog.configure(fg_color="#F4F7FE")

    ctk.CTkLabel(
        dialog,
        text="Meeting Created",
        font=("Arial", 22, "bold")
    ).pack(pady=(20, 10))

    ctk.CTkLabel(
        dialog,
        text="Share this meeting link with participants:",
        font=("Arial", 14)
    ).pack(pady=(0, 10))

    link_entry = ctk.CTkEntry(
        dialog,
        width=540,
        state="normal"
    )
    link_entry.pack(padx=20, pady=(0, 15))
    link_entry.insert(0, meeting_link)
    link_entry.configure(state="disabled")

    if qrcode and Image and ImageTk:
        qr_code = qrcode.make(meeting_link)
        qr_code = qr_code.resize((300, 300))
        qr_image = ImageTk.PhotoImage(qr_code)
        qr_label = ctk.CTkLabel(dialog, image=qr_image, text="")
        qr_label.image = qr_image
        qr_label.pack(pady=10)
    else:
        ctk.CTkLabel(
            dialog,
            text="Install qrcode and pillow to see a QR code.",
            font=("Arial", 14),
            text_color="gray"
        ).pack(pady=40)

    ctk.CTkButton(
        dialog,
        text="Close",
        width=140,
        command=dialog.destroy
    ).pack(pady=20)

    dialog.grab_set()


class CreateMeetingPage(ctk.CTkToplevel):

    def __init__(self, parent, modal=True):
        super().__init__(parent)

        self.parent = parent
        self.modal = modal

        self.title("Create Meeting")
        self.geometry("900x700")
        self.resizable(True, True)
        try:
            self.minsize(600, 500)
        except Exception:
            pass

        self.configure(fg_color="#F4F7FE")

        # Modal behavior: hide parent and grab focus when requested
        if self.modal:
            try:
                self.parent.withdraw()
            except Exception:
                pass
            self.transient(self.parent)
            self.grab_set()
            self.protocol("WM_DELETE_WINDOW", self.back)
        else:
            # Non-modal: keep dashboard visible and only destroy on close
            self.protocol("WM_DELETE_WINDOW", self.back)

        # ==========================
        # HEADER
        # ==========================

        header = ctk.CTkFrame(self, height=70)
        header.pack(fill="x", padx=20, pady=20)
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="➕ Create Meeting",
            font=("Arial", 28, "bold")
        ).pack(side="left", padx=20)

        ctk.CTkButton(
            header,
            text="← Back",
            command=self.back
        ).pack(side="right", padx=20)

        # ==========================
        # FORM
        # ==========================

        # Use a scrollable frame so smaller screens can reach bottom controls
        frame = ctk.CTkScrollableFrame(self, corner_radius=8)
        frame.pack(fill="both", expand=True, padx=30, pady=20)

        # Meeting Name
        ctk.CTkLabel(
            frame,
            text="Meeting Name",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=25, pady=(20, 5))

        # Meeting ID (optional)
        ctk.CTkLabel(
            frame,
            text="Meeting ID (optional)",
            font=("Arial", 14)
        ).pack(anchor="w", padx=25, pady=(6, 3))

        self.meeting_id_entry = ctk.CTkEntry(
            frame,
            width=250,
            placeholder_text="Enter Meeting ID (numeric)"
        )
        self.meeting_id_entry.pack(anchor="w", padx=25)

        self.meeting_name = ctk.CTkEntry(
            frame,
            width=500,
            placeholder_text="Enter Meeting Name"
        )
        self.meeting_name.pack(anchor="w", padx=25)

        # Date
        ctk.CTkLabel(
            frame,
            text="Meeting Date",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=25, pady=(20, 5))

        self.date = ctk.CTkEntry(
            frame,
            width=500,
            placeholder_text="DD/MM/YYYY"
        )
        self.date.pack(anchor="w", padx=25)

        # Time
        ctk.CTkLabel(
            frame,
            text="Meeting Time",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=25, pady=(20, 5))

        self.time = ctk.CTkEntry(
            frame,
            width=500,
            placeholder_text="HH:MM AM/PM"
        )
        self.time.pack(anchor="w", padx=25)

        # Duration
        ctk.CTkLabel(
            frame,
            text="Duration",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=25, pady=(20, 5))

        self.duration = ctk.CTkComboBox(
            frame,
            width=250,
            values=[
                "30 Minutes",
                "45 Minutes",
                "1 Hour",
                "2 Hours"
            ]
        )
        self.duration.set("30 Minutes")
        self.duration.pack(anchor="w", padx=25)

        # Description
        ctk.CTkLabel(
            frame,
            text="Description",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=25, pady=(20, 5))

        self.description = ctk.CTkTextbox(
            frame,
            width=600,
            height=120
        )
        self.description.pack(anchor="w", padx=25)

        # Create Button (styled like Join Meeting button)
        ctk.CTkButton(
            frame,
            text="Create Meeting",
            width=220,
            height=40,
            fg_color="#2B82C0",
            hover_color="#1F6FA3",
            command=self.create_meeting
        ).pack(pady=30)

    # ===================================
    # CREATE MEETING
    # ===================================

    def create_meeting(self):

        title = self.meeting_name.get().strip()
        date = self.date.get().strip()
        time = self.time.get().strip()
        duration = self.duration.get().strip()
        description = self.description.get("1.0", "end").strip()

        if title == "" or date == "" or time == "":
            messagebox.showerror(
                "Error",
                "Please fill all required fields."
            )
            return

        meeting_id_raw = self.meeting_id_entry.get().strip()

        try:
            if meeting_id_raw:
                if not meeting_id_raw.isdigit():
                    messagebox.showerror("Error", "Meeting ID must be numeric.")
                    return

                meeting_link = add_meeting_with_id(
                    int(meeting_id_raw),
                    title,
                    date,
                    time,
                    duration,
                    description
                )
            else:
                meeting_link = add_meeting(
                    title,
                    date,
                    time,
                    duration,
                    description
                )

            messagebox.showinfo(
                "Success",
                f"Meeting created successfully!\nLink: {meeting_link}"
            )
            show_meeting_link_dialog(meeting_link, title)

            # Notify open pages to refresh (calendar, meetings)
            try:
                from screens import get_page

                cal = get_page('calendar')
                if cal:
                    try:
                        cal.refresh()
                    except Exception:
                        pass

                meetp = get_page('meetings')
                if meetp:
                    try:
                        meetp.refresh()
                    except Exception:
                        pass
            except Exception:
                pass

        except IntegrityError:
            messagebox.showerror("Error", "Meeting ID already exists. Choose a different ID.")
            return

        except Exception as e:
            messagebox.showerror("Error", f"Failed to create meeting: {e}")
            return

        # Refresh only if parent has refresh()
        if hasattr(self.parent, "refresh"):
            self.parent.refresh()

        # If modal, restore parent; if non-modal, leave parent as-is
        if self.modal:
            # Do not deiconify parent; parent remains visible
            pass

        self.destroy()

    # ===================================
    # BACK BUTTON
    # ===================================

    def back(self):
        # Do not deiconify parent; simply destroy this window
        self.destroy()


class CreateMeetingPanel(ctk.CTkFrame):
    """Embedded create-meeting panel to show inside the Dashboard main view.

    Use `parent` as the container (e.g. `dashboard.main`) and pass an optional
    `on_close` callback which will be invoked when the panel is closed.
    """

    def __init__(self, parent, dashboard=None, on_close=None, **kwargs):
        super().__init__(parent, fg_color="white", corner_radius=8)
        self.parent = parent
        self.dashboard = dashboard
        self.on_close = on_close

        header = ctk.CTkFrame(self, height=60)
        header.pack(fill="x", padx=10, pady=10)
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="➕ Create Meeting",
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

        # Meeting Name
        ctk.CTkLabel(
            body,
            text="Meeting Name",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=8, pady=(6, 3))

        self.meeting_id_entry = ctk.CTkEntry(
            body,
            width=250,
            placeholder_text="Enter Meeting ID (numeric)"
        )
        self.meeting_id_entry.pack(anchor="w", padx=8)

        self.meeting_name = ctk.CTkEntry(
            body,
            width=560,
            placeholder_text="Enter Meeting Name"
        )
        self.meeting_name.pack(anchor="w", padx=8, pady=(6, 12))

        ctk.CTkLabel(
            body,
            text="Meeting Date",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=8, pady=(6, 3))

        self.date = ctk.CTkEntry(
            body,
            width=560,
            placeholder_text="DD/MM/YYYY"
        )
        self.date.pack(anchor="w", padx=8)

        ctk.CTkLabel(
            body,
            text="Meeting Time",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=8, pady=(6, 3))

        self.time = ctk.CTkEntry(
            body,
            width=560,
            placeholder_text="HH:MM AM/PM"
        )
        self.time.pack(anchor="w", padx=8)

        ctk.CTkLabel(
            body,
            text="Duration",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=8, pady=(6, 3))

        self.duration = ctk.CTkComboBox(
            body,
            width=250,
            values=[
                "30 Minutes",
                "45 Minutes",
                "1 Hour",
                "2 Hours"
            ]
        )
        self.duration.set("30 Minutes")
        self.duration.pack(anchor="w", padx=8)

        ctk.CTkLabel(
            body,
            text="Description",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=8, pady=(6, 3))

        self.description = ctk.CTkTextbox(
            body,
            width=560,
            height=120
        )
        self.description.pack(anchor="w", padx=8, pady=(0, 12))

        # Action buttons
        btn_row = ctk.CTkFrame(body, fg_color="transparent")
        btn_row.pack(pady=10)

        ctk.CTkButton(
            btn_row,
            text="Create Meeting",
            width=220,
            height=40,
            fg_color="#2B82C0",
            hover_color="#1F6FA3",
            command=self.create_meeting
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            btn_row,
            text="Cancel",
            width=120,
            command=self.close
        ).pack(side="left", padx=8)

    def create_meeting(self):
        title = self.meeting_name.get().strip()
        date = self.date.get().strip()
        time = self.time.get().strip()
        description = self.description.get("1.0", "end").strip()

        if title == "" or date == "" or time == "":
            messagebox.showerror("Error", "Please fill all required fields.")
            return

        meeting_id_raw = self.meeting_id_entry.get().strip()

        try:
            if meeting_id_raw:
                if not meeting_id_raw.isdigit():
                    messagebox.showerror("Error", "Meeting ID must be numeric.")
                    return
                from sqlite3 import IntegrityError
                from backend.database import add_meeting_with_id

                meeting_link = add_meeting_with_id(
                    int(meeting_id_raw),
                    title,
                    date,
                    time,
                    self.duration.get(),
                    description
                )
            else:
                meeting_link = add_meeting(
                    title,
                    date,
                    time,
                    self.duration.get(),
                    description
                )

            messagebox.showinfo(
                "Success",
                f"Meeting created successfully!\nLink: {meeting_link}"
            )
            show_meeting_link_dialog(meeting_link, title)

            # Notify open pages to refresh (calendar, meetings)
            try:
                from screens import get_page

                cal = get_page('calendar')
                if cal:
                    try:
                        cal.refresh()
                    except Exception:
                        pass

                meetp = get_page('meetings')
                if meetp:
                    try:
                        meetp.refresh()
                    except Exception:
                        pass
            except Exception:
                pass

        except IntegrityError:
            messagebox.showerror("Error", "Meeting ID already exists. Choose a different ID.")
            return

        except Exception as e:
            messagebox.showerror("Error", f"Failed to create meeting: {e}")
            return

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