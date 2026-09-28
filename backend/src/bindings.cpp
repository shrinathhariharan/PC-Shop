/**
 * bindings.cpp
 * Pybind11 wrapper definitions exposing the C++ engine to Python.
 */
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "compatibility.cpp"
#include "inventory.cpp"

namespace py = pybind11;

PYBIND11_MODULE(pc_engine, m) 
{
    m.doc() = "PC Shop C++ Engine – compatibility checks & pricing";

    // ── CompatResult struct ───────────────────────────────────────────
    py::class_<pc_engine::CompatResult>(m, "CompatResult")
        .def_readonly("compatible", &pc_engine::CompatResult::compatible)
        .def_readonly("warnings",   &pc_engine::CompatResult::warnings)
        .def_readonly("errors",     &pc_engine::CompatResult::errors)
        .def("__repr__", [](const pc_engine::CompatResult& r) {
            return "<CompatResult compatible=" +
                   std::string(r.compatible ? "True" : "False") +
                   " errors=" + std::to_string(r.errors.size()) +
                   " warnings=" + std::to_string(r.warnings.size()) + ">";
        });

    // ── Compatibility functions ───────────────────────────────────────
    m.def("check_socket_compat", &pc_engine::check_socket_compat,
          py::arg("cpu_socket"), py::arg("mb_chipset"),
          "Check CPU socket ↔ motherboard chipset compatibility.");

    m.def("check_ram_compat", &pc_engine::check_ram_compat,
          py::arg("cpu_socket"), py::arg("ram_type"),
          "Check RAM type compatibility for a CPU socket.");

    m.def("check_power", &pc_engine::check_power,
          py::arg("cpu_tdp_w"), py::arg("gpu_tdp_w"), py::arg("psu_wattage"),
          "Validate PSU wattage against estimated system draw.");

    m.def("full_compatibility_check", &pc_engine::full_compatibility_check,
          py::arg("cpu_socket"), py::arg("mb_chipset"), py::arg("ram_type"),
          py::arg("cpu_tdp_w"), py::arg("gpu_tdp_w"), py::arg("psu_wattage"),
          "Run all compatibility checks and return aggregated results.");

    // ── PriceBreakdown struct ─────────────────────────────────────────
    py::class_<pc_engine::PriceBreakdown>(m, "PriceBreakdown")
        .def_readonly("unit_price",       &pc_engine::PriceBreakdown::unit_price)
        .def_readonly("quantity",          &pc_engine::PriceBreakdown::quantity)
        .def_readonly("discount_pct",      &pc_engine::PriceBreakdown::discount_pct)
        .def_readonly("subtotal",          &pc_engine::PriceBreakdown::subtotal)
        .def_readonly("discount_amount",   &pc_engine::PriceBreakdown::discount_amount)
        .def_readonly("total",             &pc_engine::PriceBreakdown::total)
        .def("__repr__", [](const pc_engine::PriceBreakdown& pb) {
            return "<PriceBreakdown qty=" + std::to_string(pb.quantity) +
                   " total=$" + std::to_string(pb.total) + ">";
        });

    // ── Inventory / pricing functions ─────────────────────────────────
    m.def("calculate_discount", &pc_engine::calculate_discount,
          py::arg("quantity"),
          "Return the bulk discount percentage for a quantity.");

    m.def("calculate_line_total", &pc_engine::calculate_line_total,
          py::arg("unit_price"), py::arg("quantity"),
          "Calculate discounted line total.");

    m.def("check_stock_availability", &pc_engine::check_stock_availability,
          py::arg("current_stock"), py::arg("requested_qty"),
          "Return True if stock covers the requested quantity.");

    m.def("get_price_breakdown", &pc_engine::get_price_breakdown,
          py::arg("unit_price"), py::arg("quantity"),
          "Return a detailed price breakdown with discount info.");

    m.def("calculate_cart_total", &pc_engine::calculate_cart_total,
          py::arg("items"),
          "Sum line totals from list of (unit_price, quantity) tuples.");

    m.def("estimate_tax", &pc_engine::estimate_tax,
          py::arg("subtotal"), py::arg("tax_rate") = 0.0825,
          "Calculate sales tax.");
}
