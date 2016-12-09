cmake_minimum_required(VERSION 3.1)
project(beetle-vb)

list(APPEND CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR})

include(ExternalProject)

string(TOUPPER ${PROJECT_NAME} PROJECT_NAME_UC)

set(LIBRETRO_BINARY_DIR .)
set(LIBRETRO_SONAME mednafen_vb_libretro${CMAKE_SHARED_LIBRARY_SUFFIX})

if(CMAKE_BUILD_TYPE MATCHES Debug)
  set(LIBRETRO_DEBUG DEBUG=1)
endif()

if(CORE_SYSTEM_NAME STREQUAL windows)
  find_package(MinGW REQUIRED)
  set(BUILD_COMMAND ${MINGW_MAKE} -j$ENV{NUMBER_OF_PROCESSORS} -C . -f Makefile platform=win  ${LIBRETRO_DEBUG})
elseif(CORE_SYSTEM_NAME STREQUAL linux)
  set(BUILD_COMMAND $(MAKE) -C . -f Makefile  ${LIBRETRO_DEBUG})
elseif(CORE_SYSTEM_NAME STREQUAL osx)
  set(BUILD_COMMAND $(MAKE) -C . -f Makefile  platform=osx ${LIBRETRO_DEBUG})
elseif(CORE_SYSTEM_NAME STREQUAL ios)
  set(LIBRETRO_SONAME mednafen_vb_libretro_ios${CMAKE_SHARED_LIBRARY_SUFFIX})
  set(BUILD_COMMAND $(MAKE) -C . -f Makefile  platform=ios ${LIBRETRO_DEBUG})
elseif(CORE_SYSTEM_NAME STREQUAL android)
  if(CPU STREQUAL armeabi-v7a)
    set(PLATFORM android-armv7a-cortexa9-neon-softfloat)
  elseif(CPU STREQUAL i686)
    set(PLATFORM android-x86)
  else()
    message(FATAL_ERROR "${PROJECT_NAME} needs Android ${CPU} build command in CMakeLists.txt!")
  endif()
  set(BUILD_COMMAND CC=${CMAKE_C_COMPILER} CXX=${CMAKE_CXX_COMPILER}
                    $(MAKE) -C . -f Makefile  platform=${PLATFORM} ${LIBRETRO_DEBUG})
elseif(CORE_SYSTEM_NAME STREQUAL rbpi)
  if(CPU STREQUAL arm1176jzf-s)
    set(PLATFORM rpi1-armv6j-hardfloat)
  elseif(CPU MATCHES "cortex-a7")
    set(PLATFORM rpi2-armv7a-cortexa7-neon-hardfloat)
  elseif(CPU MATCHES "cortex-a53")
    set(PLATFORM rpi3-armv8a-cortexa53-hardfloat)
  else()
    message(FATAL_ERROR "${PROJECT_NAME} needs Rbpi ${CPU} build command in CMakeLists.txt!")
  endif()
  set(BUILD_COMMAND CC=${CMAKE_C_COMPILER} CXX=${CMAKE_CXX_COMPILER} $(MAKE) -C . -f Makefile  platform=${PLATFORM} ${LIBRETRO_DEBUG})
elseif(CORE_SYSTEM_NAME STREQUAL freebsd)
  set(BUILD_COMMAND $(MAKE) -C . -f Makefile platform=bsd  ${LIBRETRO_DEBUG})
else()
  message(FATAL_ERROR "${PROJECT_NAME} - Unknown system: ${CORE_SYSTEM_NAME}")
endif()

externalproject_add(${PROJECT_NAME}
                    SOURCE_DIR ${PROJECT_SOURCE_DIR}
                    PREFIX ${PROJECT_NAME}
                    CONFIGURE_COMMAND ""
                    INSTALL_COMMAND ""
                    BUILD_COMMAND ${BUILD_COMMAND}
                    BUILD_IN_SOURCE 1)

# install the generated shared library
install(FILES ${PROJECT_SOURCE_DIR}/${LIBRETRO_BINARY_DIR}/${LIBRETRO_SONAME}
        DESTINATION ${CMAKE_INSTALL_PREFIX}/lib)

# write the config.cmake script
file(WRITE ${CMAKE_INSTALL_PREFIX}/libretro-${PROJECT_NAME}-config.cmake "set(${PROJECT_NAME_UC}_LIB ${CMAKE_INSTALL_PREFIX}/lib/${LIBRETRO_SONAME})")