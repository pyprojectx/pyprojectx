@echo off
if defined UserProfile (
    set "h=%UserProfile%"
) else (
    set "h=%HomeDrive%%HomePath%"
)
if exist "%h%\.pyprojectx\global\pw" (
  python "%h%\.pyprojectx\global\pw" %*
) else (
     echo ERROR: no pw script found in %h%\.pyprojectx\global
     exit 1
)
