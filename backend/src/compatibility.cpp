/**
 * compatibility.cpp
 * CPU-socket and motherboard-RAM compatibility checks, plus PSU wattage
 * validation for custom PC builds.
 */
#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>


namespace pc_engine 
{

// ── Socket compatibility matrix ──────────────────────────────────────────
//   Maps CPU socket → set of compatible motherboard chipsets.
static const std::unordered_map<std::string, std::unordered_set<std::string>>
    SOCKET_CHIPSETS = {
        {"AM4",     {"B550", "B550M", "X570"}},
        {"AM5",     {"B650", "B650I", "B650M", "X670", "X670E"}},
        {"LGA1700", {"B760", "Z790", "H770"}},
};

// ── RAM type per socket generation ───────────────────────────────────────
static const std::unordered_map<std::string, std::string>
    SOCKET_RAM_TYPE = {
        {"AM4",     "DDR4"},
        {"AM5",     "DDR5"},
        {"LGA1700", "DDR5"},  // most modern LGA1700 boards are DDR5
};


struct CompatResult {
    bool compatible;
    std::vector<std::string> warnings;
    std::vector<std::string> errors;
};

/**
 * check_socket_compat
 * Verifies that a CPU socket matches the motherboard chipset.
 */
CompatResult check_socket_compat(const std::string& cpu_socket,
                                  const std::string& mb_chipset) {
    CompatResult res{true, {}, {}};

    auto it = SOCKET_CHIPSETS.find(cpu_socket);
    if (it == SOCKET_CHIPSETS.end()) {
        res.errors.push_back("Unknown CPU socket: " + cpu_socket);
        res.compatible = false;
        return res;
    }

    // Try a prefix match so "B650I" matches "B650I" etc.
    bool found = false;
    for (const auto& chipset : it->second) {
        if (mb_chipset.find(chipset) == 0 || chipset.find(mb_chipset) == 0) {
            found = true;
            break;
        }
    }
    if (!found) {
        res.errors.push_back("CPU socket " + cpu_socket +
                             " is NOT compatible with chipset " + mb_chipset);
        res.compatible = false;
    }
    return res;
}

/**
 * check_ram_compat
 * Ensures the RAM type matches what the motherboard supports.
 */
CompatResult check_ram_compat(const std::string& cpu_socket,
                               const std::string& ram_type) {
    CompatResult res{true, {}, {}};

    auto it = SOCKET_RAM_TYPE.find(cpu_socket);
    if (it == SOCKET_RAM_TYPE.end()) {
        res.warnings.push_back("Cannot verify RAM for unknown socket: " +
                                cpu_socket);
        return res;
    }
    if (it->second != ram_type) {
        res.errors.push_back("Socket " + cpu_socket + " requires " +
                             it->second + " RAM, but " + ram_type +
                             " was selected.");
        res.compatible = false;
    }
    return res;
}

/**
 * check_power
 * Validates that the PSU wattage provides at least a 20% headroom above
 * the total estimated power draw (CPU TDP + GPU TDP + ~75W base system).
 */
CompatResult check_power(int cpu_tdp_w, int gpu_tdp_w, int psu_wattage) {
    CompatResult res{true, {}, {}};

    const int BASE_SYSTEM_DRAW = 75;  // fans, drives, RAM, etc.
    int total_draw = cpu_tdp_w + gpu_tdp_w + BASE_SYSTEM_DRAW;
    double headroom_ratio = static_cast<double>(psu_wattage) / total_draw;

    if (psu_wattage < total_draw) {
        res.errors.push_back(
            "PSU (" + std::to_string(psu_wattage) +
            "W) is INSUFFICIENT for estimated draw (" +
            std::to_string(total_draw) + "W).");
        res.compatible = false;
    } else if (headroom_ratio < 1.20) {
        res.warnings.push_back(
            "PSU provides only " +
            std::to_string(static_cast<int>((headroom_ratio - 1.0) * 100)) +
            "% headroom (recommended ≥ 20%). Estimated draw: " +
            std::to_string(total_draw) + "W, PSU: " +
            std::to_string(psu_wattage) + "W.");
    }
    return res;
}

/**
 * full_compatibility_check
 * Runs all compatibility checks for a custom build and aggregates results.
 */
CompatResult full_compatibility_check(
    const std::string& cpu_socket,
    const std::string& mb_chipset,
    const std::string& ram_type,
    int cpu_tdp_w, int gpu_tdp_w, int psu_wattage)
{
    CompatResult final_result{true, {}, {}};

    auto socket_res = check_socket_compat(cpu_socket, mb_chipset);
    auto ram_res    = check_ram_compat(cpu_socket, ram_type);
    auto pwr_res    = check_power(cpu_tdp_w, gpu_tdp_w, psu_wattage);

    // Merge results
    for (auto* partial : {&socket_res, &ram_res, &pwr_res}) {
        if (!partial->compatible) final_result.compatible = false;
        final_result.warnings.insert(final_result.warnings.end(),
                                     partial->warnings.begin(),
                                     partial->warnings.end());
        final_result.errors.insert(final_result.errors.end(),
                                   partial->errors.begin(),
                                   partial->errors.end());
    }
    return final_result;
}

}  // namespace pc_engine
