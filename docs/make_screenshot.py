#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""为 README 生成真实 GUI 截图：启动 App，加载示例模板，抓取窗口。
仅文档用途，不参与打包。"""
import importlib.util
import json
import os
import time

from PIL import ImageGrab

HERE = os.path.dirname(os.path.abspath(__file__))      # docs/
ROOT = os.path.dirname(HERE)                            # 项目根
TPL_PATH = os.path.join(ROOT, "templates.json")
OUT = os.path.join(HERE, "screenshot-templates.png")

# 一份真实可加载的示例模板，用于演示「参数模板」回填
sample = {
    "素材归档": {
        "dir": "D:\\项目\\2026_素材",
        "count": 6,
        "start": 1,
        "format": "01_",
        "custom_fmt": "{n:02d}-",
        "overwrite": False,
        "names": ["AEP", "MP3", "MP4", "DNG", "OTH", "FIN"],
    }
}
with open(TPL_PATH, "w", encoding="utf-8") as f:
    json.dump(sample, f, ensure_ascii=False, indent=2)

spec = importlib.util.spec_from_file_location(
    "bfc", os.path.join(ROOT, "batch_file_creator.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

app = m.App()
app.geometry("880x600+90+50")
app.update_idletasks()
app.var_template.set("素材归档")
app._on_template_selected()          # 真实走一遍模板加载回填
app.update()
# 回归检查：带格式的 {n:02d} 不应被误判为「缺少占位符」
assert "格式里没有" not in app.preview_var.get(), app.preview_var.get()
assert [e.get() for e in app.name_entries] == [
    "AEP", "MP3", "MP4", "DNG", "OTH", "FIN"]
print("模板回填校验通过；预览:", app.preview_var.get())
app.lift()
app.focus_force()
app.attributes("-topmost", True)
time.sleep(0.8)
app.update()

x, y = app.winfo_rootx(), app.winfo_rooty()
w, h = app.winfo_width(), app.winfo_height()
img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
img.save(OUT)
print("截图已保存:", OUT, img.size)
app.destroy()

# 运行时数据不入库
os.remove(TPL_PATH)
print("已清理临时 templates.json")
