@echo off
REM 一键打包为单文件 exe（需已安装 Python 3.12 与 pyinstaller）
REM 用法：双击本文件，或在该目录执行 build.bat

setlocal
where py >nul 2>nul
if %errorlevel%==0 (
    set PY=py -3.12
) else (
    set PY=python
)

%PY% -m PyInstaller --onefile --windowed --clean --icon "folder_plus.ico" --name "批量建文件夹" --add-data "assets;assets" batch_file_creator.py

echo.
echo 打包完成，exe 位于 dist\批量建文件夹.exe
pause
endlocal
