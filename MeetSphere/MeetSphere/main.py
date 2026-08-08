import customtkinter as ctk

from screens.login import LoginPage


def main():
    # Application Theme
    ctk.set_appearance_mode("light")      # light or dark
    ctk.set_default_color_theme("blue")   # blue, green, dark-blue

    # Launch Login Page
    app = LoginPage()
    app.mainloop()


if __name__ == "__main__":
    main()