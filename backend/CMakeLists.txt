cmake_minimum_required(VERSION 3.16)
project(pc_engine LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# ── Find pybind11 ────────────────────────────────────────────────────────
find_package(pybind11 REQUIRED)

# ── Build the shared library ─────────────────────────────────────────────
pybind11_add_module(pc_engine src/bindings.cpp)

# ── Copy the .so to the project root so Python can import it ─────────────
add_custom_command(TARGET pc_engine POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy
        $<TARGET_FILE:pc_engine>
        ${CMAKE_SOURCE_DIR}/../pc_engine$<TARGET_FILE_SUFFIX:pc_engine>
    COMMENT "Copying pc_engine shared library to project root"
)
