@echo off
echo Running Python Scripts...

REM Run GUI.pyw
python GUI.pyw
if %errorlevel% neq 0 (
    echo GUI.pyw failed
    pause
    exit /b %errorlevel%
)
echo GUI.pyw ran successfully

echo All scripts ran successfully.
exit