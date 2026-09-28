"""
Footer component – bottom bar showing C++ engine status and active cart total.
"""
import customtkinter as ctk
from data.app_state import AppState


class Footer(ctk.CTkFrame):
    """Bottom status bar with engine status and live cart total."""

    def __init__(self, parent):
        super().__init__(parent, height=32, corner_radius=0,
                         fg_color=("#E4E4E7", "#0F0F11"))
        self.pack_propagate(False)
        self.state = AppState()

        # ── Left: engine status ───────────────────────────────────────
        left = ctk.CTkFrame(self, fg_color="transparent")
        left.pack(side="left", padx=16)

        self.engine_dot = ctk.CTkLabel(
            left, text="●",
            font=ctk.CTkFont(size=10),
            text_color=("#71717A", "#71717A"),
        )
        self.engine_dot.pack(side="left", padx=(0, 4))

        self.engine_label = ctk.CTkLabel(
            left,
            text="C++ Engine: Checking...",
            font=ctk.CTkFont(family="Inter 18pt", size=10),
            text_color=("#71717A", "#A1A1AA"),
        )
        self.engine_label.pack(side="left")

        # ── Right: live total ─────────────────────────────────────────
        right = ctk.CTkFrame(self, fg_color="transparent")
        right.pack(side="right", padx=16)

        self.total_label = ctk.CTkLabel(
            right,
            text="Cart Total: $0.00",
            font=ctk.CTkFont(family="Inter 18pt", size=10, weight="bold"),
            text_color=("#3F3F46", "#D4D4D8"),
        )
        self.total_label.pack(side="right")

        # Subscribe and update
        self.state.subscribe(self._update)
        self.after(500, self._check_engine)

    def _check_engine(self):
        """Attempt to import pc_engine and report status."""
        try:
            import pc_engine  # noqa: F401
            self.state.engine_loaded = True
            self.engine_dot.configure(text_color=("#16A34A", "#4ADE80"))
            self.engine_label.configure(text="C++ Engine: Loaded ✓")
        except ImportError:
            self.state.engine_loaded = False
            self.engine_dot.configure(text_color=("#DC2626", "#EF4444"))
            self.engine_label.configure(text="C++ Engine: Not Found ✗")

    def _update(self):
        total = self.state.cart_total()
        count = self.state.cart_count()
        self.total_label.configure(
            text=f"Cart Total: ${total:,.2f}  ({count} item{'s' if count != 1 else ''})"
        )
