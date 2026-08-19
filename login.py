import customtkinter as ctk
from tkinter import messagebox

from screens.register import Register
from backend.auth import authenticate_user
from screens.dashboard import Dashboard


class LoginPage(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("MeetSphere Login")
        self.geometry("1250x725")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.close_window)
        self._closing = False

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.configure(fg_color="#0F172A")

        # =========================
        # LEFT PANEL
        # =========================

        self.left = ctk.CTkFrame(
            self,
            width=340,
            fg_color="#16213E",
            corner_radius=0
        )

        self.left.pack(side="left", fill="both")

        # =========================
        # RIGHT PANEL
        # =========================

        self.right = ctk.CTkFrame(
            self,
            fg_color="#0F172A",
            corner_radius=0
        )

        self.right.pack(side="right", expand=True, fill="both")

        # =========================
        # LOGO
        # =========================

        logo = ctk.CTkLabel(
            self.left,
            text="MeetSphere",
            font=("Arial", 36, "bold"),
            text_color="white"
        )
        logo.pack(pady=(45, 10))

        subtitle = ctk.CTkLabel(
            self.left,
            text="Enterprise Video Conferencing Platform",
            font=("Arial", 15),
            text_color="lightgray"
        )
        subtitle.pack(pady=(0, 40))

        # =========================
        # TITLE
        # =========================

        title = ctk.CTkLabel(
            self.left,
            text="Welcome Back 👋",
            font=("Arial", 28, "bold"),
            text_color="white"
        )
        title.pack()

        desc = ctk.CTkLabel(
            self.left,
            text="Sign in to continue to MeetSphere",
            font=("Arial", 14),
            text_color="gray"
        )
        desc.pack(pady=(5, 20))

        # =========================
        # USERNAME LABEL
        # =========================

        ctk.CTkLabel(
            self.left,
            text="Username",
            font=("Arial", 14, "bold"),
            text_color="white"
        ).pack(anchor="w", padx=85)

        # =========================
        # USERNAME ENTRY
        # =========================

        self.username = ctk.CTkEntry(
            self.left,
            width=340,
            height=45,
            placeholder_text="Enter Username",
            font=("Arial", 12)
        )
        self.username.pack(pady=(5, 15))

        # =========================
        # PASSWORD LABEL
        # =========================

        ctk.CTkLabel(
            self.left,
            text="Password",
            font=("Arial", 14, "bold"),
            text_color="white"
        ).pack(anchor="w", padx=85)

        # =========================
        # PASSWORD ENTRY
        # =========================

        self.password = ctk.CTkEntry(
            self.left,
            width=340,
            height=45,
            placeholder_text="Enter Password",
            show="*",
            font=("Arial", 12)
        )
        self.password.pack(pady=(5, 15))

        # =========================
        # REMEMBER ME
        # =========================

        self.remember = ctk.CTkCheckBox(
            self.left,
            text="Remember Me",
            font=("Arial", 12)
        )
        self.remember.pack(anchor="w", padx=85, pady=5)

        # =========================
        # LOGIN BUTTON
        # =========================

        login_btn = ctk.CTkButton(
            self.left,
            text="Sign In",
            width=340,
            height=45,
            corner_radius=10,
            font=("Arial", 14),
            command=self.login
        )
        login_btn.pack(pady=20)

        # =========================
        # CREATE ACCOUNT BUTTON
        # =========================

        register_btn = ctk.CTkButton(
            self.left,
            text="Create Account",
            width=340,
            height=45,
            fg_color="transparent",
            border_width=2,
            border_color="#3B82F6",
            text_color="white",
            hover_color="#1E3A8A",
            corner_radius=10,
            font=("Arial", 14),
            command=self.open_register
        )
        register_btn.pack()

        # =========================
        # FOOTER
        # =========================

        footer = ctk.CTkLabel(
            self.left,
            text="© 2026 MeetSphere Technologies",
            text_color="gray"
        )
        footer.pack(side="bottom", pady=20)

        # =========================
        # RIGHT SIDE
        # =========================

        welcome = ctk.CTkLabel(
            self.right,
            text="MeetSphere",
            font=("Arial", 42, "bold"),
            text_color="white"
        )
        welcome.pack(pady=(175, 20))

        text = ctk.CTkLabel(
            self.right,
            text="Professional Video Conferencing\n& Screen Sharing Platform",
            font=("Arial", 22),
            justify="center",
            text_color="white"
        )
        text.pack()

        features = ctk.CTkLabel(
            self.right,
            text="""
✓ HD Video Meetings

✓ Secure Screen Sharing

✓ Live Chat

✓ Team Collaboration

✓ End-to-End Encryption
""",
            justify="left",
            font=("Arial", 18),
            text_color="lightgray"
        )
        features.pack(pady=40)
# =========================
# ENTER KEY LOGIN
# =========================
        self.bind("<Return>", lambda event: self.login())
        self.username.bind("<Return>", lambda event: self.login())
        self.password.bind("<Return>", lambda event: self.login())
    # =========================
    # OPEN REGISTER PAGE
    # =========================

    def open_register(self):
        Register(self)

    # =========================
    # LOGIN
    # =========================

    def login(self):
        username = self.username.get().strip()
        password = self.password.get().strip()

        if username == "":
            messagebox.showerror(
                "Error",
                "Please enter username."
            )
            return

        if password == "":
            messagebox.showerror(
                "Error",
                "Please enter password."
            )
            return

        if authenticate_user(username, password):
            self.close_window()

            app = Dashboard(username)
            app.mainloop()

        else:
            messagebox.showerror(
                "Login Failed",
                "Invalid Username or Password."
            )

    def close_window(self):
        if self._closing:
            return

        self._closing = True
        callback_info = self.tk.call("after", "info")
        callback_ids = callback_info if isinstance(callback_info, (tuple, list)) else str(callback_info).split()
        for callback_id in callback_ids:
            try:
                self.after_cancel(callback_id)
            except Exception:
                pass

        self.quit()
        try:
            self.destroy()
        except Exception:
            self.tk.call("destroy", self._w)
