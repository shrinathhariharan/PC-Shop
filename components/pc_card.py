"""
PC Card component – reusable visual card for displaying prebuilts or parts.
"""
import customtkinter as ctk


# ── Tier badge colours ────────────────────────────────────────────────────
TIER_COLORS = {
    "Budget":      ("#16A34A", "#4ADE80"),
    "Mid-Range":   ("#2563EB", "#3B82F6"),
    "High-End":    ("#9333EA", "#A855F7"),
    "Workstation": ("#DC2626", "#EF4444"),
    "Compact":     ("#EA580C", "#FB923C"),
}

TIER_ICONS = {
    "Budget":      "💚",
    "Mid-Range":   "💙",
    "High-End":    "💜",
    "Workstation": "🔴",
    "Compact":     "🧡",
}


class PCCard(ctk.CTkFrame):
    """
    A visual card component for displaying a prebuilt PC or part.

    Parameters
    ----------
    parent : widget
    data : dict
        Must contain at minimum: name, price.
        Optional: tier, description, specs (dict), stock, id.
    on_add_to_cart : callable, optional
        Called with (data_dict) when the Add to Cart button is clicked.
    compact : bool
        If True, renders a smaller card suitable for parts lists.
    """

    def __init__(self, parent, data: dict, on_add_to_cart=None, compact=False):
        super().__init__(
            parent,
            corner_radius=12,
            border_width=1,
            border_color=("#E4E4E7", "#3F3F46"),
            fg_color=("#FFFFFF", "#1C1C1F"),
        )
        self.data = data
        self.on_add_to_cart = on_add_to_cart
        self.compact = compact

        if compact:
            self._build_compact()
        else:
            self._build_full()

        # Hover effect
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    # ── Full card (prebuilts) ─────────────────────────────────────────
    def _build_full(self):
        pad = 16

        # Top row: tier badge + stock
        top_row = ctk.CTkFrame(self, fg_color="transparent")
        top_row.pack(fill="x", padx=pad, pady=(pad, 4))

        tier = self.data.get("tier", "")
        if tier:
            tier_color = TIER_COLORS.get(tier, ("#71717A", "#A1A1AA"))
            tier_icon = TIER_ICONS.get(tier, "")
            badge = ctk.CTkLabel(
                top_row,
                text=f" {tier_icon} {tier} ",
                font=ctk.CTkFont(family="Inter 18pt", size=10, weight="bold"),
                text_color=("#FFFFFF", "#FFFFFF"),
                fg_color=tier_color,
                corner_radius=6,
            )
            badge.pack(side="left")

        stock = self.data.get("stock", 0)
        stock_color = ("#16A34A", "#4ADE80") if stock > 3 else (
            ("#EA580C", "#FB923C") if stock > 0 else ("#DC2626", "#EF4444"))
        stock_text = f"{stock} in stock" if stock > 0 else "Out of stock"
        stock_label = ctk.CTkLabel(
            top_row,
            text=stock_text,
            font=ctk.CTkFont(family="Inter 18pt", size=10),
            text_color=stock_color,
        )
        stock_label.pack(side="right")

        # Name
        ctk.CTkLabel(
            self,
            text=self.data.get("name", "Unknown"),
            font=ctk.CTkFont(family="Inter 18pt", size=16, weight="bold"),
            text_color=("#18181B", "#FAFAFA"),
            anchor="w",
        ).pack(fill="x", padx=pad, pady=(4, 2))

        # Description
        desc = self.data.get("description", "")
        if desc:
            ctk.CTkLabel(
                self,
                text=desc,
                font=ctk.CTkFont(family="Inter 18pt", size=11),
                text_color=("#71717A", "#A1A1AA"),
                anchor="w",
                wraplength=280,
            ).pack(fill="x", padx=pad, pady=(0, 8))

        # Specs grid
        specs = self.data.get("specs", {})
        if specs:
            specs_frame = ctk.CTkFrame(self, fg_color=("#F4F4F5", "#18181B"),
                                        corner_radius=8)
            specs_frame.pack(fill="x", padx=pad, pady=(0, 8))

            spec_icons = {
                "cpu": "🔲", "gpu": "🎮", "ram": "🧠",
                "storage": "💾", "motherboard": "📟",
                "psu": "🔌", "case": "🗄️",
            }
            for key, value in specs.items():
                row = ctk.CTkFrame(specs_frame, fg_color="transparent")
                row.pack(fill="x", padx=10, pady=1)
                icon = spec_icons.get(key, "•")
                ctk.CTkLabel(
                    row,
                    text=f"{icon} {key.upper()}",
                    font=ctk.CTkFont(family="Inter 18pt", size=10, weight="bold"),
                    text_color=("#71717A", "#71717A"),
                    width=100,
                    anchor="w",
                ).pack(side="left")
                ctk.CTkLabel(
                    row,
                    text=str(value),
                    font=ctk.CTkFont(family="Inter 18pt", size=10),
                    text_color=("#3F3F46", "#D4D4D8"),
                    anchor="w",
                ).pack(side="left", padx=(4, 0))

        # Bottom: price + add button
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="x", padx=pad, pady=(4, pad))

        price = self.data.get("price", 0)
        ctk.CTkLabel(
            bottom,
            text=f"${price:,.2f}",
            font=ctk.CTkFont(family="Inter 18pt", size=20, weight="bold"),
            text_color=("#2563EB", "#3B82F6"),
        ).pack(side="left")

        if stock > 0 and self.on_add_to_cart:
            add_btn = ctk.CTkButton(
                bottom,
                text="Add to Cart",
                font=ctk.CTkFont(family="Inter 18pt", size=12, weight="bold"),
                height=34,
                corner_radius=8,
                command=lambda: self.on_add_to_cart(self.data),
            )
            add_btn.pack(side="right")

    # ── Compact card (parts) ──────────────────────────────────────────
    def _build_compact(self):
        pad = 12

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=pad, pady=pad)

        # Name
        ctk.CTkLabel(
            row,
            text=self.data.get("name", "Unknown"),
            font=ctk.CTkFont(family="Inter 18pt", size=13, weight="bold"),
            text_color=("#18181B", "#FAFAFA"),
            anchor="w",
        ).pack(side="left")

        # Price + stock + button
        right = ctk.CTkFrame(row, fg_color="transparent")
        right.pack(side="right")

        stock = self.data.get("stock", 0)
        stock_color = ("#16A34A", "#4ADE80") if stock > 3 else (
            ("#EA580C", "#FB923C") if stock > 0 else ("#DC2626", "#EF4444"))

        ctk.CTkLabel(
            right,
            text=f"({stock})",
            font=ctk.CTkFont(family="Inter 18pt", size=10),
            text_color=stock_color,
        ).pack(side="left", padx=(0, 6))

        price = self.data.get("price", 0)
        ctk.CTkLabel(
            right,
            text=f"${price:,.2f}",
            font=ctk.CTkFont(family="Inter 18pt", size=13, weight="bold"),
            text_color=("#2563EB", "#3B82F6"),
        ).pack(side="left", padx=(0, 8))

        if stock > 0 and self.on_add_to_cart:
            ctk.CTkButton(
                right,
                text="+",
                width=30,
                height=28,
                corner_radius=6,
                font=ctk.CTkFont(size=14, weight="bold"),
                command=lambda: self.on_add_to_cart(self.data),
            ).pack(side="right")

    # ── Hover effects ─────────────────────────────────────────────────
    def _on_enter(self, event=None):
        self.configure(border_color=("#2563EB", "#3B82F6"))

    def _on_leave(self, event=None):
        self.configure(border_color=("#E4E4E7", "#3F3F46"))
