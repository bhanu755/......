import customtkinter as ctk
from tkinter import messagebox


class MessagesPage(ctk.CTkToplevel):

    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        self.title("MeetSphere - Messages")
        self.geometry("1200x700")
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
            text="💬 Messages",
            font=("Arial", 28, "bold")
        ).pack(side="left", padx=20)

        ctk.CTkButton(
            header,
            text="← Back to Dashboard",
            command=self.close_window
        ).pack(side="right", padx=20)

        # ==========================
        # CHAT DISPLAY
        # ==========================

        self.chatbox = ctk.CTkTextbox(
            self,
            width=1100,
            height=450
        )
        self.chatbox.pack(padx=20, pady=10)
        self.chatbox.configure(state="disabled")

        self.chat_history = [
            "John: Good Morning Team!",
            "Sarah: Presentation is ready.",
            "Michael: Client joined the meeting.",
            "Emily: I'll share my screen shortly."
        ]
        self.load_chat_history()

        # ==========================
        # MESSAGE ENTRY
        # ==========================

        bottom = ctk.CTkFrame(self)
        bottom.pack(fill="x", padx=20, pady=10)

        self.message_entry = ctk.CTkEntry(
            bottom,
            placeholder_text="Type your message...",
            width=900
        )
        self.message_entry.pack(side="left", padx=10, pady=10)

        ctk.CTkButton(
            bottom,
            text="Send",
            width=120,
            command=self.send_message
        ).pack(side="right", padx=10)

    # ==========================
    # SEND MESSAGE
    # ==========================

    def load_chat_history(self):
        self.chatbox.configure(state="normal")
        self.chatbox.delete("1.0", "end")

        for line in self.chat_history:
            self.chatbox.insert("end", f"{line}\n\n")

        self.chatbox.configure(state="disabled")

    def send_message(self):
        msg = self.message_entry.get().strip()

        if msg == "":
            return

        self.chat_history.append(f"You: {msg}")
        self.load_chat_history()
        self.message_entry.delete(0, "end")

    # ==========================
    # CLOSE WINDOW
    # ==========================

    def close_window(self):
        # Do not deiconify parent; simply destroy this window
        self.destroy()


class MessagesPanel(ctk.CTkFrame):

    def __init__(self, parent, dashboard=None, on_close=None, **kwargs):
        super().__init__(parent, fg_color="white", corner_radius=15)
        self.dashboard = dashboard
        self.on_close = on_close

        header = ctk.CTkFrame(self, height=70)
        header.pack(fill="x", padx=20, pady=20)
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="💬 Messages",
            font=("Arial", 28, "bold")
        ).pack(side="left", padx=20)

        ctk.CTkButton(
            header,
            text="Close",
            fg_color="#EF4444",
            hover_color="#DC2626",
            command=self.close
        ).pack(side="right", padx=20)

        self.chatbox = ctk.CTkTextbox(
            self,
            width=1100,
            height=450
        )
        self.chatbox.pack(padx=20, pady=10)
        self.chatbox.configure(state="disabled")

        self.chat_history = [
            "John: Good Morning Team!",
            "Sarah: Presentation is ready.",
            "Michael: Client joined the meeting.",
            "Emily: I'll share my screen shortly."
        ]
        self.load_chat_history()

        bottom = ctk.CTkFrame(self)
        bottom.pack(fill="x", padx=20, pady=10)

        self.message_entry = ctk.CTkEntry(
            bottom,
            placeholder_text="Type your message...",
            width=900
        )
        self.message_entry.pack(side="left", padx=10, pady=10)

        ctk.CTkButton(
            bottom,
            text="Send",
            width=120,
            command=self.send_message
        ).pack(side="right", padx=10)

    def load_chat_history(self):
        self.chatbox.configure(state="normal")
        self.chatbox.delete("1.0", "end")

        for line in self.chat_history:
            self.chatbox.insert("end", f"{line}\n\n")

        self.chatbox.configure(state="disabled")

    def send_message(self):
        msg = self.message_entry.get().strip()

        if msg == "":
            return

        self.chat_history.append(f"You: {msg}")
        self.load_chat_history()
        self.message_entry.delete(0, "end")

    def close(self):
        self.destroy()
        if callable(self.on_close):
            self.on_close()


if __name__ == "__main__":

    root = ctk.CTk()
    root.withdraw()

    MessagesPage(root)

    root.mainloop()