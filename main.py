"""
PC Shop – Desktop application for browsing prebuilts, building custom PCs,
scheduling repairs, and managing orders.

Entry point: initialises the CustomTkinter window, navigation, and
wires together all views and components.
"""
import customtkinter as ctk
from components.header import Header
from components.sidebar import Sidebar
from components.footer import Footer
from components.assistant_drawer import AssistantDrawer
from views.prebuilts_view import PrebuiltsView
from views.custom_build_view import CustomBuildView
from views.repair_view import RepairView
from views.cart_view import CartView
from views.owner_view import OwnerView


class App(ctk.CTk):
    """Main application window with view-based navigation."""

    VIEW_MAP = {
        "prebuilts": PrebuiltsView,
        "custom_build": CustomBuildView,
        "repair": RepairView,
        "cart": CartView,
        "owner": OwnerView,
    }

    def __init__(self):
        super().__init__()

        self.title("PC Shop ⚡ Build · Buy · Repair")
        self.geometry("1200x780")
        self.minsize(900, 600)

        # ── Grid layout ───────────────────────────────────────────────
        # Row 0: Header
        # Row 1: Sidebar (col 0) + Content (col 1) + Assistant (col 2)
        # Row 2: Footer
        self.grid_columnconfigure(0, weight=0)   # sidebar
        self.grid_columnconfigure(1, weight=1)   # content
        self.grid_columnconfigure(2, weight=0)   # assistant drawer
        self.grid_rowconfigure(0, weight=0)       # header
        self.grid_rowconfigure(1, weight=1)       # main content
        self.grid_rowconfigure(2, weight=0)       # footer

        # ── Header ────────────────────────────────────────────────────
        self.header = Header(self)
        self.header.grid(row=0, column=0, columnspan=3, sticky="ew")

        # ── Assistant drawer (created first so Custom Build can reference it) ──
        self.assistant = AssistantDrawer(self)
        # Starts hidden; opened from Custom Build view

        # ── Sidebar ───────────────────────────────────────────────────
        self.sidebar = Sidebar(self, navigate_callback=self.navigate)
        self.sidebar.grid(row=1, column=0, sticky="nsew", rowspan=2)

        # ── Content area ──────────────────────────────────────────────
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=1, column=1, sticky="nsew", padx=12, pady=10)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # ── Footer ────────────────────────────────────────────────────
        self.footer = Footer(self)
        self.footer.grid(row=2, column=1, columnspan=2, sticky="ew")

        # ── Current view tracking ─────────────────────────────────────
        self.current_view = None
        self.navigate("prebuilts")

    def navigate(self, view_key: str):
        """Switch the main content area to a different view."""
        # Destroy current view
        if self.current_view is not None:
            self.current_view.destroy()
            self.current_view = None

        # Close assistant unless going to custom_build
        if view_key != "custom_build" and self.assistant.is_open:
            self.assistant.close()

        # Create new view
        view_class = self.VIEW_MAP.get(view_key)
        if view_class is None:
            return

        if view_class is CustomBuildView:
            self.current_view = view_class(self.content_frame,
                                            assistant_drawer=self.assistant)
        else:
            self.current_view = view_class(self.content_frame)

        self.current_view.grid(row=0, column=0, sticky="nsew")


if __name__ == "__main__":
    ctk.set_default_color_theme("data/theme.json")
    app = App()
    app.mainloop()
