# RK3568 cross-compilation toolchain
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR aarch64)

# CHANGE THIS to your actual toolchain path
set(TOOLCHAIN_PREFIX /opt/toolchains/arm-gnu-toolchain/bin/aarch64-none-linux-gnu-)

set(CMAKE_C_COMPILER   ${TOOLCHAIN_PREFIX}gcc)
set(CMAKE_CXX_COMPILER ${TOOLCHAIN_PREFIX}g++)

set(CMAKE_C_FLAGS_INIT   "-mcpu=cortex-a55 -mtune=cortex-a55 -O2")
set(CMAKE_EXE_LINKER_FLAGS_INIT "-lpthread -lm")
