set I = %cd%

:findPw
if [not] exist %~fIpw (
    if exist %~fI.. (
        set I = %~fI..
        goto findPw
    )
)

if exist %~fIpw (
  python %~fIpw %*
) else (
    set global = 0
    for %%x in (%*) do (
        if %~x == "-g" (
            set global = 1
        )
        if %~x == "--global" (
            set global = 1
        )
    )
    if global == 1 (
        if defined UserProfile (
            set h = %UserProfile%
        ) else (
            set h = %HomeDrive%%HomePath%
        )
        if exist %~fh\.pyprojectx\pw (
          python %~fh\.pyprojectx\pw %*
        ) else (
             echo "ERROR: no pw script found in %~fh\.pyproject"
             exit 1
        )
    )
    echo "ERROR: no pw script found in any parent directory"
    exit 1
)
