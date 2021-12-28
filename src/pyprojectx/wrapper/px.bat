@echo off
setlocal

set "curDir=%cd%"

:findPw
if not exist "%curDir%\pw" (
    for %%I in ("%curDir%\..") do (
        set "curDir=%%~fI"
        set "drive=%%~dI"
    )
    if not "%curDir%" == "%drive%\" (
        goto findPw
    )
)

if exist "%curDir%\pw" (
  python "%curDir%\pw" %*
) else (
    echo ERROR: no pw script found in any parent directory
    exit /b 1
)
