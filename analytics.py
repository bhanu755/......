import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class AnalyticsPage(ctk.CTkToplevel):

    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        self.title("MeetSphere - Analytics")
        self.geometry("1200x700")
        self.resizable(False, False)

        self.configure(fg_color="#F4F7FE")

            # Do not hide Dashboard when opening this page
            # (previously withdrew the parent window)

        # Restore Dashboard when window closes
        self.protocol("WM_DELETE_WINDOW", self.close_window)

        # ==========================
        # HEADER
        # ==========================

        header = ctk.CTkFrame(self, height=70)
        header.pack(fill="x", padx=20, pady=20)
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="📊 Analytics Dashboard",
            font=("Arial", 28, "bold")
        ).pack(side="left", padx=20)

        ctk.CTkButton(
            header,
            text="← Back to Dashboard",
            command=self.close_window
        ).pack(side="right", padx=20)

        # ==========================
        # STATISTICS
        # ==========================

        stats = ctk.CTkFrame(self)
        stats.pack(fill="x", padx=20, pady=10)

        self.card(stats, "Meetings", "No data").grid(row=0, column=0, padx=15, pady=10)
        self.card(stats, "Participants", "No data").grid(row=0, column=1, padx=15, pady=10)
        self.card(stats, "Hours", "No data").grid(row=0, column=2, padx=15, pady=10)
        self.card(stats, "Success", "No data").grid(row=0, column=3, padx=15, pady=10)

        # ==========================
        # CHART
        # ==========================

        chart_frame = ctk.CTkFrame(self)
        chart_frame.pack(fill="both", expand=True, padx=20, pady=20)

        fig, ax = plt.subplots(figsize=(8, 4))

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        meetings = [0, 0, 0, 0, 0, 0, 0]

        ax.plot(days, meetings, marker="o", linewidth=3)

        ax.set_title("Weekly Meetings")
        ax.set_xlabel("Days")
        ax.set_ylabel("Meetings")
        ax.grid(True)

        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # ==========================
    # CARD
    # ==========================

    def card(self, parent, title, value):

        frame = ctk.CTkFrame(
            parent,
            width=220,
            height=120,
            corner_radius=15
        )

        frame.pack_propagate(False)

        ctk.CTkLabel(
            frame,
            text=title,
            font=("Arial", 16)
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            frame,
            text=value,
            font=("Arial", 30, "bold"),
            text_color="#2563EB"
        ).pack()

        return frame

    # ==========================
    # CLOSE WINDOW
    # ==========================

    def close_window(self):
        # Do not restore/deiconify parent — leave Dashboard visible
        self.destroy()


class AnalyticsPanel(ctk.CTkFrame):

    def __init__(self, parent, dashboard=None, on_close=None):
        super().__init__(parent, fg_color="white", corner_radius=15)
        self.dashboard = dashboard
        self.on_close = on_close

        header = ctk.CTkFrame(self, height=60)
        header.pack(fill="x", padx=20, pady=15)
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="📊 Analytics Dashboard",
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

        stats = ctk.CTkFrame(self)
        stats.pack(fill="x", padx=20, pady=10)

        self.card(stats, "Meetings", "No data").grid(row=0, column=0, padx=15, pady=10)
        self.card(stats, "Participants", "No data").grid(row=0, column=1, padx=15, pady=10)
        self.card(stats, "Hours", "No data").grid(row=0, column=2, padx=15, pady=10)
        self.card(stats, "Success", "No data").grid(row=0, column=3, padx=15, pady=10)

        chart_frame = ctk.CTkFrame(self)
        chart_frame.pack(fill="both", expand=True, padx=20, pady=20)

        fig, ax = plt.subplots(figsize=(8, 4))

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        meetings = [0, 0, 0, 0, 0, 0, 0]

        ax.plot(days, meetings, marker="o", linewidth=3)

        ax.set_title("Weekly Meetings")
        ax.set_xlabel("Days")
        ax.set_ylabel("Meetings")
        ax.grid(True)

        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def close(self):
        try:
            self.destroy()
        except Exception:
            pass
        if callable(self.on_close):
            self.on_close()


if __name__ == "__main__":
    root = ctk.CTk()
    app = AnalyticsPage(root)
    app.mainloop()