"""
Prebuilts View – store catalog screen showing pre-configured PC builds.
"""
import customtkinter as ctk
from data.app_state import AppState
from components.pc_card import PCCard


class PrebuiltsView(ctk.CTkFrame):
    """Scrollable catalog of prebuilt PCs with tier filtering."""

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.state = AppState()
        self.active_tier = "All"

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ── Title bar ─────────────────────────────────────────────────
        title_row = ctk.CTkFrame(self, fg_color="transparent")
        title_row.grid(row=0, column=0, sticky="ew", padx=4, pady=(0, 4))

        ctk.CTkLabel(
            title_row,
            text="🖥️  Prebuilt Systems",
            font=ctk.CTkFont(family="Inter 18pt", size=22, weight="bold"),
            text_color=("#18181B", "#FAFAFA"),
            anchor="w",
        ).pack(side="left")

        ctk.CTkLabel(
            title_row,
            text="Ready-to-ship desktop builds",
            font=ctk.CTkFont(family="Inter 18pt", size=12),
            text_color=("#71717A", "#A1A1AA"),
            anchor="w",
        ).pack(side="left", padx=(12, 0))

        # ── Tier filter bar ───────────────────────────────────────────
        filter_row = ctk.CTkFrame(self, fg_color="transparent")
        filter_row.grid(row=1, column=0, sticky="ew", padx=4, pady=(0, 8))

        tiers = ["All", "Budget", "Mid-Range", "High-End", "Workstation", "Compact"]
        self.filter_buttons: dict[str, ctk.CTkButton] = {}
        for tier in tiers:
            btn = ctk.CTkButton(
                filter_row,
                text=tier,
                font=ctk.CTkFont(family="Inter 18pt", size=11),
                height=30,
                corner_radius=15,
                fg_color=("#2563EB", "#3B82F6") if tier == "All" else "transparent",
                text_color=("#FFFFFF", "#FFFFFF") if tier == "All"
                    else ("#3F3F46", "#D4D4D8"),
                hover_color=("#1D4ED8", "#60A5FA") if tier == "All"
                    else ("#E4E4E7", "#27272A"),
                border_width=1,
                border_color=("#D4D4D8", "#3F3F46"),
                command=lambda t=tier: self._filter_tier(t),
            )
            btn.pack(side="left", padx=(0, 6))
            self.filter_buttons[tier] = btn

        # ── Scrollable cards area ─────────────────────────────────────
        self.cards_frame = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            label_text="",
        )
        self.cards_frame.grid(row=2, column=0, sticky="nsew")
        self.cards_frame.grid_columnconfigure((0, 1), weight=1)

        self._populate()

    def _filter_tier(self, tier: str):
        """Filter prebuilts by tier."""
        self.active_tier = tier
        # Update button styles
        for t, btn in self.filter_buttons.items():
            if t == tier:
                btn.configure(
                    fg_color=("#2563EB", "#3B82F6"),
                    text_color=("#FFFFFF", "#FFFFFF"),
                    hover_color=("#1D4ED8", "#60A5FA"),
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=("#3F3F46", "#D4D4D8"),
                    hover_color=("#E4E4E7", "#27272A"),
                )
        self._populate()

    def _populate(self):
        """Build card widgets for current filter."""
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        prebuilts = self.state.get_prebuilts()
        if self.active_tier != "All":
            prebuilts = [p for p in prebuilts if p.get("tier") == self.active_tier]

        if not prebuilts:
            ctk.CTkLabel(
                self.cards_frame,
                text="No systems found for this tier.",
                font=ctk.CTkFont(family="Inter 18pt", size=14),
                text_color=("#71717A", "#A1A1AA"),
            ).grid(row=0, column=0, columnspan=2, pady=40)
            return

        for idx, pb in enumerate(prebuilts):
            card = PCCard(
                self.cards_frame,
                data=pb,
                on_add_to_cart=self._add_to_cart,
            )
            row = idx // 2
            col = idx % 2
            card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")

    def _add_to_cart(self, data: dict):
        """Add a prebuilt to the cart."""
        self.state.add_to_cart(
            item_id=data["id"],
            name=data["name"],
            price=data["price"],
            qty=1,
            category="prebuilt",
        )
        # Quick visual feedback
        self._show_toast(f"✅ {data['name']} added to cart!")

    def _show_toast(self, message: str):
        """Briefly show a confirmation message."""
        toast = ctk.CTkLabel(
            self,
            text=message,
            font=ctk.CTkFont(family="Inter 18pt", size=12, weight="bold"),
            text_color=("#FFFFFF", "#FFFFFF"),
            fg_color=("#16A34A", "#16A34A"),
            corner_radius=8,
            height=36,
        )
        toast.place(relx=0.5, rely=0.95, anchor="center")
        self.after(2000, toast.destroy)
