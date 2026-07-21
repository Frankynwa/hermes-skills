cmake_minimum_required(VERSION 3.12)
project(lvgl_sdl2_simulator LANGUAGES C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

# LVGL configuration
set(LV_BUILD_CONF_PATH "${CMAKE_CURRENT_SOURCE_DIR}/lv_conf.h" CACHE STRING "")
set(CONFIG_LV_BUILD_DEMOS ON CACHE BOOL "" FORCE)
set(CONFIG_LV_BUILD_EXAMPLES ON CACHE BOOL "" FORCE)

# Find SDL2
find_package(PkgConfig REQUIRED)
pkg_check_modules(SDL2 REQUIRED sdl2)

# Add LVGL as subdirectory
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/../lvgl lvgl_build)

# Simulator executable
add_executable(lvgl_simulator
    src/main.c
    src/sdl2_display.c
)

# Include paths — parent dir so #include "lvgl/lvgl.h" works
target_include_directories(lvgl_simulator PRIVATE
    ${SDL2_INCLUDE_DIRS}
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/..
    ${CMAKE_CURRENT_SOURCE_DIR}/../lvgl/src
)

target_link_libraries(lvgl_simulator PRIVATE
    lvgl
    lvgl::lvgl
    ${SDL2_LIBRARIES}
)

target_link_directories(lvgl_simulator PRIVATE ${SDL2_LIBRARY_DIRS})
