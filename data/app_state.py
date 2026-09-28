"""
Global application state management for cart, orders, and dynamic totals.
Thread-safe singleton pattern for consistent state across all views.
"""
import hashlib
import json
import os
from datetime import datetime

# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------
_DATA_DIR = os.path.dirname(os.path.abspath(__file__))
_INVENTORY_PATH = os.path.join(_DATA_DIR, "inventory.json")
_ADMIN_PW_PATH = os.path.join(_DATA_DIR, "admin_pw.json")


def _load_inventory():
    """Load inventory data from disk."""
    with open(_INVENTORY_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _save_inventory(data):
    """Persist inventory data to disk."""
    with open(_INVENTORY_PATH, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


# ---------------------------------------------------------------------------
# AppState singleton
# ---------------------------------------------------------------------------
class AppState:
    """Centralised, observable application state."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialised = False
        return cls._instance

    def __init__(self):
        if self._initialised:
            return
        self._initialised = True

        # Cart: list of dicts  {id, name, price, qty, category}
        self.cart: list[dict] = []

        # Order history: list of completed order dicts
        self.orders: list[dict] = []

        # Repair bookings: list of repair request dicts
        self.repair_bookings: list[dict] = []

        # Budget tracker
        self.budget: float = 0.0
        self.budget_enabled: bool = False

        # Observers – callables notified on state changes
        self._listeners: list = []

        # Load inventory
        self.inventory_data = _load_inventory()

        # C++ engine status
        self.engine_loaded: bool = False

        # Admin password (initialise file if missing)
        self._init_admin_password()

    # -- Observer pattern ------------------------------------------------
    def subscribe(self, callback):
        """Register a callback to be invoked on state change."""
        if callback not in self._listeners:
            self._listeners.append(callback)

    def unsubscribe(self, callback):
        """Remove a previously-registered callback."""
        self._listeners = [cb for cb in self._listeners if cb is not callback]

    def _notify(self):
        """Notify all observers of state change."""
        for cb in self._listeners:
            try:
                cb()
            except Exception:
                pass

    # -- Cart operations -------------------------------------------------
    def add_to_cart(self, item_id: str, name: str, price: float,
                    qty: int = 1, category: str = "prebuilt"):
        """Add or increment an item in the cart."""
        for item in self.cart:
            if item["id"] == item_id:
                item["qty"] += qty
                self._notify()
                return
        self.cart.append({
            "id": item_id,
            "name": name,
            "price": price,
            "qty": qty,
            "category": category,
        })
        self._notify()

    def remove_from_cart(self, item_id: str):
        """Remove an item from the cart entirely."""
        self.cart = [i for i in self.cart if i["id"] != item_id]
        self._notify()

    def update_cart_qty(self, item_id: str, qty: int):
        """Set quantity for a cart item.  Removes if qty <= 0."""
        if qty <= 0:
            self.remove_from_cart(item_id)
            return
        for item in self.cart:
            if item["id"] == item_id:
                item["qty"] = qty
                break
        self._notify()

    def clear_cart(self):
        """Empty the cart."""
        self.cart.clear()
        self._notify()

    def cart_total(self) -> float:
        """Return the cart's monetary total."""
        return sum(i["price"] * i["qty"] for i in self.cart)

    def cart_count(self) -> int:
        """Return total number of items."""
        return sum(i["qty"] for i in self.cart)

    # -- Budget ----------------------------------------------------------
    def set_budget(self, amount: float):
        """Set a budget cap."""
        self.budget = max(0.0, amount)
        self.budget_enabled = True
        self._notify()

    def clear_budget(self):
        self.budget = 0.0
        self.budget_enabled = False
        self._notify()

    def budget_remaining(self) -> float:
        return self.budget - self.cart_total()

    # -- Checkout --------------------------------------------------------
    def checkout(self) -> dict:
        """Finalise the current cart into an order, decrement stock."""
        if not self.cart:
            return {}
        order = {
            "order_id": f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "items": list(self.cart),
            "total": self.cart_total(),
            "date": datetime.now().isoformat(),
            "status": "Processing",
        }
        # Decrement stock
        inv = self.inventory_data
        for ci in self.cart:
            # Prebuilts
            for pb in inv.get("prebuilts", []):
                if pb["id"] == ci["id"]:
                    pb["stock"] = max(0, pb["stock"] - ci["qty"])
            # Parts
            for cat_parts in inv.get("parts", {}).values():
                for part in cat_parts:
                    if part["id"] == ci["id"]:
                        part["stock"] = max(0, part["stock"] - ci["qty"])
        _save_inventory(inv)
        self.orders.append(order)
        self.clear_cart()
        return order

    # -- Repair bookings -------------------------------------------------
    def add_repair_booking(self, booking: dict):
        """Add a repair booking."""
        booking["booking_id"] = f"RPR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        booking["date"] = datetime.now().isoformat()
        booking["status"] = "Scheduled"
        self.repair_bookings.append(booking)
        self._notify()
        return booking

    # -- Inventory helpers -----------------------------------------------
    def get_prebuilts(self) -> list:
        return self.inventory_data.get("prebuilts", [])

    def get_parts(self, category: str | None = None) -> dict | list:
        parts = self.inventory_data.get("parts", {})
        if category:
            return parts.get(category, [])
        return parts

    def get_repair_services(self) -> list:
        return self.inventory_data.get("repair_services", [])

    def reload_inventory(self):
        """Reload inventory from disk."""
        self.inventory_data = _load_inventory()
        self._notify()

    def update_stock(self, item_id: str, new_stock: int):
        """Admin: update stock for any item."""
        inv = self.inventory_data
        for pb in inv.get("prebuilts", []):
            if pb["id"] == item_id:
                pb["stock"] = max(0, new_stock)
                _save_inventory(inv)
                self._notify()
                return
        for cat_parts in inv.get("parts", {}).values():
            for part in cat_parts:
                if part["id"] == item_id:
                    part["stock"] = max(0, new_stock)
                    _save_inventory(inv)
                    self._notify()
                    return

    def update_order_status(self, order_id: str, status: str):
        """Admin: update an order's status."""
        for order in self.orders:
            if order["order_id"] == order_id:
                order["status"] = status
                self._notify()
                return

    # -- Admin password ---------------------------------------------------
    @staticmethod
    def _hash_pw(password: str) -> str:
        """Return a SHA-256 hex digest of the password."""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def _init_admin_password(self):
        """Create the password file with the default if it doesn't exist."""
        if not os.path.exists(_ADMIN_PW_PATH):
            data = {"password_hash": self._hash_pw("pc shop")}
            with open(_ADMIN_PW_PATH, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2)

    def _load_password_hash(self) -> str:
        """Read the stored password hash from disk."""
        with open(_ADMIN_PW_PATH, "r", encoding="utf-8") as fh:
            return json.load(fh).get("password_hash", "")

    def verify_admin_password(self, password: str) -> bool:
        """Return True if *password* matches the stored admin password."""
        return self._hash_pw(password) == self._load_password_hash()

    def change_admin_password(self, current: str, new: str) -> tuple[bool, str]:
        """
        Change the admin password.

        Returns (success: bool, message: str).
        """
        if not self.verify_admin_password(current):
            return False, "Current password is incorrect."
        if len(new) < 3:
            return False, "New password must be at least 3 characters."
        if current == new:
            return False, "New password must be different from the current one."
        data = {"password_hash": self._hash_pw(new)}
        with open(_ADMIN_PW_PATH, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
        return True, "Password changed successfully."
