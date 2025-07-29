@echo off
setlocal
title Neko Image Viewer
color 0F

:: === Get script base path ===
set "SCRIPT_DIR=%~dp0"
set "PY_SCRIPT=%SCRIPT_DIR%neko_viewer.py"

:: === Drag & Drop Support ===
if not "%~1"=="" (
    python "%PY_SCRIPT%" "%~1"
    goto end
)

echo Welcome to Neko!
echo Navigate with 'cd', use 'dir' to list files.
echo Commands:
echo - neko [image] open
echo - neko list
echo - neko generate [prompt]
echo - exit

:loop
set /p input=neko ^> 
if /i "%input%"=="exit" exit

:: Handle cd
if /i "%input:~0,3%"=="cd " (
    cd %input:~3%
    goto loop
)

:: Handle dir
if /i "%input%"=="dir" (
    dir
    goto loop
)

:: List image files
if /i "%input%"=="neko list" (
    dir /b *.jpg *.jpeg *.png *.bmp *.gif 2>nul
    goto loop
)

:: Handle neko generate [prompt...]
echo %input% | findstr /r /c:"^neko generate " >nul
if not errorlevel 1 (
    for /f "tokens=1,2,*" %%a in ("%input%") do (
        set "prompt=%%c"
        call :generate_image
    )
    goto loop
)

:: Handle neko [image] open
for /f "tokens=1,2,3" %%a in ("%input%") do (
    if /i "%%a"=="neko" if /i "%%c"=="open" (
        python "%PY_SCRIPT%" "%%b"
    )
)
goto loop

:generate_image
echo 🎨 Generating image for prompt: %prompt%
python "%SCRIPT_DIR%neko_generate.py" "%prompt%"
goto :eof

:end
pause
