"""
Owner View – password-protected admin dashboard for inventory management,
order tracking, and password management.
"""
import customtkinter as ctk
from data.app_state import AppState


class OwnerView(ctk.CTkFrame):
    """Admin panel gated by a password screen, with inventory/orders/repairs/settings tabs."""

    ORDER_STATUSES = ["Processing", "Confirmed", "Building", "Shipped", "Delivered", "Cancelled"]

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.state = AppState()
        self.authenticated = False
        self.active_tab = "inventory"

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Start with the login screen
        self._show_login()

    # ══════════════════════════════════════════════════════════════════
    #  LOGIN SCREEN
    # ══════════════════════════════════════════════════════════════════
    def _show_login(self):
        """Render the password gate screen."""
        self._clear_root()

        # Centred container
        wrapper = ctk.CTkFrame(self, fg_color="transparent")
        wrapper.grid(row=0, column=0)

        card = ctk.CTkFrame(
            wrapper,
            width=380,
            fg_color=("#FFFFFF", "#1C1C1F"),
            corner_radius=16,
            border_width=1,
            border_color=("#E4E4E7", "#3F3F46"),
        )
        card.pack(padx=40, pady=40)
        card.pack_propagate(False)
        card.configure(width=380, height=340)

        # Lock icon
        ctk.CTkLabel(
            card,
            text="🔒",
            font=ctk.CTkFont(size=40),
        ).pack(pady=(32, 4))

        ctk.CTkLabel(
            card,
            text="Admin Access",
            font=ctk.CTkFont(family="Inter 18pt", size=20, weight="bold"),
            text_color=("#18181B", "#FAFAFA"),
        ).pack(pady=(0, 2))

        ctk.CTkLabel(
            card,
            text="Enter the admin password to continue",
            font=ctk.CTkFont(family="Inter 18pt", size=11),
            text_color=("#71717A", "#A1A1AA"),
        ).pack(pady=(0, 16))

        # Password entry
        self.login_entry = ctk.CTkEntry(
            card,
            placeholder_text="Password",
            show="•",
            width=260,
            height=40,
            font=ctk.CTkFont(family="Inter 18pt", size=13),
            justify="center",
        )
        self.login_entry.pack(pady=(0, 4))
        self.login_entry.bind("<Return>", lambda e: self._attempt_login())
        self.login_entry.focus_set()

        # Error label
        self.login_error = ctk.CTkLabel(
            card,
            text="",
            font=ctk.CTkFont(family="Inter 18pt", size=11),
            text_color=("#DC2626", "#EF4444"),
            height=20,
        )
        self.login_error.pack()

        # Login button
        ctk.CTkButton(
            card,
            text="Unlock",
            font=ctk.CTkFont(family="Inter 18pt", size=14, weight="bold"),
            width=260,
            height=42,
            corner_radius=10,
            command=self._attempt_login,
        ).pack(pady=(4, 32))

    def _attempt_login(self):
        """Validate the entered password."""
        password = self.login_entry.get()
        if not password.strip():
            self.login_error.configure(text="Please enter a password")
            self.login_entry.configure(border_color=("#DC2626", "#EF4444"))
            return

        if self.state.verify_admin_password(password):
            self.authenticated = True
            self._show_dashboard()
        else:
            self.login_error.configure(text="Incorrect password")
            self.login_entry.configure(border_color=("#DC2626", "#EF4444"))
            self.login_entry.delete(0, "end")
            # Shake-style flash: briefly change background
            self.login_entry.configure(fg_color=("#FEE2E2", "#3B1111"))
            self.after(600, lambda: self.login_entry.configure(
                fg_color=("#FFFFFF", "#27272A"),
                border_color=("#D4D4D8", "#3F3F46"),
            ))

    # ══════════════════════════════════════════════════════════════════
    #  DASHBOARD (post-auth)
    # ══════════════════════════════════════════════════════════════════
    def _show_dashboard(self):
        """Build the full admin dashboard after authentication."""
        self._clear_root()

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ── Title bar ─────────────────────────────────────────────────
        title_row = ctk.CTkFrame(self, fg_color="transparent")
        title_row.grid(row=0, column=0, sticky="ew", padx=4, pady=(0, 8))

        ctk.CTkLabel(
            title_row,
            text="⚙️  Admin Dashboard",
            font=ctk.CTkFont(family="Inter 18pt", size=22, weight="bold"),
            text_color=("#18181B", "#FAFAFA"),
            anchor="w",
        ).pack(side="left")

        # Logout button
        ctk.CTkButton(
            title_row,
            text="🔓  Logout",
            font=ctk.CTkFont(family="Inter 18pt", size=11),
            height=30,
            corner_radius=8,
            fg_color=("transparent"),
            border_width=1,
            border_color=("#DC2626", "#EF4444"),
            text_color=("#DC2626", "#EF4444"),
            hover_color=("#FEE2E2", "#3B1111"),
            command=self._logout,
        ).pack(side="right", padx=(8, 0))

        # Reload button
        ctk.CTkButton(
            title_row,
            text="🔄  Reload Data",
            font=ctk.CTkFont(family="Inter 18pt", size=11),
            height=30,
            corner_radius=8,
            fg_color="transparent",
            border_width=1,
            border_color=("#D4D4D8", "#3F3F46"),
            text_color=("#3F3F46", "#D4D4D8"),
            hover_color=("#E4E4E7", "#27272A"),
            command=self._reload,
        ).pack(side="right")

        # ── Tab bar ───────────────────────────────────────────────────
        tab_bar = ctk.CTkFrame(self, fg_color="transparent")
        tab_bar.grid(row=1, column=0, sticky="ew", padx=4, pady=(0, 8))

        self.tab_buttons = {}
        for tab_key, tab_label in [("inventory", "📦  Inventory"),
                                     ("orders", "📋  Orders"),
                                     ("repairs", "🩺  Repairs"),
                                     ("settings", "🔑  Password")]:
            btn = ctk.CTkButton(
                tab_bar,
                text=tab_label,
                font=ctk.CTkFont(family="Inter 18pt", size=12),
                height=34,
                corner_radius=8,
                command=lambda k=tab_key: self._switch_tab(k),
            )
            btn.pack(side="left", padx=(0, 6))
            self.tab_buttons[tab_key] = btn

        # ── Content area ──────────────────────────────────────────────
        self.content_area = ctk.CTkFrame(self, fg_color="transparent")
        self.content_area.grid(row=2, column=0, sticky="nsew", padx=4)

        self._switch_tab("inventory")
        self.state.subscribe(self._on_state_change)

    def _logout(self):
        """Log out and return to the login screen."""
        self.authenticated = False
        self._show_login()

    # ══════════════════════════════════════════════════════════════════
    #  TAB SWITCHING
    # ══════════════════════════════════════════════════════════════════
    def _switch_tab(self, tab_key: str):
        """Switch between admin tabs."""
        self.active_tab = tab_key
        for key, btn in self.tab_buttons.items():
            if key == tab_key:
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

        for widget in self.content_area.winfo_children():
            widget.destroy()

        if tab_key == "inventory":
            self._build_inventory_tab()
        elif tab_key == "orders":
            self._build_orders_tab()
        elif tab_key == "repairs":
            self._build_repairs_tab()
        elif tab_key == "settings":
            self._build_settings_tab()

    # ══════════════════════════════════════════════════════════════════
    #  SETTINGS / CHANGE PASSWORD TAB
    # ══════════════════════════════════════════════════════════════════
    def _build_settings_tab(self):
        """Render the password change form."""
        container = ctk.CTkFrame(self.content_area, fg_color="transparent")
        container.pack(fill="both", expand=True)

        card = ctk.CTkFrame(
            container,
            width=420,
            fg_color=("#FFFFFF", "#1C1C1F"),
            corner_radius=14,
            border_width=1,
            border_color=("#E4E4E7", "#3F3F46"),
        )
        card.pack(pady=24)
        card.pack_propagate(False)
        card.configure(width=420, height=440)

        ctk.CTkLabel(
            card,
            text="🔑  Change Admin Password",
            font=ctk.CTkFont(family="Inter 18pt", size=17, weight="bold"),
            text_color=("#18181B", "#FAFAFA"),
        ).pack(pady=(24, 16))

        # ── Current password ──────────────────────────────────────────
        ctk.CTkLabel(
            card, text="Current Password *",
            font=ctk.CTkFont(family="Inter 18pt", size=11, weight="bold"),
            text_color=("#3F3F46", "#D4D4D8"), anchor="w",
        ).pack(padx=32, anchor="w")

        self.pw_current = ctk.CTkEntry(
            card, placeholder_text="Enter current password",
            show="•", width=356, height=38,
            font=ctk.CTkFont(family="Inter 18pt", size=12),
        )
        self.pw_current.pack(padx=32, pady=(2, 4))

        # ── Re-enter current password ─────────────────────────────────
        ctk.CTkLabel(
            card, text="Re-enter Current Password *",
            font=ctk.CTkFont(family="Inter 18pt", size=11, weight="bold"),
            text_color=("#3F3F46", "#D4D4D8"), anchor="w",
        ).pack(padx=32, anchor="w")

        self.pw_current_confirm = ctk.CTkEntry(
            card, placeholder_text="Re-enter current password",
            show="•", width=356, height=38,
            font=ctk.CTkFont(family="Inter 18pt", size=12),
        )
        self.pw_current_confirm.pack(padx=32, pady=(2, 4))

        # ── New password ──────────────────────────────────────────────
        ctk.CTkLabel(
            card, text="New Password *",
            font=ctk.CTkFont(family="Inter 18pt", size=11, weight="bold"),
            text_color=("#3F3F46", "#D4D4D8"), anchor="w",
        ).pack(padx=32, anchor="w")

        self.pw_new = ctk.CTkEntry(
            card, placeholder_text="Enter new password (min 3 chars)",
            show="•", width=356, height=38,
            font=ctk.CTkFont(family="Inter 18pt", size=12),
        )
        self.pw_new.pack(padx=32, pady=(2, 8))

        # ── Feedback label ────────────────────────────────────────────
        self.pw_feedback = ctk.CTkLabel(
            card, text="",
            font=ctk.CTkFont(family="Inter 18pt", size=11),
            text_color=("#DC2626", "#EF4444"),
            wraplength=340,
        )
        self.pw_feedback.pack(padx=32, pady=(0, 4))

        # ── Save button ──────────────────────────────────────────────
        ctk.CTkButton(
            card,
            text="Save New Password",
            font=ctk.CTkFont(family="Inter 18pt", size=13, weight="bold"),
            width=356, height=42,
            corner_radius=10,
            command=self._save_password,
        ).pack(padx=32, pady=(0, 24))

    def _save_password(self):
        """Validate inputs and change the admin password."""
        current = self.pw_current.get()
        confirm = self.pw_current_confirm.get()
        new_pw = self.pw_new.get()

        # ── Client-side validation ────────────────────────────────────
        if not current or not confirm or not new_pw:
            self.pw_feedback.configure(
                text="All fields are required.",
                text_color=("#DC2626", "#EF4444"),
            )
            # Highlight empty fields
            for entry, val in [(self.pw_current, current),
                               (self.pw_current_confirm, confirm),
                               (self.pw_new, new_pw)]:
                if not val:
                    entry.configure(border_color=("#DC2626", "#EF4444"))
            return

        if current != confirm:
            self.pw_feedback.configure(
                text="Current password entries do not match.",
                text_color=("#DC2626", "#EF4444"),
            )
            self.pw_current_confirm.configure(border_color=("#DC2626", "#EF4444"))
            self.pw_current_confirm.delete(0, "end")
            return

        # Reset border colours
        for entry in (self.pw_current, self.pw_current_confirm, self.pw_new):
            entry.configure(border_color=("#D4D4D8", "#3F3F46"))

        # ── Delegate to AppState ──────────────────────────────────────
        success, message = self.state.change_admin_password(current, new_pw)

        if success:
            self.pw_feedback.configure(
                text=f"✅  {message}",
                text_color=("#16A34A", "#4ADE80"),
            )
            # Clear fields on success
            for entry in (self.pw_current, self.pw_current_confirm, self.pw_new):
                entry.delete(0, "end")
        else:
            self.pw_feedback.configure(
                text=f"❌  {message}",
                text_color=("#DC2626", "#EF4444"),
            )
            # If current password was wrong, highlight those fields
            if "incorrect" in message.lower():
                self.pw_current.configure(border_color=("#DC2626", "#EF4444"))
                self.pw_current_confirm.configure(border_color=("#DC2626", "#EF4444"))
                self.pw_current.delete(0, "end")
                self.pw_current_confirm.delete(0, "end")

    # ══════════════════════════════════════════════════════════════════
    #  INVENTORY TAB
    # ══════════════════════════════════════════════════════════════════
    def _build_inventory_tab(self):
        scroll = ctk.CTkScrollableFrame(
            self.content_area, fg_color="transparent", label_text="")
        scroll.pack(fill="both", expand=True)
        scroll.grid_columnconfigure(0, weight=1)

        # Prebuilts section
        ctk.CTkLabel(
            scroll,
            text="🖥️  Prebuilt Systems",
            font=ctk.CTkFont(family="Inter 18pt", size=15, weight="bold"),
            text_color=("#18181B", "#FAFAFA"),
            anchor="w",
        ).pack(fill="x", padx=4, pady=(8, 4))

        for pb in self.state.get_prebuilts():
            self._create_stock_row(scroll, pb)

        # Parts sections
        for cat_key, cat_label in [("cpu", "🔲  CPUs"), ("gpu", "🎮  GPUs"),
                                     ("ram", "🧠  RAM"), ("storage", "💾  Storage"),
                                     ("motherboard", "📟  Motherboards"),
                                     ("psu", "🔌  PSUs"), ("case", "🗄️  Cases")]:
            ctk.CTkLabel(
                scroll,
                text=cat_label,
                font=ctk.CTkFont(family="Inter 18pt", size=15, weight="bold"),
                text_color=("#18181B", "#FAFAFA"),
                anchor="w",
            ).pack(fill="x", padx=4, pady=(12, 4))

            for part in self.state.get_parts(cat_key):
                self._create_stock_row(scroll, part)

    def _create_stock_row(self, parent, item: dict):
        """Create an editable stock row for an inventory item."""
        row = ctk.CTkFrame(
            parent,
            corner_radius=8,
            border_width=1,
            border_color=("#E4E4E7", "#3F3F46"),
            fg_color=("#FFFFFF", "#1C1C1F"),
        )
        row.pack(fill="x", padx=4, pady=2)

        inner = ctk.CTkFrame(row, fg_color="transparent")
        inner.pack(fill="x", padx=12, pady=8)

        # Name + price
        ctk.CTkLabel(
            inner,
            text=item["name"],
            font=ctk.CTkFont(family="Inter 18pt", size=12, weight="bold"),
            text_color=("#18181B", "#FAFAFA"),
            anchor="w",
        ).pack(side="left")

        price = item.get("price", 0)
        ctk.CTkLabel(
            inner,
            text=f"${price:,.2f}",
            font=ctk.CTkFont(family="Inter 18pt", size=11),
            text_color=("#71717A", "#A1A1AA"),
        ).pack(side="left", padx=(8, 0))

        # Stock controls (right side)
        controls = ctk.CTkFrame(inner, fg_color="transparent")
        controls.pack(side="right")

        stock = item.get("stock", 0)
        stock_color = ("#16A34A", "#4ADE80") if stock > 5 else (
            ("#EA580C", "#FB923C") if stock > 0 else ("#DC2626", "#EF4444"))

        ctk.CTkLabel(
            controls,
            text=f"Stock: {stock}",
            font=ctk.CTkFont(family="Inter 18pt", size=11),
            text_color=stock_color,
        ).pack(side="left", padx=(0, 8))

        stock_entry = ctk.CTkEntry(
            controls,
            width=60, height=28,
            placeholder_text=str(stock),
            font=ctk.CTkFont(family="Inter 18pt", size=11),
        )
        stock_entry.pack(side="left", padx=(0, 4))

        def update_stock(item_id=item["id"], entry=stock_entry):
            val = entry.get().strip()
            try:
                new_stock = int(val)
                if new_stock < 0:
                    raise ValueError
                self.state.update_stock(item_id, new_stock)
                entry.delete(0, "end")
                self._switch_tab("inventory")  # refresh
            except ValueError:
                entry.delete(0, "end")
                entry.configure(placeholder_text="Invalid!")
                self.after(1500, lambda: entry.configure(
                    placeholder_text=str(item.get("stock", 0))))

        ctk.CTkButton(
            controls,
            text="Update",
            width=60, height=28,
            corner_radius=6,
            font=ctk.CTkFont(family="Inter 18pt", size=10),
            command=update_stock,
        ).pack(side="left")

    # ══════════════════════════════════════════════════════════════════
    #  ORDERS TAB
    # ══════════════════════════════════════════════════════════════════
    def _build_orders_tab(self):
        scroll = ctk.CTkScrollableFrame(
            self.content_area, fg_color="transparent", label_text="")
        scroll.pack(fill="both", expand=True)

        if not self.state.orders:
            ctk.CTkLabel(
                scroll,
                text="No orders yet.",
                font=ctk.CTkFont(family="Inter 18pt", size=14),
                text_color=("#71717A", "#A1A1AA"),
            ).pack(pady=40)
            return

        for order in reversed(self.state.orders):
            card = ctk.CTkFrame(
                scroll,
                corner_radius=10,
                border_width=1,
                border_color=("#E4E4E7", "#3F3F46"),
                fg_color=("#FFFFFF", "#1C1C1F"),
            )
            card.pack(fill="x", padx=4, pady=4)

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=14, pady=(10, 4))

            ctk.CTkLabel(
                top,
                text=order["order_id"],
                font=ctk.CTkFont(family="Inter 18pt", size=13, weight="bold"),
                text_color=("#18181B", "#FAFAFA"),
            ).pack(side="left")

            ctk.CTkLabel(
                top,
                text=f"${order['total']:,.2f}",
                font=ctk.CTkFont(family="Inter 18pt", size=13, weight="bold"),
                text_color=("#2563EB", "#3B82F6"),
            ).pack(side="right")

            # Items list
            items_text = ", ".join(
                f"{i['name']} ×{i['qty']}" for i in order.get("items", [])
            )
            ctk.CTkLabel(
                card,
                text=items_text,
                font=ctk.CTkFont(family="Inter 18pt", size=10),
                text_color=("#71717A", "#A1A1AA"),
                wraplength=400,
                anchor="w",
            ).pack(padx=14, pady=(0, 4), anchor="w")

            # Status dropdown
            status_frame = ctk.CTkFrame(card, fg_color="transparent")
            status_frame.pack(fill="x", padx=14, pady=(0, 10))

            status_color = {
                "Processing": ("#EA580C", "#FB923C"),
                "Confirmed": ("#2563EB", "#3B82F6"),
                "Building": ("#9333EA", "#A855F7"),
                "Shipped": ("#0891B2", "#22D3EE"),
                "Delivered": ("#16A34A", "#4ADE80"),
                "Cancelled": ("#DC2626", "#EF4444"),
            }
            current = order.get("status", "Processing")
            s_color = status_color.get(current, ("#71717A", "#A1A1AA"))

            ctk.CTkLabel(
                status_frame,
                text=f"Status: {current}",
                font=ctk.CTkFont(family="Inter 18pt", size=11, weight="bold"),
                text_color=s_color,
            ).pack(side="left")

            dropdown = ctk.CTkOptionMenu(
                status_frame,
                values=self.ORDER_STATUSES,
                font=ctk.CTkFont(family="Inter 18pt", size=10),
                height=28,
                width=120,
                corner_radius=6,
                command=lambda val, oid=order["order_id"]: self._update_order(oid, val),
            )
            dropdown.set(current)
            dropdown.pack(side="right")

    def _update_order(self, order_id: str, status: str):
        self.state.update_order_status(order_id, status)
        self._switch_tab("orders")

    # ══════════════════════════════════════════════════════════════════
    #  REPAIRS TAB
    # ══════════════════════════════════════════════════════════════════
    def _build_repairs_tab(self):
        scroll = ctk.CTkScrollableFrame(
            self.content_area, fg_color="transparent", label_text="")
        scroll.pack(fill="both", expand=True)

        if not self.state.repair_bookings:
            ctk.CTkLabel(
                scroll,
                text="No repair bookings yet.",
                font=ctk.CTkFont(family="Inter 18pt", size=14),
                text_color=("#71717A", "#A1A1AA"),
            ).pack(pady=40)
            return

        for booking in reversed(self.state.repair_bookings):
            card = ctk.CTkFrame(
                scroll,
                corner_radius=10,
                border_width=1,
                border_color=("#E4E4E7", "#3F3F46"),
                fg_color=("#FFFFFF", "#1C1C1F"),
            )
            card.pack(fill="x", padx=4, pady=4)

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=14, pady=(10, 2))

            ctk.CTkLabel(
                top,
                text=booking.get("booking_id", "N/A"),
                font=ctk.CTkFont(family="Inter 18pt", size=13, weight="bold"),
                text_color=("#18181B", "#FAFAFA"),
            ).pack(side="left")

            ctk.CTkLabel(
                top,
                text=booking.get("status", "Scheduled"),
                font=ctk.CTkFont(family="Inter 18pt", size=11, weight="bold"),
                text_color=("#EA580C", "#FB923C"),
            ).pack(side="right")

            details = [
                f"🔧  Service: {booking.get('service', 'N/A')}",
                f"👤  Customer: {booking.get('customer_name', 'N/A')}",
                f"📧  Email: {booking.get('customer_email', 'N/A')}",
                f"📅  Est. completion: {booking.get('est_completion', 'N/A')}",
            ]
            for detail in details:
                ctk.CTkLabel(
                    card,
                    text=detail,
                    font=ctk.CTkFont(family="Inter 18pt", size=11),
                    text_color=("#3F3F46", "#D4D4D8"),
                    anchor="w",
                ).pack(padx=14, pady=1, anchor="w")

            ctk.CTkLabel(
                card,
                text=f"📝  {booking.get('description', '')[:100]}",
                font=ctk.CTkFont(family="Inter 18pt", size=10),
                text_color=("#71717A", "#A1A1AA"),
                anchor="w",
                wraplength=400,
            ).pack(padx=14, pady=(2, 10), anchor="w")

    # ══════════════════════════════════════════════════════════════════
    #  HELPERS
    # ══════════════════════════════════════════════════════════════════
    def _clear_root(self):
        """Remove all child widgets from this frame."""
        for widget in self.winfo_children():
            widget.destroy()

    def _reload(self):
        """Reload inventory from disk and refresh view."""
        self.state.reload_inventory()
        self._switch_tab(self.active_tab)

    def _on_state_change(self):
        """React to global state changes."""
        if self.authenticated and self.active_tab in ("orders", "repairs"):
            self._switch_tab(self.active_tab)
