if exist %~dp0\pw (
    echo ==== file exists ====
) else (
    echo ==== file doesn't exist ====
)
python %~dp0\pw %*
