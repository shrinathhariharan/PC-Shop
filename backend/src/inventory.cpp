/**
 * inventory.cpp
 * Dynamic stock checking and pricing engine with bulk discount calculations.
 */

#include <vector>
#include <cmath>

namespace pc_engine 
{

// ── Discount tiers ───────────────────────────────────────────────────────
struct DiscountTier {
    int    min_quantity;
    double discount_pct;  // e.g. 0.05 = 5%
};

static const std::vector<DiscountTier> DISCOUNT_TIERS = {
    {5,  0.03},   // 3% off for 5+ of same item
    {10, 0.05},   // 5% off for 10+
    {25, 0.08},   // 8% off for 25+
    {50, 0.12},   // 12% off for 50+
};

/**
 * calculate_discount
 * Returns the discount percentage (0.0–1.0) for a given quantity.
 */
double calculate_discount(int quantity) {
    double discount = 0.0;
    for (const auto& tier : DISCOUNT_TIERS) {
        if (quantity >= tier.min_quantity) {
            discount = tier.discount_pct;
        }
    }
    return discount;
}

/**
 * calculate_line_total
 * Returns the total price for a given unit price & quantity, after discount.
 */
double calculate_line_total(double unit_price, int quantity) {
    double discount = calculate_discount(quantity);
    double subtotal = unit_price * quantity;
    return std::round((subtotal * (1.0 - discount)) * 100.0) / 100.0;
}

/**
 * check_stock_availability
 * Returns true if requested quantity is available.
 */
bool check_stock_availability(int current_stock, int requested_qty) {
    return current_stock >= requested_qty;
}

struct PriceBreakdown {
    double unit_price;
    int    quantity;
    double discount_pct;
    double subtotal;
    double discount_amount;
    double total;
};

/**
 * get_price_breakdown
 * Returns a detailed price breakdown for a line item.
 */
PriceBreakdown get_price_breakdown(double unit_price, int quantity) {
    PriceBreakdown pb;
    pb.unit_price       = unit_price;
    pb.quantity          = quantity;
    pb.discount_pct      = calculate_discount(quantity);
    pb.subtotal          = unit_price * quantity;
    pb.discount_amount   = std::round(pb.subtotal * pb.discount_pct * 100.0) / 100.0;
    pb.total             = std::round((pb.subtotal - pb.discount_amount) * 100.0) / 100.0;
    return pb;
}

/**
 * calculate_cart_total
 * Sums line totals from a list of (unit_price, quantity) pairs.
 */
double calculate_cart_total(const std::vector<std::pair<double, int>>& items) {
    double total = 0.0;
    for (const auto& [price, qty] : items) {
        total += calculate_line_total(price, qty);
    }
    return std::round(total * 100.0) / 100.0;
}

/**
 * estimate_tax
 * Computes sales tax for a given subtotal and rate.
 */
double estimate_tax(double subtotal, double tax_rate = 0.0825) {
    return std::round(subtotal * tax_rate * 100.0) / 100.0;
}

}  // namespace pc_engine
