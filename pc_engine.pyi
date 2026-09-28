"""Type stub for the pc_engine C++ pybind11 extension module."""

from typing import List, Tuple

class CompatResult:
    compatible: bool
    warnings: List[str]
    errors: List[str]
    def __init__(self, *args, **kwargs) -> None: ...
    def __repr__(self) -> str: ...

class PriceBreakdown:
    unit_price: float
    quantity: int
    discount_pct: float
    subtotal: float
    discount_amount: float
    total: float
    def __init__(self, *args, **kwargs) -> None: ...
    def __repr__(self) -> str: ...

def check_socket_compat(cpu_socket: str, mb_chipset: str) -> CompatResult:
    """Check CPU socket <-> motherboard chipset compatibility."""
    ...

def check_ram_compat(cpu_socket: str, ram_type: str) -> CompatResult:
    """Check RAM type compatibility for a CPU socket."""
    ...

def check_power(cpu_tdp_w: int, gpu_tdp_w: int, psu_wattage: int) -> CompatResult:
    """Validate PSU wattage against estimated system draw."""
    ...

def full_compatibility_check(
    cpu_socket: str,
    mb_chipset: str,
    ram_type: str,
    cpu_tdp_w: int,
    gpu_tdp_w: int,
    psu_wattage: int,
) -> CompatResult:
    """Run all compatibility checks and return aggregated results."""
    ...

def calculate_discount(quantity: int) -> float:
    """Return the bulk discount percentage for a quantity."""
    ...

def calculate_line_total(unit_price: float, quantity: int) -> float:
    """Calculate discounted line total."""
    ...

def check_stock_availability(current_stock: int, requested_qty: int) -> bool:
    """Return True if stock covers the requested quantity."""
    ...

def get_price_breakdown(unit_price: float, quantity: int) -> PriceBreakdown:
    """Return a detailed price breakdown with discount info."""
    ...

def calculate_cart_total(items: List[Tuple[float, int]]) -> float:
    """Sum line totals from list of (unit_price, quantity) tuples."""
    ...

def estimate_tax(subtotal: float, tax_rate: float = 0.0825) -> float:
    """Calculate sales tax."""
    ...
