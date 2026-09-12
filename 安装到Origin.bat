@echo off
chcp 65001 >nul
set "SRC=%~dp0"
set "DEST=%LOCALAPPDATA%\OriginLab\Apps\NatureFormat"
echo 正在安装 Origin App 到:
echo   %DEST%
mkdir "%DEST%" 2>nul
xcopy /E /Y /I "%SRC%origin_app\NatureFormat\*" "%DEST%\" >nul
xcopy /E /Y /I "%SRC%natureformat" "%DEST%\natureformat\" >nul
if not exist "%DEST%\AppIcon.png" (
  py -3 "%SRC%scripts\make_app_icon.py"
  copy /Y "%SRC%origin_app\NatureFormat\AppIcon.png" "%DEST%\AppIcon.png" >nul
)
echo.
echo 文件已就位。
echo.
echo 请打开 Origin Pro：
echo   1. 先打开并点选一张已经组好的图
echo   2. 把下面这行贴进 窗口 → 脚本窗口，回车：
echo      run -pyf "%%@ANatureFormat\open_app.py";
echo.
echo 若要出现在右侧 Apps 画廊：Origin 里 工具 → 包管理器，
echo 添加文件夹 "%DEST%" 后 Generate / 保存为 OPX，再把 OPX 拖进 Origin。
echo.
echo 也可以先双击 启动Nature排版.bat 在 Origin 外面预览界面。
pause
