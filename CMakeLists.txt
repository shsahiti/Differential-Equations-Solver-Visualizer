cmake_minimum_required(VERSION 3.15)
project(DiffEqSolver CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(main
    main.cpp
    parsing.cpp
    solving.cpp
)

# exprtk.hpp is a massive single-header (~46k lines).
# MSVC needs /bigobj to handle the generated object file.
if(MSVC)
    target_compile_options(main PRIVATE /bigobj)
endif()

# Headers live in the same directory as the sources.
target_include_directories(main PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
