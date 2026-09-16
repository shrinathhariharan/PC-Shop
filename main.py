import customtkinter as ctk
from components.sidebar import Sidebar
# pylint: disable=missing-docstring


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PC Shop")
        self.geometry("800x600")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = Sidebar(self)
        self.sidebar.grid(row=0, column=0, sticky="ns")

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, sticky="nsew")

        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.sidebar_button = ctk.CTkButton(
            master=self,
            width=20,
            height=20,
            text=">",
            command=self.button_callback
        )
        self.sidebar.bind("<Configure>", self.position_button)

    def position_button(self, event=None):
        self.sidebar_button.place(
            x=self.sidebar.winfo_width(),
            
        )
    def button_callback(self):
        print("Sidebar button called")

if __name__ == "__main__":
    app = App()
    app.mainloop()