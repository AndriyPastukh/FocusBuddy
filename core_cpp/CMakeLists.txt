cmake_minimum_required(VERSION 3.10)
project(FocusBuddyCore)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include_directories(include)
include_directories(lib)

file(GLOB_RECURSE SOURCES "src/*.cpp")

set(SQLITE_SOURCE "lib/sqlite3.c")

add_executable(core ${SOURCES} ${SQLITE_SOURCE})

if(UNIX)
    target_link_libraries(core pthread dl)
endif()