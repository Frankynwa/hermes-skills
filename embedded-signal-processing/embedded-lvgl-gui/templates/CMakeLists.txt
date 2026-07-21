cmake_minimum_required(VERSION 3.16)
project(lvgl_app C CXX)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

set(LVGL_DIR ${CMAKE_SOURCE_DIR}/../lvgl)
add_subdirectory(${LVGL_DIR} lvgl_build)

find_package(PkgConfig REQUIRED)
pkg_check_modules(DRM libdrm)
pkg_check_modules(LIBINPUT libinput)
pkg_check_modules(UDEV libudev)

option(USE_SDL2     "SDL2 PC sim"       OFF)
option(USE_DRM      "DRM/KMS display"   OFF)
option(USE_FBDEV    "Linux FBDEV"       OFF)
option(USE_LIBINPUT "libinput touch"    OFF)
option(USE_EVDEV    "evdev touch"       OFF)

if(USE_SDL2)
    pkg_check_modules(SDL2 sdl2)
endif()

# Source files
file(GLOB APP_SOURCES "src/*.c")
set(DRIVER_SOURCES "")
if(USE_SDL2)
    list(APPEND DRIVER_SOURCES drivers/sdl2_display.c)
endif()
if(USE_DRM OR (CMAKE_SYSTEM_NAME STREQUAL "Linux" AND NOT USE_SDL2 AND NOT USE_FBDEV))
    list(APPEND DRIVER_SOURCES drivers/drm_display.c)
endif()
if(USE_LIBINPUT)
    list(APPEND DRIVER_SOURCES drivers/libinput_drv.c)
endif()
if(USE_EVDEV)
    list(APPEND DRIVER_SOURCES drivers/evdev_drv.c)
endif()

add_executable(lvgl_app ${APP_SOURCES} ${DRIVER_SOURCES})

# Include paths
target_include_directories(lvgl_app PRIVATE
    ${CMAKE_SOURCE_DIR} ${CMAKE_SOURCE_DIR}/src
    ${LVGL_DIR}/.. ${LVGL_DIR} ${LVGL_DIR}/src
    ${DRM_INCLUDE_DIRS} ${LIBINPUT_INCLUDE_DIRS} ${UDEV_INCLUDE_DIRS}
)
if(USE_SDL2 AND SDL2_FOUND)
    target_include_directories(lvgl_app PRIVATE ${SDL2_INCLUDE_DIRS})
endif()

# Link
target_link_libraries(lvgl_app PRIVATE lvgl lvgl_thorvg m pthread)

if(USE_SDL2 AND SDL2_FOUND)
    target_link_directories(lvgl_app PRIVATE ${SDL2_LIBRARY_DIRS})
    target_link_libraries(lvgl_app PRIVATE ${SDL2_LIBRARIES})
    target_compile_definitions(lvgl_app PRIVATE USE_SDL2=1 LV_USE_SDL=1)
endif()
if(DRM_FOUND AND USE_DRM)
    target_link_libraries(lvgl_app PRIVATE ${DRM_LIBRARIES})
    target_compile_definitions(lvgl_app PRIVATE HAS_DRM=1 LV_USE_LINUX_DRM=1)
endif()
if(LIBINPUT_FOUND AND USE_LIBINPUT)
    target_link_libraries(lvgl_app PRIVATE ${LIBINPUT_LIBRARIES})
    target_compile_definitions(lvgl_app PRIVATE HAS_LIBINPUT=1 LV_USE_LIBINPUT=1)
endif()
if(UDEV_FOUND)
    target_link_libraries(lvgl_app PRIVATE ${UDEV_LIBRARIES})
endif()
if(USE_FBDEV)
    target_compile_definitions(lvgl_app PRIVATE LV_USE_LINUX_FBDEV=1)
endif()
if(USE_EVDEV)
    target_compile_definitions(lvgl_app PRIVATE LV_USE_EVDEV=1)
endif()

if(CMAKE_CROSSCOMPILING)
    set_target_properties(lvgl_app PROPERTIES
        COMPILE_FLAGS "-ffunction-sections -fdata-sections"
        LINK_FLAGS "-Wl,--gc-sections -Wl,--strip-all")
endif()
