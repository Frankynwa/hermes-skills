cmake_minimum_required(VERSION 3.15)
project(lvgl_simulator C)
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(LVGL_DIR ${CMAKE_SOURCE_DIR}/../lvgl)

add_compile_definitions(LV_CONF_INCLUDE_SIMPLE LV_LVGL_H_INCLUDE_SIMPLE SDL_MAIN_HANDLED)

find_library(SDL2_LIB SDL2 HINTS /opt/homebrew/lib /usr/local/lib)
find_path(SDL2_INC SDL2/SDL.h HINTS /opt/homebrew/include /usr/local/include)

if(NOT SDL2_LIB)
    message(FATAL_ERROR "SDL2 not found. Install: brew install sdl2")
endif()

file(GLOB_RECURSE LVGL_SOURCES ${LVGL_DIR}/src/*.c)
list(FILTER LVGL_SOURCES EXCLUDE REGEX ".*/drivers/(fbdev|drm|wayland|win32|x11|linux|dev/display|nuttx|gles|opengles).*")

# Add your app sources here
set(APP_SOURCES
    ${CMAKE_SOURCE_DIR}/src/main.c
    # ${CMAKE_SOURCE_DIR}/src/ui_xxx.c
)

add_executable(simulator ${LVGL_SOURCES} ${APP_SOURCES})
target_include_directories(simulator PRIVATE
    ${CMAKE_SOURCE_DIR}
    ${LVGL_DIR}
    ${LVGL_DIR}/src
    ${SDL2_INC}
)
target_link_libraries(simulator PRIVATE ${SDL2_LIB})
target_compile_definitions(simulator PRIVATE LV_USE_SDL=1)
