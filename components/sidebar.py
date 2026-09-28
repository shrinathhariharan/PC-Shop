"""
Sidebar component – main navigation menu with persistent budget tracker.
"""
import customtkinter as ctk
from data.app_state import AppState


class Sidebar(ctk.CTkFrame):
    """Navigation sidebar with budget tracker and cart summary."""

    # Navigation items: (label, icon, view_key)
    NAV_ITEMS = [
        ("Prebuilts",    "🖥️", "prebuilts"),
        ("Custom Build", "🔧", "custom_build"),
        ("Repair",       "🩺", "repair"),
        ("Cart",         "🛒", "cart"),
        ("Admin Panel",  "⚙️", "owner"),
    ]

    def __init__(self, parent, navigate_callback=None):
        super().__init__(parent, width=220, corner_radius=0,
                         fg_color=("#F4F4F5", "#0F0F11"))
        self.parent = parent
        self.navigate_callback = navigate_callback
        self.is_visible = True
        self.active_view = "prebuilts"
        self.state = AppState()
        self.grid_propagate(False)

        self.grid_rowconfigure(10, weight=1)  # spacer before budget
        self.grid_columnconfigure(0, weight=1)

        # ── Section title ─────────────────────────────────────────────
        self.section_label = ctk.CTkLabel(
            self, text="Navigation",
            font=ctk.CTkFont(family="Inter 18pt", size=11, weight="bold"),
            text_color=("#71717A", "#71717A"),
            anchor="w",
        )
        self.section_label.grid(row=0, column=0, padx=20, pady=(20, 6), sticky="w")

        # ── Nav buttons ───────────────────────────────────────────────
        self.nav_buttons: dict[str, ctk.CTkButton] = {}
        for idx, (label, icon, key) in enumerate(self.NAV_ITEMS):
            btn = ctk.CTkButton(
                self,
                text=f"  {icon}  {label}",
                font=ctk.CTkFont(family="Inter 18pt", size=13),
                anchor="w",
                height=38,
                corner_radius=8,
                fg_color="transparent",
                text_color=("#3F3F46", "#D4D4D8"),
                hover_color=("#E4E4E7", "#27272A"),
                command=lambda k=key: self._nav_click(k),
            )
            btn.grid(row=idx + 1, column=0, padx=12, pady=2, sticky="ew")
            self.nav_buttons[key] = btn

        # Highlight default
        self._highlight_button("prebuilts")

        # ── Budget tracker section ────────────────────────────────────
        budget_frame = ctk.CTkFrame(self, fg_color=("#E4E4E7", "#18181B"),
                                     corner_radius=10)
        budget_frame.grid(row=11, column=0, padx=12, pady=(8, 8), sticky="ew")

        ctk.CTkLabel(
            budget_frame, text="💰  Budget Tracker",
            font=ctk.CTkFont(family="Inter 18pt", size=11, weight="bold"),
            text_color=("#3F3F46", "#A1A1AA"),
            anchor="w",
        ).pack(padx=12, pady=(10, 4), anchor="w")

        budget_input_frame = ctk.CTkFrame(budget_frame, fg_color="transparent")
        budget_input_frame.pack(padx=12, pady=(0, 4), fill="x")

        self.budget_entry = ctk.CTkEntry(
            budget_input_frame,
            placeholder_text="$ Budget",
            width=100,
            height=30,
            font=ctk.CTkFont(family="Inter 18pt", size=11),
        )
        self.budget_entry.pack(side="left", expand=True, fill="x", padx=(0, 4))

        self.budget_btn = ctk.CTkButton(
            budget_input_frame,
            text="Set",
            width=40,
            height=30,
            font=ctk.CTkFont(family="Inter 18pt", size=11),
            command=self._set_budget,
        )
        self.budget_btn.pack(side="right")

        self.budget_label = ctk.CTkLabel(
            budget_frame,
            text="No budget set",
            font=ctk.CTkFont(family="Inter 18pt", size=11),
            text_color=("#71717A", "#71717A"),
        )
        self.budget_label.pack(padx=12, pady=(0, 10), anchor="w")

        # ── Cart summary ──────────────────────────────────────────────
        cart_frame = ctk.CTkFrame(self, fg_color=("#E4E4E7", "#18181B"),
                                   corner_radius=10)
        cart_frame.grid(row=12, column=0, padx=12, pady=(0, 12), sticky="ew")

        self.cart_summary_label = ctk.CTkLabel(
            cart_frame,
            text="🛒  Cart: 0 items  —  $0.00",
            font=ctk.CTkFont(family="Inter 18pt", size=11),
            text_color=("#3F3F46", "#A1A1AA"),
            anchor="w",
        )
        self.cart_summary_label.pack(padx=12, pady=10, anchor="w")

        # ── Toggle button (placed on parent so it persists) ───────────
        TOGGLE_SIZE = 28
        self.toggle_button = ctk.CTkButton(
            parent,
            text="◀",
            width=TOGGLE_SIZE,
            height=TOGGLE_SIZE,
            corner_radius=TOGGLE_SIZE // 2,
            font=ctk.CTkFont(size=12),
            fg_color=("#D4D4D8", "#3F3F46"),
            hover_color=("#A1A1AA", "#52525B"),
            text_color=("#18181B", "#FAFAFA"),
            command=self._toggle_sidebar,
        )
        self.bind("<Configure>", self._position_toggle)

        # Subscribe to state changes
        self.state.subscribe(self._on_state_change)

    # ── Navigation ────────────────────────────────────────────────────
    def _nav_click(self, view_key: str):
        self.active_view = view_key
        self._highlight_button(view_key)
        if self.navigate_callback:
            self.navigate_callback(view_key)

    def _highlight_button(self, active_key: str):
        """Visually highlight the active nav button."""
        for key, btn in self.nav_buttons.items():
            if key == active_key:
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

    # ── Budget ────────────────────────────────────────────────────────
    def _set_budget(self):
        raw = self.budget_entry.get().strip().replace("$", "").replace(",", "")
        try:
            amount = float(raw)
            if amount <= 0:
                raise ValueError
            self.state.set_budget(amount)
            self.budget_entry.delete(0, "end")
        except ValueError:
            self.budget_entry.delete(0, "end")
            self.budget_entry.configure(placeholder_text="Invalid!")
            self.after(1500, lambda: self.budget_entry.configure(
                placeholder_text="$ Budget"))

    # ── State observer ────────────────────────────────────────────────
    def _on_state_change(self):
        # Update budget display
        if self.state.budget_enabled:
            remaining = self.state.budget_remaining()
            color = ("#16A34A", "#4ADE80") if remaining >= 0 else ("#DC2626", "#EF4444")
            self.budget_label.configure(
                text=f"Remaining: ${remaining:,.2f}",
                text_color=color,
            )
        else:
            self.budget_label.configure(
                text="No budget set",
                text_color=("#71717A", "#71717A"),
            )

        # Update cart summary
        count = self.state.cart_count()
        total = self.state.cart_total()
        self.cart_summary_label.configure(
            text=f"🛒  Cart: {count} item{'s' if count != 1 else ''}  —  ${total:,.2f}"
        )

    # ── Toggle sidebar ────────────────────────────────────────────────
    def _position_toggle(self, event=None):
        if self.is_visible:
            w = self.winfo_width()
            x = (w + 5 if w > 1 else 225) - 5
            self.toggle_button.configure(text="◀")
            self.toggle_button.place(x=x, rely=0.5, anchor="center")
        else:
            self.toggle_button.configure(text="▶")
            self.toggle_button.place(x=14, rely=0.5, anchor="center")
        self.toggle_button.lift()

    def _toggle_sidebar(self):
        if self.is_visible:
            self.grid_remove()
            self.is_visible = False
        else:
            self.grid()
            self.is_visible = True
        self._position_toggle()