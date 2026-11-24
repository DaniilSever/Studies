# Additional clean files
cmake_minimum_required(VERSION 3.16)

if("${CONFIG}" STREQUAL "" OR "${CONFIG}" STREQUAL "")
  file(REMOVE_RECURSE
  "CMakeFiles/superapp_autogen.dir/AutogenUsed.txt"
  "CMakeFiles/superapp_autogen.dir/ParseCache.txt"
  "CMakeFiles/superapp_core_autogen.dir/AutogenUsed.txt"
  "CMakeFiles/superapp_core_autogen.dir/ParseCache.txt"
  "CMakeFiles/superapp_monitoring_autogen.dir/AutogenUsed.txt"
  "CMakeFiles/superapp_monitoring_autogen.dir/ParseCache.txt"
  "CMakeFiles/superapp_popup_autogen.dir/AutogenUsed.txt"
  "CMakeFiles/superapp_popup_autogen.dir/ParseCache.txt"
  "CMakeFiles/superapp_terminal_autogen.dir/AutogenUsed.txt"
  "CMakeFiles/superapp_terminal_autogen.dir/ParseCache.txt"
  "superapp_autogen"
  "superapp_core_autogen"
  "superapp_monitoring_autogen"
  "superapp_popup_autogen"
  "superapp_terminal_autogen"
  )
endif()
