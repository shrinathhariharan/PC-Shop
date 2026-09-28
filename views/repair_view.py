"""
Repair View – device repair & diagnostic scheduler with form validation.
"""
import re
from datetime import datetime, timedelta
import customtkinter as ctk
from data.app_state import AppState


class RepairView(ctk.CTkFrame):
    """Repair service browser and appointment scheduler."""

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.state = AppState()

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ── Title ─────────────────────────────────────────────────────
        title_row = ctk.CTkFrame(self, fg_color="transparent")
        title_row.grid(row=0, column=0, sticky="ew", padx=4, pady=(0, 8))

        ctk.CTkLabel(
            title_row,
            text="🩺  Repair & Diagnostics",
            font=ctk.CTkFont(family="Inter 18pt", size=22, weight="bold"),
            text_color=("#18181B", "#FAFAFA"),
            anchor="w",
        ).pack(side="left")

        # ── Content: services list + booking form side by side ────────
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=4)
        content.grid_columnconfigure(0, weight=3)
        content.grid_columnconfigure(1, weight=2)
        content.grid_rowconfigure(0, weight=1)

        # ── Left: services catalog ────────────────────────────────────
        services_frame = ctk.CTkScrollableFrame(
            content, fg_color="transparent",
            label_text="Available Services",
            label_font=ctk.CTkFont(family="Inter 18pt", size=13, weight="bold"),
        )
        services_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self.selected_service = None
        self.service_cards: list[ctk.CTkFrame] = []

        for service in self.state.get_repair_services():
            card = self._create_service_card(services_frame, service)
            card.pack(fill="x", padx=4, pady=4)
            self.service_cards.append(card)

        # ── Right: booking form ───────────────────────────────────────
        form_frame = ctk.CTkFrame(
            content,
            fg_color=("#FFFFFF", "#1C1C1F"),
            corner_radius=12,
            border_width=1,
            border_color=("#E4E4E7", "#3F3F46"),
        )
        form_frame.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(
            form_frame,
            text="📝  Schedule Repair",
            font=ctk.CTkFont(family="Inter 18pt", size=15, weight="bold"),
            text_color=("#18181B", "#FAFAFA"),
            anchor="w",
        ).pack(padx=16, pady=(16, 12), anchor="w")

        # Selected service display
        self.selected_label = ctk.CTkLabel(
            form_frame,
            text="No service selected",
            font=ctk.CTkFont(family="Inter 18pt", size=12),
            text_color=("#71717A", "#A1A1AA"),
            anchor="w",
        )
        self.selected_label.pack(padx=16, pady=(0, 8), anchor="w")

        # Customer name
        ctk.CTkLabel(
            form_frame, text="Full Name *",
            font=ctk.CTkFont(family="Inter 18pt", size=11, weight="bold"),
            text_color=("#3F3F46", "#D4D4D8"), anchor="w",
        ).pack(padx=16, pady=(8, 2), anchor="w")

        self.name_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="John Doe",
            height=36,
            font=ctk.CTkFont(family="Inter 18pt", size=12),
        )
        self.name_entry.pack(padx=16, fill="x")

        self.name_error = ctk.CTkLabel(
            form_frame, text="",
            font=ctk.CTkFont(family="Inter 18pt", size=10),
            text_color=("#DC2626", "#EF4444"), anchor="w",
        )
        self.name_error.pack(padx=16, anchor="w")

        # Email
        ctk.CTkLabel(
            form_frame, text="Email *",
            font=ctk.CTkFont(family="Inter 18pt", size=11, weight="bold"),
            text_color=("#3F3F46", "#D4D4D8"), anchor="w",
        ).pack(padx=16, pady=(4, 2), anchor="w")

        self.email_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="john@example.com",
            height=36,
            font=ctk.CTkFont(family="Inter 18pt", size=12),
        )
        self.email_entry.pack(padx=16, fill="x")

        self.email_error = ctk.CTkLabel(
            form_frame, text="",
            font=ctk.CTkFont(family="Inter 18pt", size=10),
            text_color=("#DC2626", "#EF4444"), anchor="w",
        )
        self.email_error.pack(padx=16, anchor="w")

        # Phone
        ctk.CTkLabel(
            form_frame, text="Phone",
            font=ctk.CTkFont(family="Inter 18pt", size=11, weight="bold"),
            text_color=("#3F3F46", "#D4D4D8"), anchor="w",
        ).pack(padx=16, pady=(4, 2), anchor="w")

        self.phone_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="(555) 123-4567",
            height=36,
            font=ctk.CTkFont(family="Inter 18pt", size=12),
        )
        self.phone_entry.pack(padx=16, fill="x")

        self.phone_error = ctk.CTkLabel(
            form_frame, text="",
            font=ctk.CTkFont(family="Inter 18pt", size=10),
            text_color=("#DC2626", "#EF4444"), anchor="w",
        )
        self.phone_error.pack(padx=16, anchor="w")

        # Device description
        ctk.CTkLabel(
            form_frame, text="Device / Issue Description *",
            font=ctk.CTkFont(family="Inter 18pt", size=11, weight="bold"),
            text_color=("#3F3F46", "#D4D4D8"), anchor="w",
        ).pack(padx=16, pady=(4, 2), anchor="w")

        self.desc_textbox = ctk.CTkTextbox(
            form_frame,
            height=80,
            font=ctk.CTkFont(family="Inter 18pt", size=11),
            corner_radius=6,
            border_width=2,
            border_color=("#D4D4D8", "#3F3F46"),
        )
        self.desc_textbox.pack(padx=16, fill="x")

        self.desc_error = ctk.CTkLabel(
            form_frame, text="",
            font=ctk.CTkFont(family="Inter 18pt", size=10),
            text_color=("#DC2626", "#EF4444"), anchor="w",
        )
        self.desc_error.pack(padx=16, anchor="w")

        # Submit button
        self.submit_btn = ctk.CTkButton(
            form_frame,
            text="Schedule Repair",
            font=ctk.CTkFont(family="Inter 18pt", size=13, weight="bold"),
            height=40,
            corner_radius=8,
            command=self._submit,
        )
        self.submit_btn.pack(padx=16, pady=(8, 16), fill="x")

        # ── Confirmation area ─────────────────────────────────────────
        self.confirmation_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.confirmation_frame.grid(row=2, column=0, sticky="ew", padx=4, pady=(8, 0))

    def _create_service_card(self, parent, service: dict) -> ctk.CTkFrame:
        """Build a clickable service card."""
        card = ctk.CTkFrame(
            parent,
            corner_radius=10,
            border_width=1,
            border_color=("#E4E4E7", "#3F3F46"),
            fg_color=("#FFFFFF", "#1C1C1F"),
            cursor="hand2",
        )

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=12, pady=(10, 2))

        ctk.CTkLabel(
            top,
            text=service["name"],
            font=ctk.CTkFont(family="Inter 18pt", size=13, weight="bold"),
            text_color=("#18181B", "#FAFAFA"),
            anchor="w",
        ).pack(side="left")

        ctk.CTkLabel(
            top,
            text=f"${service['price']:,.2f}",
            font=ctk.CTkFont(family="Inter 18pt", size=13, weight="bold"),
            text_color=("#2563EB", "#3B82F6"),
        ).pack(side="right")

        ctk.CTkLabel(
            card,
            text=service["description"],
            font=ctk.CTkFont(family="Inter 18pt", size=11),
            text_color=("#71717A", "#A1A1AA"),
            anchor="w",
            wraplength=300,
        ).pack(fill="x", padx=12, pady=(0, 2))

        ctk.CTkLabel(
            card,
            text=f"⏱️  Est. {service['duration_days']} day{'s' if service['duration_days'] > 1 else ''}",
            font=ctk.CTkFont(family="Inter 18pt", size=10),
            text_color=("#71717A", "#71717A"),
            anchor="w",
        ).pack(fill="x", padx=12, pady=(0, 10))

        # Bind click
        def select(e=None, s=service, c=card):
            self._select_service(s, c)

        for widget in [card] + list(card.winfo_children()):
            widget.bind("<Button-1>", select)
            for child in widget.winfo_children():
                child.bind("<Button-1>", select)

        return card

    def _select_service(self, service: dict, card: ctk.CTkFrame):
        """Mark a service as selected."""
        self.selected_service = service
        self.selected_label.configure(
            text=f"✅  {service['name']}  —  ${service['price']:,.2f}",
            text_color=("#16A34A", "#4ADE80"),
        )
        # Highlight selected card
        for sc in self.service_cards:
            sc.configure(border_color=("#E4E4E7", "#3F3F46"))
        card.configure(border_color=("#2563EB", "#3B82F6"))

    def _validate(self) -> bool:
        """Validate all form fields.  Returns True if valid."""
        valid = True

        # Name
        name = self.name_entry.get().strip()
        if not name:
            self.name_error.configure(text="Name is required")
            self.name_entry.configure(border_color=("#DC2626", "#EF4444"))
            valid = False
        elif len(name) < 2:
            self.name_error.configure(text="Name must be at least 2 characters")
            self.name_entry.configure(border_color=("#DC2626", "#EF4444"))
            valid = False
        else:
            self.name_error.configure(text="")
            self.name_entry.configure(border_color=("#D4D4D8", "#3F3F46"))

        # Email
        email = self.email_entry.get().strip()
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not email:
            self.email_error.configure(text="Email is required")
            self.email_entry.configure(border_color=("#DC2626", "#EF4444"))
            valid = False
        elif not re.match(email_pattern, email):
            self.email_error.configure(text="Enter a valid email address")
            self.email_entry.configure(border_color=("#DC2626", "#EF4444"))
            valid = False
        else:
            self.email_error.configure(text="")
            self.email_entry.configure(border_color=("#D4D4D8", "#3F3F46"))

        # Phone (optional but validate format if provided)
        phone = self.phone_entry.get().strip()
        if phone:
            digits_only = re.sub(r'\D', '', phone)
            if len(digits_only) < 10 or len(digits_only) > 15:
                self.phone_error.configure(text="Enter a valid phone number")
                self.phone_entry.configure(border_color=("#DC2626", "#EF4444"))
                valid = False
            else:
                self.phone_error.configure(text="")
                self.phone_entry.configure(border_color=("#D4D4D8", "#3F3F46"))
        else:
            self.phone_error.configure(text="")
            self.phone_entry.configure(border_color=("#D4D4D8", "#3F3F46"))

        # Description
        desc = self.desc_textbox.get("1.0", "end-1c").strip()
        if not desc:
            self.desc_error.configure(text="Please describe the issue")
            self.desc_textbox.configure(border_color=("#DC2626", "#EF4444"))
            valid = False
        elif len(desc) < 10:
            self.desc_error.configure(text="Please provide more detail (min 10 chars)")
            self.desc_textbox.configure(border_color=("#DC2626", "#EF4444"))
            valid = False
        else:
            self.desc_error.configure(text="")
            self.desc_textbox.configure(border_color=("#D4D4D8", "#3F3F46"))

        # Service
        if not self.selected_service:
            self.selected_label.configure(
                text="⚠️  Please select a service first",
                text_color=("#DC2626", "#EF4444"),
            )
            valid = False

        return valid

    def _submit(self):
        """Validate and submit the repair booking."""
        if not self._validate():
            return

        booking = self.state.add_repair_booking({
            "service": self.selected_service["name"],
            "service_id": self.selected_service["id"],
            "price": self.selected_service["price"],
            "customer_name": self.name_entry.get().strip(),
            "customer_email": self.email_entry.get().strip(),
            "customer_phone": self.phone_entry.get().strip(),
            "description": self.desc_textbox.get("1.0", "end-1c").strip(),
            "est_completion": (
                datetime.now() +
                timedelta(days=self.selected_service["duration_days"])
            ).strftime("%B %d, %Y"),
        })

        # Show confirmation
        for widget in self.confirmation_frame.winfo_children():
            widget.destroy()

        conf = ctk.CTkFrame(
            self.confirmation_frame,
            fg_color=("#DCFCE7", "#14532D"),
            corner_radius=10,
        )
        conf.pack(fill="x", padx=4)

        ctk.CTkLabel(
            conf,
            text=f"✅  Repair booked!  ID: {booking['booking_id']}",
            font=ctk.CTkFont(family="Inter 18pt", size=13, weight="bold"),
            text_color=("#16A34A", "#4ADE80"),
        ).pack(padx=16, pady=(12, 2))

        ctk.CTkLabel(
            conf,
            text=f"Service: {self.selected_service['name']}  |  "
                 f"Est. completion: {booking.get('est_completion', 'N/A')}",
            font=ctk.CTkFont(family="Inter 18pt", size=11),
            text_color=("#166534", "#86EFAC"),
        ).pack(padx=16, pady=(0, 12))

        # Reset form
        self._reset_form()

    def _reset_form(self):
        """Clear all form fields."""
        self.name_entry.delete(0, "end")
        self.email_entry.delete(0, "end")
        self.phone_entry.delete(0, "end")
        self.desc_textbox.delete("1.0", "end")
        self.selected_service = None
        self.selected_label.configure(
            text="No service selected",
            text_color=("#71717A", "#A1A1AA"),
        )
        for sc in self.service_cards:
            sc.configure(border_color=("#E4E4E7", "#3F3F46"))
        # Clear errors
        for lbl in [self.name_error, self.email_error, self.phone_error, self.desc_error]:
            lbl.configure(text="")
