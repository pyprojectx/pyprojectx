if defined UserProfile (
    set h = %UserProfile%
) else (
    set h = %HomeDrive%%HomePath%
)
if exist %~fh\.pyprojectx\global\pw (
  python %~fh\.pyprojectx\global\pw %*
) else (
     echo "ERROR: no pw script found in %~fh\.pyprojectx\global\pw"
     exit 1
)
