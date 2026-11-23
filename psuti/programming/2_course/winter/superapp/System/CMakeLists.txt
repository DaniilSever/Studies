cmake_minimum_required(VERSION 3.16)
project(Superapp LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
find_package(QT NAMES Qt6 Qt5 REQUIRED COMPONENTS Widgets Network)
find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Widgets Network)
add_library(superapp_core STATIC
    src/settings.cpp
    src/modules/filemanager.cpp
    src/modules/terminal.cpp
    src/modules/monitoring.cpp
    src/popup.cpp)
target_link_libraries(superapp_core PUBLIC Qt${QT_VERSION_MAJOR}::Widgets Qt${QT_VERSION_MAJOR}::Network)
target_include_directories(superapp_core PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_compile_definitions(superapp_core PRIVATE SUPERAPP_SOURCE_ROOT="${CMAKE_CURRENT_SOURCE_DIR}")
add_executable(superapp src/app.cpp)
target_link_libraries(superapp PRIVATE superapp_core)
add_executable(superapp_terminal src/terminal_main.cpp)
target_link_libraries(superapp_terminal PRIVATE superapp_core)
add_executable(superapp_monitoring src/monitoring_main.cpp)
target_link_libraries(superapp_monitoring PRIVATE superapp_core)
add_executable(superapp_popup src/popup_main.cpp)
target_link_libraries(superapp_popup PRIVATE superapp_core)
# Assets are copied next to executables, without changing original PNGs.
file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/src/modules/assets DESTINATION ${CMAKE_CURRENT_BINARY_DIR})
