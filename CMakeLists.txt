# ----------------------------------------------------------------------------
# Setup the project
# ----------------------------------------------------------------------------
cmake_minimum_required(VERSION 3.16 FATAL_ERROR)

if(DEFINED PROJECT_NAME_OVERRIDE)
    set(MY_PROJECT_NAME ${PROJECT_NAME_OVERRIDE})
else()
    get_filename_component(MY_PROJECT_NAME ${CMAKE_CURRENT_SOURCE_DIR} NAME)
endif()

project("${MY_PROJECT_NAME}" CXX)

set(CMAKE_CXX_STANDARD 17) 
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ----------------------------------------------------------------------------
# Find Geant4
# ----------------------------------------------------------------------------
option(WITH_GEANT4_UIVIS "Build example with Geant4 UI and Vis drivers" OFF)
if(WITH_GEANT4_UIVIS)
  find_package(Geant4 REQUIRED ui_all vis_all)
else()
  find_package(Geant4 REQUIRED)
endif()

# Setup Geant4 include directories and compile definitions
include(${Geant4_USE_FILE})

# ----------------------------------------------------------------------------
# Locate sources
# ----------------------------------------------------------------------------
include_directories(${PROJECT_SOURCE_DIR}/include
                    ${Geant4_INCLUDE_DIR})

file(GLOB SOURCES ${PROJECT_SOURCE_DIR}/src/*.cc)
file(GLOB HEADERS ${PROJECT_SOURCE_DIR}/include/*.hh)

# ----------------------------------------------------------------------------
# Add the executable
# ----------------------------------------------------------------------------
add_executable(${PROJECT_NAME} main.cc ${SOURCES} ${HEADERS})

target_include_directories(${PROJECT_NAME} PUBLIC include)
target_link_libraries(${PROJECT_NAME} ${Geant4_LIBRARIES})

# ----------------------------------------------------------------------------
# Copy Scripts (Macros)
# ----------------------------------------------------------------------------
file(GLOB MACRO_FILES ${PROJECT_SOURCE_DIR}/*.mac ${PROJECT_SOURCE_DIR}/macro/*.mac)

foreach(_script ${MACRO_FILES})
  # Ottiene solo il nome del file per la destinazione
  get_filename_component(_script_name ${_script} NAME)
  configure_file(
    ${_script}
    ${PROJECT_BINARY_DIR}/${_script_name}
    COPYONLY
    )
endforeach()

# ----------------------------------------------------------------------------
# Install
# ----------------------------------------------------------------------------
install(TARGETS ${PROJECT_NAME} DESTINATION bin)

message(STATUS "-----------------------------------------------------------")
message(STATUS " Configured Project: ${PROJECT_NAME}")
message(STATUS " Executable Name:    ${PROJECT_NAME}")
message(STATUS "-----------------------------------------------------------")
