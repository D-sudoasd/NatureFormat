# Nature 一键排版

这是给 **Origin / OriginPro** 用的 **Apps 画廊插件**（App），不是 Origin 安装包本身，也不是改 Origin 内核的 DLL。

组好图 → 点 Apps 图标 → 选单栏或双栏和布局 → **一键套用**。只改页面尺寸、字体和轴体，**不改数据、圆形/方形标记、配色**。

<p align="center">
  <img src="origin_app/ui_preview.png" alt="Nature 一键排版界面" width="480">
</p>

## 在 Origin Pro 里用

1. 双击 `安装到Origin.bat`（复制到 `%LOCALAPPDATA%\OriginLab\Apps\NatureFormat`）
2. 打开 Origin Pro，点选一张**已经组好**的图（几个图层 = 几个面板）
3. 脚本窗口运行：

```labtalk
run -pyf "%@ANatureFormat\open_app.py";
```

或在 **代码生成器** 里把 `NatureFormat` 文件夹加成 App，Generate 成 `.opx`，拖进 Origin，之后就可以点右侧 **Apps 画廊** 里的图标。

窗口里：

- **单栏（Single Column）** 89 mm / **双栏（Double Column）** 183 mm
- **单图（一行一图） / 两图一行 / 三图一行 / 六宫格 / 九宫格**
- 轴体和轴上数字分开拖
- 顶部会显示当前图有几个图层；对不上会直接说，不会偷偷少排

Apps 画廊里图标只在 **Graph 窗口** 激活时可用。

## 先看界面（不经过画廊）

```powershell
cd E:\Vibe_coding\NatureFormat
py -3 -m natureformat ui
```

或双击 `启动Nature排版.bat`。Origin 开着时，同一套界面会套用到**当前图**。

## 会改 / 不改

| 会改 | 不改 |
| --- | --- |
| 单栏 89 mm / 双栏 183 mm，高 ≤ 247 mm | 数据点 x、y |
| 各面板位置和大小 | 圆形、方形等标记 |
| 标题、注释、轴上数字 → Arial 5–7 pt | 曲线颜色 |
| 多图 `a, b, c…`：8 pt 粗体正体小写 | 轴标题文字 |
| 轴体 / 刻度 0.25–1 pt | |

六宫格：单栏 3×2，双栏 2×3。

## 命令行

```powershell
py -3 -m pip install -e ".[test]"
py -3 -m natureformat apply --column 单栏 --layout 六宫格 examples\assembled_six_panel.json
py -3 -m pytest
```
