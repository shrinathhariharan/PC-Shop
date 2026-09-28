"""
Cart View – shopping cart, checkout, and digital invoice generator.
"""
import customtkinter as ctk
from data.app_state import AppState
from utils.pdf_generator import generate_invoice


class CartView(ctk.CTkFrame):
    """Cart management with quantity editing, checkout, and PDF invoice generation."""

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.state = AppState()

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ── Title ─────────────────────────────────────────────────────
        title_row = ctk.CTkFrame(self, fg_color="transparent")
        title_row.grid(row=0, column=0, sticky="ew", padx=4, pady=(0, 8))

        ctk.CTkLabel(
            title_row,
            text="🛒  Shopping Cart",
            font=ctk.CTkFont(family="Inter 18pt", size=22, weight="bold"),
            text_color=("#18181B", "#FAFAFA"),
            anchor="w",
        ).pack(side="left")

        self.item_count_label = ctk.CTkLabel(
            title_row,
            text="0 items",
            font=ctk.CTkFont(family="Inter 18pt", size=12),
            text_color=("#71717A", "#A1A1AA"),
        )
        self.item_count_label.pack(side="left", padx=(12, 0))

        ctk.CTkButton(
            title_row,
            text="Clear Cart",
            font=ctk.CTkFont(family="Inter 18pt", size=11),
            height=30,
            corner_radius=8,
            fg_color="transparent",
            border_width=1,
            border_color=("#DC2626", "#EF4444"),
            text_color=("#DC2626", "#EF4444"),
            hover_color=("#FEE2E2", "#3B1111"),
            command=self._clear_cart,
        ).pack(side="right")

        # ── Main content: items + summary ─────────────────────────────
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=4)
        content.grid_columnconfigure(0, weight=3)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)

        # Left: cart items
        self.items_frame = ctk.CTkScrollableFrame(
            content, fg_color="transparent",
            label_text="",
        )
        self.items_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.items_frame.grid_columnconfigure(0, weight=1)

        # Right: order summary
        self.summary_frame = ctk.CTkFrame(
            content,
            fg_color=("#FFFFFF", "#1C1C1F"),
            corner_radius=12,
            border_width=1,
            border_color=("#E4E4E7", "#3F3F46"),
        )
        self.summary_frame.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(
            self.summary_frame,
            text="Order Summary",
            font=ctk.CTkFont(family="Inter 18pt", size=15, weight="bold"),
            text_color=("#18181B", "#FAFAFA"),
            anchor="w",
        ).pack(padx=16, pady=(16, 12), anchor="w")

        # Summary labels
        self.subtotal_label = ctk.CTkLabel(
            self.summary_frame,
            text="Subtotal:  $0.00",
            font=ctk.CTkFont(family="Inter 18pt", size=12),
            text_color=("#3F3F46", "#D4D4D8"),
            anchor="w",
        )
        self.subtotal_label.pack(padx=16, pady=2, anchor="w")

        self.tax_label = ctk.CTkLabel(
            self.summary_frame,
            text="Tax (8.25%):  $0.00",
            font=ctk.CTkFont(family="Inter 18pt", size=12),
            text_color=("#3F3F46", "#D4D4D8"),
            anchor="w",
        )
        self.tax_label.pack(padx=16, pady=2, anchor="w")

        # Discount info (if applicable via C++ engine)
        self.discount_label = ctk.CTkLabel(
            self.summary_frame,
            text="",
            font=ctk.CTkFont(family="Inter 18pt", size=11),
            text_color=("#16A34A", "#4ADE80"),
            anchor="w",
        )
        self.discount_label.pack(padx=16, pady=2, anchor="w")

        ctk.CTkFrame(
            self.summary_frame, height=1, corner_radius=0,
            fg_color=("#E4E4E7", "#3F3F46"),
        ).pack(fill="x", padx=16, pady=8)

        self.total_label = ctk.CTkLabel(
            self.summary_frame,
            text="Total:  $0.00",
            font=ctk.CTkFont(family="Inter 18pt", size=18, weight="bold"),
            text_color=("#2563EB", "#3B82F6"),
            anchor="w",
        )
        self.total_label.pack(padx=16, pady=(0, 12), anchor="w")

        # Budget warning
        self.budget_warning = ctk.CTkLabel(
            self.summary_frame,
            text="",
            font=ctk.CTkFont(family="Inter 18pt", size=11),
            text_color=("#DC2626", "#EF4444"),
            anchor="w",
            wraplength=200,
        )
        self.budget_warning.pack(padx=16, pady=(0, 8), anchor="w")

        # Checkout button
        self.checkout_btn = ctk.CTkButton(
            self.summary_frame,
            text="Checkout",
            font=ctk.CTkFont(family="Inter 18pt", size=14, weight="bold"),
            height=44,
            corner_radius=8,
            command=self._checkout,
        )
        self.checkout_btn.pack(padx=16, fill="x", pady=(4, 16))

        # Invoice status
        self.invoice_label = ctk.CTkLabel(
            self.summary_frame,
            text="",
            font=ctk.CTkFont(family="Inter 18pt", size=10),
            text_color=("#71717A", "#A1A1AA"),
            anchor="w",
            wraplength=200,
        )
        self.invoice_label.pack(padx=16, pady=(0, 12), anchor="w")

        # Subscribe and populate
        self.state.subscribe(self._refresh)
        self._refresh()

    def _refresh(self):
        """Rebuild cart display from state."""
        # Clear items
        for widget in self.items_frame.winfo_children():
            widget.destroy()

        cart = self.state.cart
        self.item_count_label.configure(
            text=f"{self.state.cart_count()} item{'s' if self.state.cart_count() != 1 else ''}"
        )

        if not cart:
            ctk.CTkLabel(
                self.items_frame,
                text="Your cart is empty.\n\nBrowse prebuilts or create a custom build!",
                font=ctk.CTkFont(family="Inter 18pt", size=14),
                text_color=("#71717A", "#A1A1AA"),
                justify="center",
            ).grid(row=0, column=0, pady=60)
            self._update_summary()
            return

        for idx, item in enumerate(cart):
            card = self._create_item_card(item)
            card.grid(row=idx, column=0, sticky="ew", padx=4, pady=4)

        self._update_summary()

    def _create_item_card(self, item: dict) -> ctk.CTkFrame:
        """Build a cart item card with quantity controls."""
        card = ctk.CTkFrame(
            self.items_frame,
            corner_radius=10,
            border_width=1,
            border_color=("#E4E4E7", "#3F3F46"),
            fg_color=("#FFFFFF", "#1C1C1F"),
        )

        # Category badge
        cat = item.get("category", "item")
        cat_icons = {"prebuilt": "🖥️", "custom_build": "🔧", "part": "🔩"}
        cat_icon = cat_icons.get(cat, "📦")

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=14, pady=(10, 2))

        ctk.CTkLabel(
            top,
            text=f"{cat_icon}  {item['name']}",
            font=ctk.CTkFont(family="Inter 18pt", size=13, weight="bold"),
            text_color=("#18181B", "#FAFAFA"),
            anchor="w",
        ).pack(side="left")

        # Remove button
        ctk.CTkButton(
            top,
            text="✕",
            width=24, height=24,
            corner_radius=6,
            fg_color="transparent",
            hover_color=("#FEE2E2", "#3B1111"),
            text_color=("#DC2626", "#EF4444"),
            font=ctk.CTkFont(size=12),
            command=lambda: self.state.remove_from_cart(item["id"]),
        ).pack(side="right")

        bottom = ctk.CTkFrame(card, fg_color="transparent")
        bottom.pack(fill="x", padx=14, pady=(0, 10))

        ctk.CTkLabel(
            bottom,
            text=f"${item['price']:,.2f} each",
            font=ctk.CTkFont(family="Inter 18pt", size=11),
            text_color=("#71717A", "#A1A1AA"),
        ).pack(side="left")

        # Quantity controls
        qty_frame = ctk.CTkFrame(bottom, fg_color="transparent")
        qty_frame.pack(side="right")

        ctk.CTkButton(
            qty_frame, text="−", width=28, height=28, corner_radius=6,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#E4E4E7", "#27272A"),
            hover_color=("#D4D4D8", "#3F3F46"),
            text_color=("#18181B", "#FAFAFA"),
            command=lambda: self.state.update_cart_qty(item["id"], item["qty"] - 1),
        ).pack(side="left")

        ctk.CTkLabel(
            qty_frame,
            text=str(item["qty"]),
            font=ctk.CTkFont(family="Inter 18pt", size=13, weight="bold"),
            text_color=("#18181B", "#FAFAFA"),
            width=36,
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            qty_frame, text="+", width=28, height=28, corner_radius=6,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#E4E4E7", "#27272A"),
            hover_color=("#D4D4D8", "#3F3F46"),
            text_color=("#18181B", "#FAFAFA"),
            command=lambda: self.state.update_cart_qty(item["id"], item["qty"] + 1),
        ).pack(side="left")

        # Line total
        line_total = item["price"] * item["qty"]
        ctk.CTkLabel(
            qty_frame,
            text=f"${line_total:,.2f}",
            font=ctk.CTkFont(family="Inter 18pt", size=13, weight="bold"),
            text_color=("#2563EB", "#3B82F6"),
            width=80,
        ).pack(side="left", padx=(12, 0))

        return card

    def _update_summary(self):
        """Recalculate order summary."""
        subtotal = self.state.cart_total()
        tax_rate = 0.0825

        # Try C++ engine for tax & discount
        try:
            import pc_engine
            tax = pc_engine.estimate_tax(subtotal, tax_rate)
            # Check bulk discounts
            discount_info = []
            for item in self.state.cart:
                if item["qty"] >= 5:
                    pct = pc_engine.calculate_discount(item["qty"])
                    if pct > 0:
                        discount_info.append(
                            f"{item['name']}: {pct*100:.0f}% bulk discount"
                        )
            if discount_info:
                self.discount_label.configure(
                    text="💰 " + "\n💰 ".join(discount_info))
            else:
                self.discount_label.configure(text="")
        except ImportError:
            tax = round(subtotal * tax_rate, 2)
            self.discount_label.configure(text="")

        total = round(subtotal + tax, 2)

        self.subtotal_label.configure(text=f"Subtotal:  ${subtotal:,.2f}")
        self.tax_label.configure(text=f"Tax ({tax_rate*100:.2f}%):  ${tax:,.2f}")
        self.total_label.configure(text=f"Total:  ${total:,.2f}")

        # Budget check
        if self.state.budget_enabled:
            remaining = self.state.budget - total
            if remaining < 0:
                self.budget_warning.configure(
                    text=f"⚠️  Over budget by ${abs(remaining):,.2f}")
            else:
                self.budget_warning.configure(text="")
        else:
            self.budget_warning.configure(text="")

        # Enable/disable checkout
        self.checkout_btn.configure(
            state="normal" if self.state.cart else "disabled"
        )

    def _checkout(self):
        """Process checkout, generate invoice, show confirmation."""
        if not self.state.cart:
            return

        order = self.state.checkout()
        if not order:
            return

        # Generate PDF invoice
        try:
            pdf_path = generate_invoice(order)
            self.invoice_label.configure(
                text=f"📄 Invoice saved:\n{pdf_path}",
                text_color=("#16A34A", "#4ADE80"),
            )
        except Exception as e:
            self.invoice_label.configure(
                text=f"⚠️ Invoice error: {e}",
                text_color=("#DC2626", "#EF4444"),
            )

        # Show confirmation toast
        self._show_checkout_toast(order)

    def _clear_cart(self):
        """Clear the entire cart with confirmation."""
        if not self.state.cart:
            return
        self.state.clear_cart()
        self.invoice_label.configure(text="")

    def _show_checkout_toast(self, order: dict):
        toast = ctk.CTkFrame(
            self,
            fg_color=("#DCFCE7", "#14532D"),
            corner_radius=10,
        )
        toast.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            toast,
            text=f"✅  Order placed!",
            font=ctk.CTkFont(family="Inter 18pt", size=16, weight="bold"),
            text_color=("#16A34A", "#4ADE80"),
        ).pack(padx=24, pady=(16, 4))

        ctk.CTkLabel(
            toast,
            text=f"ID: {order['order_id']}  |  Total: ${order['total']:,.2f}",
            font=ctk.CTkFont(family="Inter 18pt", size=12),
            text_color=("#166534", "#86EFAC"),
        ).pack(padx=24, pady=(0, 16))

        self.after(3000, toast.destroy)
