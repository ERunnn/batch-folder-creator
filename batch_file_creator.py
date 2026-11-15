#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量建文件夹工具 (Batch Folder Creator)
======================================
为「项目管理 / 搭项目骨架」而做：在指定文件夹中一键批量创建
带序号前缀的【空文件夹】。

界面流程：
  1) 选择目标文件夹（默认 exe 所在目录；不存在自动创建）
  2) 选择数量、起始序号
  3) 选择【序号格式】（样式预设，如 1_ / 01- / 一、 / 第1章 等；或自定义模板串）
  4) 下方逐行列出 01- / 02- / 03- … ，每行右侧由你填写对应的文件夹名
     （留空则该项仅用序号，如 01-）
  5) 参数可存为用户模板（存于 exe 旁边的 templates.json，便携），无内置预设

仅依赖 Python 标准库 (tkinter)，无需任何第三方包。
"""

import json
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

# 序号格式预设：下拉显示名 -> 模板串
#   {n}   阿拉伯数字（可带格式如 {n:02d} 补零）
#   {cn}  中文数字（一、二、三…）
#   None  表示“自定义”，使用 self.var_custom_fmt 里的模板串
FORMAT_PRESETS = [
    ("1_",   "{n}_"),
    ("1-",   "{n}-"),
    ("1.",   "{n}."),
    ("1、",  "{n}、"),
    ("01_",  "{n:02d}_"),
    ("01-",  "{n:02d}-"),
    ("001_", "{n:03d}_"),
    ("一、", "{cn}、"),
    ("第1章 ", "第{n}章 "),
    ("(1) ", "({n}) "),
    ("自定义…", None),
]
FORMAT_MAP = {disp: tmpl for disp, tmpl in FORMAT_PRESETS}
CUSTOM_LABEL = "自定义…"


def sanitize(text: str) -> str:
    """去掉 Windows 文件夹名非法字符。"""
    illegal = '"<>:/\\|?*'
    for ch in illegal:
        text = text.replace(ch, "")
    return text.strip()


_CN_DIGITS = "零一二三四五六七八九"


def cn_num(n: int) -> str:
    """把整数转成中文数字（支持 1-99，超出回退阿拉伯数字）。"""
    if n <= 0:
        return str(n)
    if n < 10:
        return _CN_DIGITS[n]
    if n == 10:
        return "十"
    if n < 20:
        return "十" + _CN_DIGITS[n - 10]
    if n < 100:
        tens, ones = n // 10, n % 10
        s = _CN_DIGITS[tens] + "十"
        if ones:
            s += _CN_DIGITS[ones]
        return s
    return str(n)


def format_prefix(n: int, tmpl: str) -> str:
    """根据模板串生成序号前缀。模板中 {cn} 先替换为中文数字，再用 {n} 格式化。"""
    if not tmpl:
        tmpl = "{n}_"
    t = tmpl.replace("{cn}", cn_num(n))
    try:
        return t.format(n=n)
    except Exception:
        try:
            return t.format(n)
        except Exception:
            return t


def _asset_path(name: str):
    """返回随仓库分发的资源文件路径（收款码等）。
    打包后资源在 sys._MEIPASS；开发时在本脚本目录下的 assets/。"""
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    p = os.path.join(base, "assets", name)
    return p if os.path.exists(p) else None


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()               # 先隐藏：构建并定位后再显示，避免左上角闪一下
        self.title("批量建文件夹工具")

        # 双击 exe 时 cwd 即 exe 所在目录；脚本模式下为启动目录
        self.target_dir = os.getcwd()

        # 模板存储路径：跟随 exe（便携）；开发模式下跟随脚本
        if getattr(sys, "frozen", False):
            self.base_dir = os.path.dirname(sys.executable)
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.templates_path = os.path.join(self.base_dir, "templates.json")

        # 逐行名称输入框集合；_names 是名称的持久缓存，
        # 避免分步修改「数量」时中间态重建把已填内容丢掉
        self.name_entries = []
        self._names = []

        self._build_vars()
        self._build_ui()
        self._set_icon()
        self._on_format_change()      # 初始化自定义框状态
        self.rebuild_rows()
        self._refresh_template_list()
        self._update_preview()         # 首屏即显示示例（原来要改动参数才出现）
        self._center_and_show()        # 定位到屏幕中央后再显示

    # ---------------- 居中 ----------------
    def _center_and_show(self):
        self.update_idletasks()
        w, h = self.winfo_reqwidth(), self.winfo_reqheight()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        px = max((sw - w) // 2, 0)
        py = max((sh - h) // 2, 0)
        self.geometry(f"{w}x{h}+{px}+{py}")
        self.deiconify()

    # ---------------- 图标 ----------------
    def _set_icon(self):
        # 打包后用 exe 内嵌图标；开发时用旁边的 folder_plus.ico
        try:
            if getattr(sys, "frozen", False):
                self.iconbitmap(sys.executable)
            else:
                ico = os.path.join(self.base_dir, "folder_plus.ico")
                if os.path.exists(ico):
                    self.iconbitmap(ico)
        except Exception:
            pass

    # ---------------- 变量 ----------------
    def _build_vars(self):
        self.var_dir = tk.StringVar(value=self.target_dir)
        self.var_count = tk.StringVar(value="5")
        self.var_start = tk.StringVar(value="1")
        # 序号格式：下拉显示名
        self.var_format = tk.StringVar(value="1_")
        self.var_custom_fmt = tk.StringVar(value="{n:02d}-")    # 自定义模板串
        self.var_overwrite = tk.BooleanVar(value=False)
        self.var_template = tk.StringVar(value="— 选择模板 —")

        # 数量/起始/格式/自定义串 变化时，重建逐行列表 + 预览
        for v in (self.var_count, self.var_start, self.var_format,
                  self.var_custom_fmt):
            v.trace_add("write", lambda *_: (self.rebuild_rows(),
                                             self._update_preview()))
        self.var_format.trace_add("write", lambda *_: self._on_format_change())

    # ---------------- 界面 ----------------
    def _build_ui(self):
        pad = {"padx": 8, "pady": 4}
        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, padx=12, pady=12)

        frm.columnconfigure(1, weight=1)

        # 1) 目标文件夹
        ttk.Label(frm, text="目标文件夹：").grid(row=0, column=0, sticky="w", **pad)
        ttk.Entry(frm, textvariable=self.var_dir).grid(
            row=0, column=1, columnspan=2, sticky="ew", **pad)
        ttk.Button(frm, text="浏览...", command=self._browse).grid(
            row=0, column=3, sticky="e", **pad)

        # 2) 数量 / 起始序号
        ttk.Label(frm, text="文件夹数量：").grid(row=1, column=0, sticky="w", **pad)
        ttk.Entry(frm, textvariable=self.var_count, width=12).grid(
            row=1, column=1, sticky="w", **pad)
        ttk.Label(frm, text="起始序号：").grid(row=1, column=2, sticky="w", **pad)
        ttk.Entry(frm, textvariable=self.var_start, width=12).grid(
            row=1, column=3, sticky="w", **pad)

        # 3) 序号格式（样式预设）+ 自定义模板串
        ttk.Label(frm, text="序号格式：").grid(row=2, column=0, sticky="w", **pad)
        ttk.Combobox(frm, textvariable=self.var_format,
                     values=[d for d, _ in FORMAT_PRESETS],
                     state="readonly", width=12).grid(
            row=2, column=1, sticky="w", **pad)
        ttk.Label(frm, text="自定义模板：").grid(row=2, column=2, sticky="w", **pad)
        self.custom_entry = ttk.Entry(frm, textvariable=self.var_custom_fmt,
                                      state="disabled")
        self.custom_entry.grid(row=2, column=3, sticky="ew", **pad)

        # 4) 实时示例
        self.preview_var = tk.StringVar(value="")
        ttk.Label(frm, textvariable=self.preview_var, foreground="#1a7f37").grid(
            row=3, column=0, columnspan=4, sticky="w", **pad)

        # 5) 参数模板（用户自建，无内置预设）
        ttk.Label(frm, text="参数模板：").grid(row=4, column=0, sticky="w", **pad)
        self.template_cb = ttk.Combobox(frm, textvariable=self.var_template,
                                        state="readonly", width=14)
        self.template_cb.grid(row=4, column=1, sticky="w", **pad)
        self.template_cb.bind("<<ComboboxSelected>>", self._on_template_selected)
        ttk.Button(frm, text="保存模板", command=self._save_current_as_template).grid(
            row=4, column=2, sticky="w", padx=4)
        ttk.Button(frm, text="删除模板", command=self._delete_template).grid(
            row=4, column=3, sticky="w", padx=4)

        # 6) 覆盖选项
        ttk.Checkbutton(frm, text="覆盖已存在的同名文件夹",
                        variable=self.var_overwrite).grid(
            row=5, column=0, columnspan=4, sticky="w", **pad)

        # 7) 逐行列表（可滚动）
        self.rows_info = tk.StringVar(value="")
        ttk.Label(frm, textvariable=self.rows_info).grid(
            row=6, column=0, columnspan=4, sticky="w", **pad)

        self.rows_canvas = tk.Canvas(frm, height=200, borderwidth=1,
                                     relief="sunken")
        self.rows_canvas.grid(row=7, column=0, columnspan=4, sticky="nsew",
                              padx=8, pady=4)
        self.rows_scroll = ttk.Scrollbar(frm, orient="vertical",
                                         command=self.rows_canvas.yview)
        self.rows_scroll.grid(row=7, column=4, sticky="ns", pady=4)
        self.rows_canvas.configure(yscrollcommand=self.rows_scroll.set)
        self.rows_frame = ttk.Frame(self.rows_canvas)
        self.rows_window = self.rows_canvas.create_window(
            (0, 0), window=self.rows_frame, anchor="nw")
        self.rows_canvas.bind("<Configure>", self._on_canvas_configure)
        self.rows_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # 8) 按钮行
        btn_row = ttk.Frame(frm)
        btn_row.grid(row=8, column=0, columnspan=4, sticky="ew", pady=6)
        ttk.Button(btn_row, text="生成", command=self._generate).pack(
            side="left", padx=(0, 8))
        self.open_btn = ttk.Button(btn_row, text="打开目标文件夹",
                                   command=self._open_dir, state="disabled")
        self.open_btn.pack(side="left")
        # 投喂作者入口（仿同作者其他项目的常驻按钮，README 不体现）
        feed_btn = ttk.Button(btn_row, text="投喂作者 (๑´ㅂ`๑)",
                              command=self._open_feed_dialog)
        feed_btn.pack(side="right", padx=(8, 0))

        # 9) 日志
        ttk.Label(frm, text="运行日志：").grid(row=9, column=0, sticky="w", **pad)
        self.log = tk.Text(frm, height=7, width=60, state="disabled")
        self.log.grid(row=10, column=0, columnspan=4, sticky="ew", pady=4)
        self.log.configure(font=("Consolas", 9))

        frm.rowconfigure(7, weight=1)

    # ---------------- 逐行列表 ----------------
    def _on_canvas_configure(self, event):
        # 关键修复：同时把内部 Frame 的真实宽度钉到画布可视宽度，
        # 否则 Entry 的 fill=x 会把内容撑出卡片右边界。
        self.rows_canvas.itemconfig(self.rows_window, width=event.width)
        self.rows_frame.configure(width=event.width)

    def _on_mousewheel(self, event):
        self.rows_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def rebuild_rows(self):
        # 先把当前控件的值同步回持久缓存（按索引覆盖、只增不减）。
        # 关键：分步修改「数量」（清空→逐字符输入）会触发多次重建，
        # 中间态 count=0/1 时控件已被销毁，若只从当前控件取旧值就会永久丢失。
        for i, e in enumerate(self.name_entries):
            name = e.get()
            if i < len(self._names):
                self._names[i] = name
            else:
                self._names.append(name)
        for child in self.rows_frame.winfo_children():
            child.destroy()
        self.name_entries = []

        try:
            count = int(self.var_count.get() or "0")
            start = int(self.var_start.get() or "1")
        except ValueError:
            count, start = 0, 1
        if count < 0:
            count = 0
        tmpl = self._get_template()

        for i in range(count):
            n = start + i
            prefix = format_prefix(n, tmpl)
            row = ttk.Frame(self.rows_frame)
            row.pack(fill="x", padx=2, pady=2)
            # 序号前缀紧贴内容，左不留空；输入框占满剩余宽度且不溢出
            ttk.Label(row, text=prefix, anchor="w").pack(
                side="left", padx=(0, 6))
            ent = ttk.Entry(row)
            if i < len(self._names):
                ent.insert(0, self._names[i])
            ent.pack(side="left", fill="x", expand=True)
            self.name_entries.append(ent)

        self.rows_info.set(
            f"共 {count} 个文件夹（右侧填写名称，留空则仅用序号）")
        self.rows_canvas.configure(scrollregion=self.rows_canvas.bbox("all"))

    # ---------------- 模板存取（仅用户自建） ----------------
    def _load_templates(self) -> dict:
        try:
            if os.path.exists(self.templates_path):
                with open(self.templates_path, "r", encoding="utf-8") as f:
                    return json.load(f) or {}
        except Exception:
            pass
        return {}

    def _save_templates(self, data: dict) -> bool:
        try:
            with open(self.templates_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            messagebox.showerror("保存失败", f"无法写入模板文件：\n{e}")
            return False

    def _refresh_template_list(self):
        names = list(self._load_templates().keys())
        self.template_cb["values"] = ["— 选择模板 —"] + names
        self.var_template.set("— 选择模板 —")

    def _collect_config(self) -> dict:
        return {
            "dir": self.var_dir.get(),
            "count": int(self.var_count.get() or 0),
            "start": int(self.var_start.get() or 1),
            "format": self.var_format.get(),
            "custom_fmt": self.var_custom_fmt.get(),
            "overwrite": self.var_overwrite.get(),
            "names": [e.get() for e in self.name_entries],
        }

    def _apply_config(self, tpl: dict):
        self.var_dir.set(tpl.get("dir", ""))
        self.var_count.set(str(tpl.get("count", 5)))
        self.var_start.set(str(tpl.get("start", 1)))
        self.var_overwrite.set(bool(tpl.get("overwrite", False)))
        self.var_format.set(tpl.get("format", "1_")
                            if tpl.get("format") in FORMAT_MAP else "1_")
        self.var_custom_fmt.set(tpl.get("custom_fmt", "{n:02d}-"))

        self.rebuild_rows()
        names = tpl.get("names") or []
        for i, ent in enumerate(self.name_entries):
            if i < len(names):
                ent.delete(0, "end")
                ent.insert(0, names[i])
        # 载入模板是「整体替换」：缓存同步并裁剪到当前行数，
        # 否则之后再改数量会串回上一份配置里的旧名称
        self._names = [e.get() for e in self.name_entries]

        self._on_format_change()
        self._update_preview()

    def _on_template_selected(self, *_):
        name = self.var_template.get()
        if not name or name == "— 选择模板 —":
            return
        tpl = self._load_templates().get(name)
        if tpl:
            self._apply_config(tpl)

    def _save_current_as_template(self):
        name = simpledialog.askstring("保存模板", "请输入模板名称：", parent=self)
        if not name or not name.strip():
            return
        name = name.strip()
        data = self._load_templates()
        data[name] = self._collect_config()
        if self._save_templates(data):
            self._refresh_template_list()
            self.var_template.set(name)
            messagebox.showinfo("已保存", f"模板「{name}」已保存。")

    def _delete_template(self):
        name = self.var_template.get()
        if not name or name == "— 选择模板 —":
            messagebox.showwarning("提示", "请先在下拉框选择一个要删除的模板。")
            return
        if not messagebox.askyesno("确认", f"确定删除模板「{name}」？"):
            return
        data = self._load_templates()
        data.pop(name, None)
        if self._save_templates(data):
            self._refresh_template_list()
            messagebox.showinfo("已删除", f"模板「{name}」已删除。")

    # ---------------- 交互 ----------------
    def _browse(self):
        d = filedialog.askdirectory(initialdir=self.var_dir.get() or os.getcwd())
        if d:
            self.var_dir.set(d)

    def _on_format_change(self, *_):
        state = "normal" if self.var_format.get() == CUSTOM_LABEL else "disabled"
        self.custom_entry.configure(state=state)

    def _get_template(self) -> str:
        disp = self.var_format.get()
        if disp == CUSTOM_LABEL:
            return self.var_custom_fmt.get()
        return FORMAT_MAP.get(disp, "{n}_")

    def _update_preview(self):
        tmpl = self._get_template()
        try:
            start = int(self.var_start.get() or "1")
        except ValueError:
            start = 1
        sample = format_prefix(start, tmpl) + "项目名"
        # 提示：模板里没有序号占位符时，序号不会变化
        # 用前缀判断：{n:02d} 这类带格式说明的同样是有效占位符
        if "{n" not in tmpl and "{cn" not in tmpl:
            self.preview_var.set(
                f"示例输出：{sample}（文件夹）  ⚠ 格式里没有 {{n}}，序号不会变化")
        else:
            self.preview_var.set(f"示例输出：{sample}（文件夹）")

    def _get_name_list(self) -> list:
        return [sanitize(e.get()) for e in self.name_entries]

    def _build_targets(self):
        """返回 [base, ...]；参数非法返回 None；无项目返回 []。"""
        tmpl = self._get_template()
        try:
            start = int(self.var_start.get() or "1")
        except ValueError:
            return None
        names = self._get_name_list()
        if not names:
            return []
        return [(format_prefix(start + i, tmpl) + nm if nm
                 else format_prefix(start + i, tmpl))
                for i, nm in enumerate(names)]

    def _log(self, msg: str):
        self.log.configure(state="normal")
        self.log.insert("end", msg + "\n")
        self.log.configure(state="disabled")
        self.log.see("end")

    def _generate(self):
        folder = self.var_dir.get().strip() or os.getcwd()
        try:
            os.makedirs(folder, exist_ok=True)
        except Exception as e:
            messagebox.showerror("文件夹错误", f"无法创建/访问目标文件夹：\n{e}")
            return

        targets = self._build_targets()
        if targets is None:
            messagebox.showerror("参数错误", "起始序号必须为整数。")
            return
        if not targets:
            messagebox.showwarning(
                "参数错误",
                "没有可生成的项目：请先设置“文件夹数量”，并在下方逐行填写名称"
                "（或留空仅用序号）。")
            return

        overwrite = self.var_overwrite.get()
        created = skipped = 0
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

        for base in targets:
            path = os.path.join(folder, base)
            if os.path.exists(path):
                if overwrite:
                    try:
                        os.makedirs(path, exist_ok=True)
                        self._log(f"已覆盖：{base}/")
                        created += 1
                    except Exception as e:
                        self._log(f"覆盖失败：{base}/ ({e})")
                else:
                    self._log(f"已跳过（已存在）：{base}/")
                    skipped += 1
                continue
            try:
                os.makedirs(path, exist_ok=True)
                self._log(f"已创建文件夹：{base}/")
                created += 1
            except Exception as e:
                self._log(f"创建失败：{base}/ ({e})")

        summary = f"\n完成：新建 {created} 个，跳过 {skipped} 个。"
        self._log(summary)
        self.open_btn.configure(state="normal")
        messagebox.showinfo("完成", summary)

    def _open_dir(self):
        folder = self.var_dir.get().strip() or os.getcwd()
        if os.path.isdir(folder):
            os.startfile(folder)

    def _open_feed_dialog(self):
        """投喂 Token：微信 / 支付宝收款码（仿 V2Live 的可爱向弹窗）。"""
        dlg = tk.Toplevel(self)
        dlg.withdraw()                # 先隐藏，定位后再显示，避免闪一下
        dlg.title("投喂 Token")
        dlg.transient(self)
        # 用软件 logo 替换 Tk 默认的羽毛图标
        try:
            if getattr(sys, "frozen", False):
                dlg.iconbitmap(sys.executable)
            else:
                ico = os.path.join(self.base_dir, "folder_plus.ico")
                if os.path.exists(ico):
                    dlg.iconbitmap(ico)
        except Exception:
            pass
        self._feed_photos = []  # 保持 PhotoImage 引用，避免被 GC 后图片消失

        body = ttk.Frame(dlg, padding=14)
        body.pack(fill="both", expand=True)

        msg = ttk.Label(
            body,
            text="如果这个小工具帮到了你，\n欢迎投喂作者一个 Token 续续命 (๑•̀ㅂ•́)و✧",
            justify="center")
        msg.pack(pady=(0, 12))

        rowd = ttk.Frame(body)
        rowd.pack()
        for img, name, kao in (("qr_wechat.png", "微信", "(๑´ㅂ`๑)"),
                               ("qr_alipay.png", "支付宝", "(≧▽≦)")):
            col = ttk.Frame(rowd)
            col.pack(side="left", padx=12)
            path = _asset_path(img)
            if path:
                # 两张码已在 assets/ 内预先统一为 200×200，直接读取即可等大显示
                photo = tk.PhotoImage(file=path)
                self._feed_photos.append(photo)
                pic = ttk.Label(col, image=photo)
            else:
                pic = ttk.Label(col, text="（收款码未随仓库分发）")
            pic.pack()
            ttk.Label(col, text=f"{name} {kao}", justify="center").pack(pady=(8, 0))

        ok = ttk.Button(body, text="谢谢老板 (*^▽^*)", command=dlg.destroy)
        ok.pack(pady=(12, 0))

        # 居中：优先相对父窗口；若超出屏幕则相对屏幕居中；定位后再显示
        dlg.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        dw, dh = dlg.winfo_reqwidth(), dlg.winfo_reqheight()
        px = self.winfo_rootx() + (self.winfo_width() - dw) // 2
        py = self.winfo_rooty() + (self.winfo_height() - dh) // 2
        if px < 0 or px + dw > sw:
            px = max((sw - dw) // 2, 0)
        if py < 0 or py + dh > sh:
            py = max((sh - dh) // 2, 0)
        dlg.geometry(f"{dw}x{dh}+{px}+{py}")
        dlg.deiconify()
        dlg.grab_set()


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
