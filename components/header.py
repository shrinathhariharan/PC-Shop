"""
Header component – top bar with app title, logo, and theme toggle.
"""
import customtkinter as ctk


class Header(ctk.CTkFrame):
    """Top application header with branding and theme switch."""

    def __init__(self, parent):
        super().__init__(parent, height=56, corner_radius=0,
                         fg_color=("white", "#1C1C1F"))
        self.pack_propagate(False)
        self.grid_propagate(False)

        # ── Left: logo + title ────────────────────────────────────────
        left_frame = ctk.CTkFrame(self, fg_color="transparent")
        left_frame.pack(side="left", padx=20)

        self.logo_label = ctk.CTkLabel(
            left_frame,
            text="⚡",
            font=ctk.CTkFont(size=22),
        )
        self.logo_label.pack(side="left", padx=(0, 6))

        self.title_label = ctk.CTkLabel(
            left_frame,
            text="PC Shop",
            font=ctk.CTkFont(family="Inter 18pt", size=18, weight="bold"),
            text_color=("#18181B", "#FAFAFA"),
        )
        self.title_label.pack(side="left")

        self.subtitle_label = ctk.CTkLabel(
            left_frame,
            text="Build · Buy · Repair",
            font=ctk.CTkFont(family="Inter 18pt", size=11),
            text_color=("#71717A", "#A1A1AA"),
        )
        self.subtitle_label.pack(side="left", padx=(12, 0))

        # ── Right: theme toggle ───────────────────────────────────────
        right_frame = ctk.CTkFrame(self, fg_color="transparent")
        right_frame.pack(side="right", padx=20)

        self.theme_icon = ctk.CTkLabel(
            right_frame,
            text="🌙",
            font=ctk.CTkFont(size=16),
        )
        self.theme_icon.pack(side="left", padx=(0, 6))

        self.theme_switch = ctk.CTkSwitch(
            right_frame,
            width=40,
            text="",
            command=self._toggle_theme,
            onvalue=1,
            offvalue=0,
        )
        self.theme_switch.pack(side="left")

        self.theme_label = ctk.CTkLabel(
            right_frame,
            text="Dark",
            font=ctk.CTkFont(family="Inter 18pt", size=12),
            text_color=("#71717A", "#A1A1AA"),
        )
        self.theme_label.pack(side="left", padx=(6, 0))

        # Bottom separator line
        sep = ctk.CTkFrame(self, height=1, corner_radius=0,
                           fg_color=("#E4E4E7", "#3F3F46"))
        sep.pack(side="bottom", fill="x")

    def _toggle_theme(self):
        """Switch between dark and light appearance modes."""
        if self.theme_switch.get() == 1:
            ctk.set_appearance_mode("light")
            self.theme_icon.configure(text="☀️")
            self.theme_label.configure(text="Light")
        else:
            ctk.set_appearance_mode("dark")
            self.theme_icon.configure(text="🌙")
            self.theme_label.configure(text="Dark")