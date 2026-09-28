"""
Custom Build View – interactive PC builder with real-time C++ compatibility checks.
"""
import customtkinter as ctk
from data.app_state import AppState


class CustomBuildView(ctk.CTkFrame):
    """Custom PC builder with part selection and live compatibility feedback."""

    CATEGORIES = [
        ("cpu",         "🔲  CPU"),
        ("gpu",         "🎮  GPU"),
        ("ram",         "🧠  RAM"),
        ("storage",     "💾  Storage"),
        ("motherboard", "📟  Motherboard"),
        ("psu",         "🔌  PSU"),
        ("case",        "🗄️  Case"),
    ]

    def __init__(self, parent, assistant_drawer=None):
        super().__init__(parent, fg_color="transparent")
        self.state = AppState()
        self.assistant = assistant_drawer
        self.selections: dict[str, dict | None] = {cat: None for cat, _ in self.CATEGORIES}
        self.dropdowns: dict[str, ctk.CTkOptionMenu] = {}

        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ── Title ─────────────────────────────────────────────────────
        title_row = ctk.CTkFrame(self, fg_color="transparent")
        title_row.grid(row=0, column=0, sticky="ew", padx=4, pady=(0, 4))

        ctk.CTkLabel(
            title_row,
            text="🔧  Custom Build",
            font=ctk.CTkFont(family="Inter 18pt", size=22, weight="bold"),
            text_color=("#18181B", "#FAFAFA"),
            anchor="w",
        ).pack(side="left")

        # Advisor toggle
        if self.assistant:
            ctk.CTkButton(
                title_row,
                text="🤖  Advisor",
                font=ctk.CTkFont(family="Inter 18pt", size=11),
                height=32,
                corner_radius=8,
                fg_color=("#9333EA", "#A855F7"),
                hover_color=("#7E22CE", "#9333EA"),
                command=self.assistant.toggle,
            ).pack(side="right")

        # ── Part selection grid ───────────────────────────────────────
        parts_frame = ctk.CTkFrame(self, fg_color=("#FFFFFF", "#1C1C1F"),
                                    corner_radius=12, border_width=1,
                                    border_color=("#E4E4E7", "#3F3F46"))
        parts_frame.grid(row=1, column=0, sticky="ew", padx=4, pady=(0, 8))
        parts_frame.grid_columnconfigure(1, weight=1)

        for idx, (category, label) in enumerate(self.CATEGORIES):
            # Label
            ctk.CTkLabel(
                parts_frame,
                text=label,
                font=ctk.CTkFont(family="Inter 18pt", size=13, weight="bold"),
                text_color=("#3F3F46", "#D4D4D8"),
                anchor="w",
            ).grid(row=idx, column=0, padx=(16, 8), pady=8, sticky="w")

            # Build options
            parts = self.state.get_parts(category)
            options = ["— Select —"] + [
                f"{p['name']}  |  ${p['price']:,.2f}  ({p['stock']} left)"
                for p in parts if p.get("stock", 0) > 0
            ]

            dropdown = ctk.CTkOptionMenu(
                parts_frame,
                values=options,
                font=ctk.CTkFont(family="Inter 18pt", size=11),
                height=34,
                corner_radius=8,
                fg_color=("#F4F4F5", "#27272A"),
                button_color=("#D4D4D8", "#3F3F46"),
                button_hover_color=("#A1A1AA", "#52525B"),
                text_color=("#18181B", "#FAFAFA"),
                command=lambda val, cat=category: self._on_select(cat, val),
            )
            dropdown.set("— Select —")
            dropdown.grid(row=idx, column=1, padx=(0, 16), pady=8, sticky="ew")
            self.dropdowns[category] = dropdown

        # ── Compatibility result summary ──────────────────────────────
        self.compat_frame = ctk.CTkFrame(
            self, fg_color=("#F4F4F5", "#18181B"),
            corner_radius=12, border_width=1,
            border_color=("#E4E4E7", "#3F3F46"),
        )
        self.compat_frame.grid(row=2, column=0, sticky="ew", padx=4, pady=(0, 8))

        self.compat_label = ctk.CTkLabel(
            self.compat_frame,
            text="Select components above to check compatibility",
            font=ctk.CTkFont(family="Inter 18pt", size=12),
            text_color=("#71717A", "#A1A1AA"),
        )
        self.compat_label.pack(padx=16, pady=12)

        # ── Action buttons ────────────────────────────────────────────
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.grid(row=3, column=0, sticky="sew", padx=4, pady=(0, 4))

        self.total_label = ctk.CTkLabel(
            actions_frame,
            text="Build Total:  $0.00",
            font=ctk.CTkFont(family="Inter 18pt", size=16, weight="bold"),
            text_color=("#2563EB", "#3B82F6"),
        )
        self.total_label.pack(side="left")

        self.add_build_btn = ctk.CTkButton(
            actions_frame,
            text="Add Build to Cart",
            font=ctk.CTkFont(family="Inter 18pt", size=13, weight="bold"),
            height=38,
            corner_radius=8,
            state="disabled",
            command=self._add_build_to_cart,
        )
        self.add_build_btn.pack(side="right")

        ctk.CTkButton(
            actions_frame,
            text="Reset",
            font=ctk.CTkFont(family="Inter 18pt", size=12),
            height=38,
            corner_radius=8,
            fg_color="transparent",
            border_width=1,
            border_color=("#D4D4D8", "#3F3F46"),
            text_color=("#3F3F46", "#D4D4D8"),
            hover_color=("#E4E4E7", "#27272A"),
            command=self._reset,
        ).pack(side="right", padx=(0, 8))

    def _on_select(self, category: str, value: str):
        """Handle part selection from dropdown."""
        if value == "— Select —":
            self.selections[category] = None
        else:
            # Parse part from display string
            name = value.split("  |  ")[0].strip()
            parts = self.state.get_parts(category)
            for part in parts:
                if part["name"] == name:
                    self.selections[category] = part
                    break

        self._update_total()
        self._run_compatibility()

    def _update_total(self):
        """Recalculate and display build total."""
        total = sum(
            p["price"] for p in self.selections.values() if p is not None
        )
        self.total_label.configure(text=f"Build Total:  ${total:,.2f}")

        # Enable add-to-cart if at least CPU + GPU + motherboard selected
        core_parts = ["cpu", "gpu", "motherboard"]
        has_core = all(self.selections.get(c) is not None for c in core_parts)
        self.add_build_btn.configure(state="normal" if has_core else "disabled")

    def _run_compatibility(self):
        """Run C++ compatibility checks if enough parts are selected."""
        cpu = self.selections.get("cpu")
        mb = self.selections.get("motherboard")
        ram = self.selections.get("ram")
        gpu = self.selections.get("gpu")
        psu = self.selections.get("psu")

        if not cpu or not mb:
            self.compat_label.configure(
                text="Select at least CPU & Motherboard to check compatibility",
                text_color=("#71717A", "#A1A1AA"),
            )
            return

        try:
            import pc_engine

            cpu_socket = cpu.get("socket", "")
            mb_chipset = mb.get("name", "").split()[0]  # e.g. "B650" from "B650 ATX"
            ram_type = ram.get("type", "DDR5") if ram else "DDR5"
            cpu_tdp = cpu.get("tdp_w", 100)
            gpu_tdp = gpu.get("tdp_w", 200) if gpu else 200
            psu_w = psu.get("wattage", 750) if psu else 750

            result = pc_engine.full_compatibility_check(
                cpu_socket, mb_chipset, ram_type,
                cpu_tdp, gpu_tdp, psu_w,
            )

            if result.compatible and not result.warnings:
                self.compat_label.configure(
                    text="✅  All selected components are compatible!",
                    text_color=("#16A34A", "#4ADE80"),
                )
            elif result.compatible:
                msgs = "\n".join(f"⚠️ {w}" for w in result.warnings)
                self.compat_label.configure(
                    text=f"⚠️  Compatible with warnings:\n{msgs}",
                    text_color=("#EA580C", "#FB923C"),
                )
            else:
                msgs = "\n".join(f"❌ {e}" for e in result.errors)
                warns = "\n".join(f"⚠️ {w}" for w in result.warnings)
                full = msgs + ("\n" + warns if warns else "")
                self.compat_label.configure(
                    text=f"❌  Issues found:\n{full}",
                    text_color=("#DC2626", "#EF4444"),
                )

            # Update assistant drawer
            if self.assistant and self.assistant.is_open:
                base_draw = 75
                total_power = cpu_tdp + gpu_tdp + base_draw
                headroom = int(((psu_w / total_power) - 1.0) * 100) if total_power > 0 else 0
                self.assistant.show_results(result, {
                    "total_power": total_power,
                    "psu_headroom": headroom,
                })

        except ImportError:
            self.compat_label.configure(
                text="⚠️  C++ engine not loaded – compatibility checks unavailable",
                text_color=("#EA580C", "#FB923C"),
            )

    def _add_build_to_cart(self):
        """Add the complete custom build to the cart."""
        parts_list = [p for p in self.selections.values() if p is not None]
        if not parts_list:
            return

        names = " + ".join(p["name"] for p in parts_list[:3])
        if len(parts_list) > 3:
            names += f" +{len(parts_list)-3} more"
        total = sum(p["price"] for p in parts_list)

        self.state.add_to_cart(
            item_id=f"CUSTOM-{hash(tuple(p['id'] for p in parts_list)) & 0xFFFF:04X}",
            name=f"Custom Build ({names})",
            price=total,
            qty=1,
            category="custom_build",
        )
        self._show_toast("✅  Custom build added to cart!")
        self._reset()

    def _reset(self):
        """Clear all selections."""
        for cat, _ in self.CATEGORIES:
            self.selections[cat] = None
            self.dropdowns[cat].set("— Select —")
        self._update_total()
        self.compat_label.configure(
            text="Select components above to check compatibility",
            text_color=("#71717A", "#A1A1AA"),
        )

    def _show_toast(self, message: str):
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
