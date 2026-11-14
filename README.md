# 批量建文件夹工具 · Batch Folder Creator

[![License](https://img.shields.io/github/license/ERunnn/batch-folder-creator?style=flat-square)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11-blue?style=flat-square)](#项目简介)
[![Built with](https://img.shields.io/badge/built%20with-Python%20%2B%20tkinter-2ea44f?style=flat-square)](#技术栈)

> 序号规则定一次，名字逐行填；一键铺好项目骨架，右键新建文件夹的苦差事交给它。

一个 Windows 单文件 GUI 小工具：在指定目录里，按「**序号前缀 + 你逐行填写的名称**」批量创建空文件夹，用来给项目搭目录骨架。

双击即用，不需要安装 Python，也不需要任何运行库。

下面几张都是程序**真实启动后抓取**的画面。

**完整界面**（加载模板后的状态）

![完整 GUI 截图](docs/screenshot-templates.png)

**模板操作区**（存 / 载 / 删命名模板）

![模板操作区局部截图](docs/screenshot-template-detail.png)

**生成结果**（6 个带序号的文件夹）

![生成结果示例](docs/example-folders.png)

**English** — *Batch Folder Creator* is a Windows single-file GUI that creates empty folders in bulk by a numeric prefix plus a list of names you fill line by line. Python + tkinter, no install, no network.
**你可能在找**：批量建文件夹 · 批量新建目录 · 项目目录骨架 · 序号命名文件夹 · batch create folders

## 目录

<ul>
<li><a href="#项目简介">项目简介</a></li>
<li>
<details open>
<summary><a href="#功能介绍">功能介绍</a></summary>
<ul>
<li><a href="#序号格式">序号格式</a></li>
<li><a href="#参数模板">参数模板</a></li>
<li><a href="#一个小彩蛋">一个小彩蛋</a></li>
</ul>
</details>
</li>
<li><a href="#获取与运行">获取与运行</a></li>
<li><a href="#常见问题">常见问题</a></li>
<li><a href="#贡献与致谢">贡献与致谢</a></li>
<li>
<details open>
<summary><a href="#附录">附录</a></summary>
<ul>
<li><a href="#文件构成">文件构成</a></li>
<li><a href="#实测过与没实测过">实测过 / 没实测过</a></li>
<li><a href="#已知局限">已知局限</a></li>
<li><a href="#同类工具">同类工具</a></li>
<li><a href="#技术栈">技术栈</a></li>
</ul>
</details>
</li>
</ul>

---

## 项目简介

| | |
|---|---|
| **做什么** | 在指定目录里，按「序号前缀 + 逐行填写的名称」批量创建空文件夹，给项目铺一套有顺序的目录骨架（`01_AEP`、`02_MP3`……） |
| **平台** | Windows 10/11 桌面程序，有单文件 exe，也有 Python 源码 |
| **不做什么** | 不重命名已有文件夹、不做多级嵌套、不导入 Excel / CSV；只建空目录，不往里放文件 |

## 功能介绍

| | |
|---|---|
| **序号规则** | 11 个预设前缀（`1_`、`01_`、`第1章 `、`(1) ` …）+ 一个自定义模板串，决定序号长什么样 |
| **逐行清单** | 数量决定行数，每行左侧序号前缀、右侧填名称；留空只生成序号；调数量 / 起始 / 格式时已填名称按行保留 |
| **实时预览** | 右侧显示首个文件夹的实际名字，如 `01_项目名`；模板里没写占位符会提示「序号不会变化」 |
| **参数模板** | 整套参数存成命名模板，下次下拉一键回填（见下节） |
| **覆盖开关** | 关闭时遇到同名文件夹跳过并记日志；打开时确保存在 |
| **运行日志** | 逐条显示已创建 / 已跳过 / 失败原因，结束可一键打开目标文件夹 |

Windows 文件夹名非法字符（`" < > : / \ | ? *`）会被自动移除。

### 序号格式

预设只决定**序号前缀长什么样**，与名称无关：

| 预设 | 示例（起始=1） | 预设 | 示例 |
|---|---|---|---|
| `1_` | `1_项目名` | `01_` | `01_项目名` |
| `1-` | `1-项目名` | `01-` | `01-项目名` |
| `1.` | `1.项目名` | `001_` | `001_项目名` |
| `1、` | `1、项目名` | `一、` | `一、项目名` |
| `第1章 ` | `第1章 项目名` | `(1) ` | `(1) 项目名` |

选「自定义…」后，右侧输入框可写任意模板串：

- `{n}` 阿拉伯数字，可带格式 `{n:02d}` 补零、`{n:03d}` 三位补零
- `{cn}` 中文数字（一、二、三……）
- 其余文字原样保留，例如 `第{n}节 ` → `第1节 项目名`、`{n:03d}. ` → `001. 项目名`

模板里若没写 `{n}` 或 `{cn}`，实时示例会提示「序号不会变化」。

### 参数模板

模板解决的是「同一套项目骨架要反复铺」：把**整套参数**存成一个名字，下次下拉选中即全部回填，不用重新填一遍。

- **保存模板**：点「保存模板」，输入名称，把当前的目标目录、数量、起始序号、序号格式、自定义串、覆盖开关、以及逐行名称清单一起存下
- **加载模板**：在下拉框选中即回填所有参数并重建逐行列表
- **删除模板**：选中后二次确认删除
- **存哪**：exe 同目录的 `templates.json`。它是纯 JSON、跟着 exe 走，把 exe 拷到 U 盘或另一台电脑，模板也跟着过去
- **留空给你自己做**：软件内**没有内置预设模板**，下拉框初始只有一个「选择模板」占位项

一份模板的实际结构（对应 `_collect_config()` 的字段）：

```json
{
  "素材归档": {
    "dir": "D:\\项目\\2026_素材",
    "count": 6,
    "start": 1,
    "format": "01_",
    "custom_fmt": "{n:02d}-",
    "overwrite": false,
    "names": ["AEP", "MP3", "MP4", "DNG", "OTH", "FIN"]
  }
}
```

模板目前没有导入 / 导出界面，也没有版本迁移；老版本模板里多出来的字段会被忽略。

### 一个小彩蛋

按下 `Ctrl + Shift + F`，会弹出一个小窗口，放着微信 / 支付宝收款码（文案「请作者喝杯咖啡～」）——这是给用得顺手的人留的隐藏入口，不在界面上摆出来。收款码在 `assets/qr_wechat.png`、`assets/qr_alipay.png`；重新打包需保留 `--add-data "assets;assets"`，否则弹窗显示「（收款码未随仓库分发）」。

## 获取与运行

- **直接用（推荐）**：从仓库下载 `dist/批量建文件夹.exe`，双击运行（约 10 MB，免安装）。把 exe 放在哪个目录，默认就在哪个目录建文件夹；`templates.json` 也跟着 exe 走
- **跑源码**：`py -3.12 batch_file_creator.py`（需 Python 3.12 + tkinter）

<details>
<summary>重新打包成单文件 exe</summary>

```bat
build.bat
```

等价于：

```bat
py -3.12 -m PyInstaller --onefile --windowed --clean --icon folder_plus.ico --add-data "assets;assets" --name 批量建文件夹 batch_file_creator.py
```

注意：WorkBuddy 自带的精简版 Python 3.13 没有 tkinter 和 PyInstaller，请用系统 `py -3.12`。若打包时提示无法覆盖旧的 `dist\批量建文件夹.exe`，先手动删掉或改名旧 exe 再跑。

</details>

## 常见问题

<details>
<summary>「投喂作者」在哪？怎么触发？</summary>

它现在是个隐藏彩蛋，不在界面上：在程序窗口里按 `Ctrl + Shift + F` 即可弹出微信 / 支付宝收款码。收款码已打进 exe（打包时带 `--add-data "assets;assets"`）；若某环境缺图，弹窗会显示「（收款码未随仓库分发）」。

</details>

<details>
<summary>勾上「覆盖」会清空已有文件夹里的内容吗？</summary>

不会。覆盖开关执行的是 `os.makedirs(exist_ok=True)`，语义是「确保文件夹存在」，不会删除或清空已有内容；同名文件夹会跳过。

</details>

<details>
<summary>中文数字（一、二、三）为什么到 99 之后变回阿拉伯数字？</summary>

`cn_num` 只覆盖 1–99；序号 ≥100 会回退成阿拉伯数字（`100_` 而非 `一百_`）。这是当前实现的上限，不是 bug。

</details>

<details>
<summary>模板换台电脑还在吗？放在只读目录会怎样？</summary>

模板写在 exe 同目录的 `templates.json`，跟着 exe 走，拷到 U 盘或另一台电脑都还在。但若 exe 放在只读目录（如 `Program Files`），保存模板会失败并弹错。

</details>

<details>
<summary>两个文件夹名字填成一样会怎样？</summary>

名称清洗是直接删除非法字符、**不检测清单内重名**；填了两个相同名字时，后者会被跳过（日志里记为已跳过）。

</details>

## 贡献与致谢

**反馈与贡献**

- 遇到问题请到 [Issues](https://github.com/ERunnn/batch-folder-creator/issues) 提交，附上出错截图、复现步骤与 Windows 版本。
- 欢迎 Pull Request；说明改动影响的行为即可，本仓库没有独立的自检测试套件（仅 `docs/make_screenshot.py` 可复跑）。
- 「投喂作者」入口与收款码做法参考自同作者的 [subtitle-puzzle](https://github.com/ERun-3/subtitle-puzzle) 项目。

**致谢**

- 界面基于 Python 标准库 [tkinter](https://docs.python.org/3/library/tkinter.html)。
- 应用图标由 [Pillow](https://python-pillow.org/) 绘制并手工拼装多尺寸 ICO（`make_icon.py`）。
- 本仓库代码采用 [MIT License](LICENSE)。

## 附录

- **文件构成**：`batch_file_creator.py`（主程序，仅标准库 tkinter）、`dist/批量建文件夹.exe`（约 10 MB 成品）、`make_icon.py`（用 Pillow 生成 ICO）、`folder_plus.ico`（9 个尺寸 16–256px 图标）、`assets/qr_wechat.png`、`assets/qr_alipay.png`（投喂收款码）、`build.bat`（打包）、`docs/`（截图与可复跑截图脚本 `make_screenshot.py`）、`templates.json`（运行时生成的参数模板，随 exe 走）
- **实测过 / 没实测过**：纯函数断言（中文数字到 99、各预设、自定义串、非法字符清洗）、临时目录真实 mkdir、ICO 二进制 9 帧解析、`py_compile`、`docs/make_screenshot.py` 真实启动 GUI 抓图并含回填 / 预览断言均通过；人工交互手感（鼠标点击、滚轮、DPI 缩放）、exe 图标在任务栏 / 桌面显示、同类工具对比（仅网页检索）未经逐一实测
- **已知局限**：`cn_num` 仅 1–99，≥100 回退阿拉伯数字；名称清洗不查清单内重名，同名时后者被跳过；覆盖=确保存在而不清空；仅 Windows（`os.startfile` / `iconbitmap` / Windows 非法字符集）；`templates.json` 在只读目录保存会失败并弹错；模板无导入导出、无版本迁移
- **同类工具**：[FolderMaker](https://github.com/fayaznaim/FolderMaker)（C# 单 exe，固定前缀加数字，无格式模板串 / 中文数字 / 参数模板）、[bulk-folder-creator](https://github.com/Harikumarthapa/bulk-folder-creator)（浏览器 Web 工具，导出 ZIP/.bat，不直接建目录）、[汇帮批量建文件夹](https://www.huibang168.com/createfile/detail/tWz9XuukLTcl) 等国产闭源工具、[Bulk Rename Utility](https://www.bulkrenameutility.co.uk/)（主业重命名）、PowerShell / Excel + .bat（系统自带，无界面）；2026-11-14 检索，**未逐一安装实测**
- **许可**：代码 [MIT](LICENSE) · Copyright (c) 2026 Huang Yirun
- **更新记录**：本仓库暂无独立 `CHANGELOG.md`，版本与改动以 git 提交历史为准

### 技术栈

仅 Python 标准库 tkinter；PyInstaller 单文件、无控制台窗口；成品 `dist/批量建文件夹.exe` 约 10 MB；构建脚本 `build.bat`；图标由 `make_icon.py` 生成 `folder_plus.ico`。

<!-- AI-BRIEF:START
定位/受众：Windows 单文件 GUI，按「序号前缀 + 逐行填写名」批量建空文件夹搭项目骨架；面向个人项目目录规范化，无 CLI/库/API，入口 batch_file_creator.py 的 main() 直接起 Tk。
差异1（可核实）：序号前缀是可编辑模板串，FORMAT_PRESETS 支持 {n}、{n:02d}、{cn} 中文数字与自定义串；检索到的同类 https://github.com/fayaznaim/FolderMaker 与 https://github.com/Harikumarthapa/bulk-folder-creator 多为固定前缀加数字或补零，此差异未经逐一安装实测。
差异2（可核实）：名称清单是逐行 Entry 列表（rebuild_rows），非多行文本框粘贴；整套参数可存/载/删为命名模板（_collect_config / _apply_config，文件 templates.json，无内置预设）。
技术：仅 Python 标准库 tkinter；PyInstaller 单文件且无控制台窗口；成品 dist/批量建文件夹.exe 约 10 MB；构建 build.bat；图标 make_icon.py 生成 folder_plus.ico。
功能补充（可核实）：投喂收款码不再做常驻按钮，改为隐藏彩蛋——Ctrl+Shift+F 触发 _open_feed_dialog，弹窗读取 assets/qr_wechat.png 与 assets/qr_alipay.png；打包需 --add-data "assets;assets" 才能随 exe 走，否则显示「收款码未随仓库分发」。
已实测：纯函数断言、临时目录真实 mkdir、ICO 二进制 9 帧解析、py_compile 均通过；docs/make_screenshot.py 真实启动 GUI 并抓 docs/screenshot-templates.png，内含模板回填/预览断言；并修复预览把 {n:02d} 误判缺占位符的 bug。
未验证：人工交互（鼠标点击、滚轮滚动、DPI 缩放）未经人手逐项验证；exe 图标在任务栏/桌面的显示效果未验证；同类工具对比仅基于网页检索。
局限1：cn_num 仅 1..99，>=100 回退阿拉伯数字；sanitize 直接删非法字符且不检测清单内重名，同名时后项被跳过。
局限2：勾选覆盖时执行 os.makedirs(exist_ok=True)，不清空已有内容，语义是「确保存在」而非重建。
局限3：仅 Windows（os.startfile / iconbitmap / Windows 非法字符集）；templates.json 写在 exe 同目录，目录只读时保存模板失败并弹错。
局限4：仓库无 tests/，多数断言为临时内联脚本、不可复跑，仅 docs/make_screenshot.py 可复跑；模板无导入导出、无版本迁移。
维护注意：make_icon.py 手工拼 ICO 二进制，因 PIL 的 save(sizes=..., append_images=...) 只写首帧，曾导致图标仅 16px 而糊；_on_canvas_configure 须同时钉 rows_frame 宽度，否则逐行 Entry 溢出卡片。
git 历史：本仓库初始化时仅 1 条提交，无「近 20 条提交」可引用；事实来自当前文件、README.md 及 docs/ 下截图。
AI-BRIEF:END -->
