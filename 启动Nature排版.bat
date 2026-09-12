@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "PYTHONPATH=%~dp0;%PYTHONPATH%"
echo 预览界面。要在 Origin Pro 画廊里用，请先运行 安装到Origin.bat
py -3 -m natureformat ui
if errorlevel 1 python -m natureformat ui
if errorlevel 1 (
  echo.
  echo 无法启动。请确认已安装 Python 3.10+（py -3）。
  pause
)
