import customtkinter as ctk
from tkinter import messagebox
from sqlite3 import IntegrityError

from backend.auth import create_user


class Register(ctk.CTkToplevel):

    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        self.title("Create MeetSphere Account")
        self.geometry("500x650")
        self.resizable(False, False)

        self.configure(fg_color="#0F172A")

        # Make this window modal
        self.grab_set()

        # Close properly
        self.protocol("WM_DELETE_WINDOW", self.close_window)

        # ==========================
        # TITLE
        # ==========================

        ctk.CTkLabel(
            self,
            text="Create Account",
            font=("Arial", 28, "bold")
        ).pack(pady=25)

        # ==========================
        # FULL NAME
        # ==========================

        self.name = ctk.CTkEntry(
            self,
            width=320,
            height=45,
            placeholder_text="Full Name"
        )
        self.name.pack(pady=10)

        # ==========================
        # EMAIL
        # ==========================

        self.email = ctk.CTkEntry(
            self,
            width=320,
            height=45,
            placeholder_text="Email Address"
        )
        self.email.pack(pady=10)

        # ==========================
        # USERNAME
        # ==========================

        self.username = ctk.CTkEntry(
            self,
            width=320,
            height=45,
            placeholder_text="Username"
        )
        self.username.pack(pady=10)

        # ==========================
        # PASSWORD
        # ==========================

        self.password = ctk.CTkEntry(
            self,
            width=320,
            height=45,
            placeholder_text="Password",
            show="*"
        )
        self.password.pack(pady=10)

        # ==========================
        # CONFIRM PASSWORD
        # ==========================

        self.confirm = ctk.CTkEntry(
            self,
            width=320,
            height=45,
            placeholder_text="Confirm Password",
            show="*"
        )
        self.confirm.pack(pady=10)

        # ==========================
        # CREATE ACCOUNT BUTTON
        # ==========================

        ctk.CTkButton(
            self,
            text="Create Account",
            width=320,
            height=45,
            command=self.register
        ).pack(pady=20)

        # ==========================
        # ENTER KEY SUPPORT
        # ==========================

        self.bind("<Return>", lambda event: self.register())

        self.name.bind("<Return>", lambda event: self.register())
        self.email.bind("<Return>", lambda event: self.register())
        self.username.bind("<Return>", lambda event: self.register())
        self.password.bind("<Return>", lambda event: self.register())
        self.confirm.bind("<Return>", lambda event: self.register())

        # Focus on first field
        self.name.focus()

    # ==========================
    # REGISTER
    # ==========================

    def register(self):

        name = self.name.get().strip()
        email = self.email.get().strip()
        username = self.username.get().strip()
        password = self.password.get().strip()
        confirm = self.confirm.get().strip()

        if name == "":
            messagebox.showerror("Error", "Please enter your full name.")
            return

        if email == "":
            messagebox.showerror("Error", "Please enter your email.")
            return

        if username == "":
            messagebox.showerror("Error", "Please enter a username.")
            return

        if password == "":
            messagebox.showerror("Error", "Please enter a password.")
            return

        if confirm == "":
            messagebox.showerror("Error", "Please confirm your password.")
            return

        if password != confirm:
            messagebox.showerror(
                "Error",
                "Passwords do not match."
            )
            return

        try:

            create_user(
                name,
                email,
                username,
                password
            )

            messagebox.showinfo(
                "Success",
                "Account created successfully!"
            )

            self.destroy()

        except IntegrityError:
            messagebox.showerror(
                "Error",
                "Username already exists."
            )

        except Exception as e:
            messagebox.showerror(
                "Database Error",
                str(e)
            )

    # ==========================
    # CLOSE WINDOW
    # ==========================

    def close_window(self):
        self.destroy()