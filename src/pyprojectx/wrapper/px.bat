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
 echo "ERROR: no pw script found in any parent directory"
)
