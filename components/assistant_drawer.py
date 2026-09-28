"""
Assistant Drawer – docked right-side panel providing AI-style configuration advice.
Uses the C++ engine for real-time compatibility checking.
"""
import customtkinter as ctk
from data.app_state import AppState


class AssistantDrawer(ctk.CTkFrame):
    """
    Right-side collapsible advisor panel.
    Shows compatibility results and build suggestions.
    """

    def __init__(self, parent):
        super().__init__(parent, width=300, corner_radius=0,
                         fg_color=("#F4F4F5", "#0F0F11"))
        self.parent = parent
        self.state = AppState()
        self.is_open = False
        self.grid_propagate(False)

        self.grid_rowconfigure(5, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ── Header ────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=16, pady=(16, 8), sticky="ew")

        ctk.CTkLabel(
            header,
            text="🤖  Config Advisor",
            font=ctk.CTkFont(family="Inter 18pt", size=15, weight="bold"),
            text_color=("#18181B", "#FAFAFA"),
            anchor="w",
        ).pack(side="left")

        ctk.CTkButton(
            header,
            text="✕",
            width=28, height=28,
            corner_radius=6,
            fg_color="transparent",
            hover_color=("#E4E4E7", "#27272A"),
            text_color=("#71717A", "#A1A1AA"),
            font=ctk.CTkFont(size=14),
            command=self.close,
        ).pack(side="right")

        # Separator
        ctk.CTkFrame(
            self, height=1, corner_radius=0,
            fg_color=("#E4E4E7", "#3F3F46"),
        ).grid(row=1, column=0, sticky="ew", padx=16)

        # ── Status area ───────────────────────────────────────────────
        self.status_label = ctk.CTkLabel(
            self,
            text="Select parts in Custom Build to get\nreal-time compatibility feedback.",
            font=ctk.CTkFont(family="Inter 18pt", size=11),
            text_color=("#71717A", "#A1A1AA"),
            justify="left",
            anchor="nw",
        )
        self.status_label.grid(row=2, column=0, padx=16, pady=(12, 4), sticky="new")

        # ── Compatibility results ─────────────────────────────────────
        self.results_frame = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            label_text="",
        )
        self.results_frame.grid(row=3, column=0, padx=8, pady=4, sticky="nsew")

        # ── Suggestions ───────────────────────────────────────────────
        self.suggestions_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(family="Inter 18pt", size=10),
            text_color=("#71717A", "#A1A1AA"),
            justify="left",
            anchor="nw",
            wraplength=260,
        )
        self.suggestions_label.grid(row=4, column=0, padx=16, pady=(4, 16), sticky="new")

    def open(self):
        """Show the advisor drawer."""
        self.is_open = True
        self.grid(row=1, column=2, sticky="nsew", rowspan=2)

    def close(self):
        """Hide the advisor drawer."""
        self.is_open = False
        self.grid_remove()

    def toggle(self):
        """Toggle the drawer open/closed."""
        if self.is_open:
            self.close()
        else:
            self.open()

    def show_results(self, compat_result, build_info: dict = None):
        """
        Display compatibility results from the C++ engine.

        Parameters
        ----------
        compat_result : pc_engine.CompatResult or dict
        build_info : dict, optional
            Additional build metadata (power draw, etc.)
        """
        # Clear old results
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        # Overall status
        compatible = getattr(compat_result, "compatible", True)
        errors = getattr(compat_result, "errors", [])
        warnings = getattr(compat_result, "warnings", [])

        if compatible and not warnings:
            self.status_label.configure(
                text="✅  All components are compatible!",
                text_color=("#16A34A", "#4ADE80"),
            )
        elif compatible and warnings:
            self.status_label.configure(
                text="⚠️  Compatible with warnings",
                text_color=("#EA580C", "#FB923C"),
            )
        else:
            self.status_label.configure(
                text="❌  Compatibility issues found!",
                text_color=("#DC2626", "#EF4444"),
            )

        # Error cards
        for err in errors:
            card = ctk.CTkFrame(self.results_frame,
                                fg_color=("#FEE2E2", "#3B1111"),
                                corner_radius=8)
            card.pack(fill="x", padx=4, pady=3)
            ctk.CTkLabel(
                card, text=f"❌  {err}",
                font=ctk.CTkFont(family="Inter 18pt", size=10),
                text_color=("#DC2626", "#EF4444"),
                wraplength=240, justify="left", anchor="w",
            ).pack(padx=10, pady=8, anchor="w")

        # Warning cards
        for warn in warnings:
            card = ctk.CTkFrame(self.results_frame,
                                fg_color=("#FEF3C7", "#3B2F11"),
                                corner_radius=8)
            card.pack(fill="x", padx=4, pady=3)
            ctk.CTkLabel(
                card, text=f"⚠️  {warn}",
                font=ctk.CTkFont(family="Inter 18pt", size=10),
                text_color=("#EA580C", "#FB923C"),
                wraplength=240, justify="left", anchor="w",
            ).pack(padx=10, pady=8, anchor="w")

        # Build info
        if build_info:
            info_text = []
            if "total_power" in build_info:
                info_text.append(
                    f"⚡ Est. power draw: {build_info['total_power']}W")
            if "psu_headroom" in build_info:
                info_text.append(
                    f"🔋 PSU headroom: {build_info['psu_headroom']}%")
            if info_text:
                self.suggestions_label.configure(text="\n".join(info_text))
