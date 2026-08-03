cmake_minimum_required(VERSION 3.15)
project(DiffEqSolver CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(main
    main.cpp
    parsing.cpp
    solving.cpp
    visualizer.cpp
)

# exprtk.hpp is a massive single-header (~46k lines) — needs big-obj on all compilers.
if(MSVC)
    target_compile_options(main PRIVATE /bigobj)
elseif(MINGW OR CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    target_compile_options(main PRIVATE -Wa,-mbig-obj -O2)
endif()

target_include_directories(main PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# Visualizer window (mglGLUT) needs MathGL's core + glut backend, and GLUT/freeglut itself.
set(_mgl_hints /mingw64 /ucrt64 C:/msys64/ucrt64 C:/msys64/mingw64)
find_library(MGL_LIBRARY NAMES mgl2 mgl HINTS ${_mgl_hints} PATH_SUFFIXES lib)
find_library(MGL_GLUT_LIBRARY NAMES mgl2-glut HINTS ${_mgl_hints} PATH_SUFFIXES lib)
find_library(GLUT_LIBRARY NAMES freeglut glut HINTS ${_mgl_hints} PATH_SUFFIXES lib)
find_path(MGL_INCLUDE_DIR mgl2/glut.h HINTS ${_mgl_hints} PATH_SUFFIXES include)
if(NOT MGL_LIBRARY OR NOT MGL_GLUT_LIBRARY OR NOT GLUT_LIBRARY OR NOT MGL_INCLUDE_DIR)
    message(FATAL_ERROR "MathGL/GLUT not found. On MSYS2 UCRT64: pacman -S mingw-w64-ucrt-x86_64-mathgl")
endif()
target_include_directories(main PRIVATE ${MGL_INCLUDE_DIR})
target_link_libraries(main PRIVATE ${MGL_GLUT_LIBRARY} ${MGL_LIBRARY} ${GLUT_LIBRARY})
