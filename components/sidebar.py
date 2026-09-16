import customtkinter as ctk
# pylint: disable=missing-docstring

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_rowconfigure(4, weight=1)

        self.title_label = ctk.CTkLabel(self, text="Shop", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.home_button = ctk.CTkButton(self, text="Home", command=self.go_home)
        self.home_button.grid(row=1, column=0, padx=20, pady=10)

        self.settings_button = ctk.CTkButton(self, text="Settings", command=self.go_settings)
        self.settings_button.grid(row=2, column=0, padx=20, pady=10)

    def go_home(self):
        print("Home clicked")

    def go_settings(self):
        print("Settings clicked")