# Origin App

真正给 Origin / OriginPro **Apps 画廊**用的插件在 `NatureFormat\` 文件夹。

1. 运行仓库根目录 `安装到Origin.bat`
2. 在 Origin 里打开已组好的图
3. 脚本窗口：`run -pyf "%@ANatureFormat\open_app.py";`
4. 或把该文件夹打成 `.opx` 拖进 Origin，之后点画廊图标

核心排版逻辑在上一级 Python 包 `natureformat`，不依赖 Origin 也能跑测试和预览界面。
