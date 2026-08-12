# Markdown to PPT HTML

把 Markdown 输入文件转换成深色科技风 PPT 风格 HTML。页面按 `1920x1080` 设计基准制作，并铺满浏览器视口。

## 使用

```powershell
python tools/md_to_ppt_html.py examples/template.md dist/template.html
```

生成后直接用浏览器打开 `dist/template.html`。

可用参数覆盖导出行为：

```powershell
python tools/md_to_ppt_html.py examples/template.md dist/template.html --no-agenda --no-step-reveal
```

- `--agenda` / `--no-agenda`：强制显示或隐藏目录页。
- `--step-reveal` / `--no-step-reveal`：强制开启或关闭分点逐条动画。

## 实时编辑器

直接用浏览器打开 `tools/live_editor.html`，左侧编辑 Markdown，右侧会实时生成 PPT 风格 HTML 预览。

- 右上角 `保存 Markdown`：把当前 Markdown 保存到浏览器本地存储，并显示保存成功提示。
- 右上角 `下载 HTML`：把右侧当前预览对应的 HTML 下载到本地，默认文件名为 `markdown-ppt-preview.html`。
- 编辑区光标移动到某个章节时，右侧预览会自动定位到对应页面。
- 右侧预览使用 `1920x1080` 原始画布按比例缩放，页面结构和样式与 `dist/template.html` 保持一致。
- 右侧预览会直接显示当前页所有分点内容；通过 `下载 HTML` 导出的文件仍保留方向键逐条显示效果。
- 编辑内容会自动保存到浏览器本地存储，刷新页面后会优先恢复上次编辑内容。

如果当前终端找不到 `python`，可直接使用安装路径：

```powershell
& 'C:\Users\zhugeheng\AppData\Local\Programs\Python\Python312\python.exe' tools\md_to_ppt_html.py examples\template.md dist\template.html
```

## Markdown 规则

- `#`：封面页标题。
- `##`：新页面。
- 空内容的 `##`：自动识别为章节页。
- `-` 或 `*` 列表：自动选择分点版式，并支持逐条显示。
- `-` 或 `*` 列表如果有 2 到 6 条：可自动识别为矩阵卡片页，按条数排成 `1x2`、`1x3`、`2x2` 或 `2x3`，最多两行。
- 如需直观指定分点样式，可直接使用符号作为列表前缀：`[]` 表示第 4 页那种大方块分点，`·` 表示第 7 页那种小方点卡片，`::` 表示第 11 页那种标题加多个小分点。
- 列表详情中使用 `；`、`;`、`｜` 或 `|` 分隔多段文字时，会自动渲染为截图里的“痛点/痒点”分点面板。
- 旧的 HTML 注释指令仍兼容：`<!-- point-style: matrix-list -->`，但推荐使用符号前缀。
- 可选分点样式：`cards`、`matrix`、`matrix-list`、`matrix-feature`。不写时会自动选择，并尽量避免相邻分点页重复同一种样式。

```markdown
## 四种典型机会缺口

[] **场景缺口**：同样的事，换个场景没人做
[] **人群缺口**：小众群体永远在凑合用
[] **体验缺口**：功能都有，但用起来痛苦
[] **AI Native 缺口**：把老产品用 AI 重新做一遍
```

- `1.` 有序列表：自动识别为时间线/步骤页，并支持逐条显示。
- `>` 引用：自动识别为金句页。
- `![alt](path)` 图片：自动识别为图文页。
- 标准 Markdown 表格：自动识别为对比表格页，适合做多对象、多维度横向对比。
- 两列表格如果第一列是 `状态` / `支持` / `是否` 等，并使用 `✓`、`✗`，会自动识别为状态清单页，适合做能力区分、权益说明或支持/不支持列表。
- 使用反引号标记重点文字，例如 `` `AGENTS.md` ``，会在标题、正文、引用、列表、时间线、卡片和表格中渲染为统一的强调标签样式。
- 工具会根据章节页自动插入目录页。

可在 Markdown 文件开头写 frontmatter 作为默认导出配置：

```markdown
---
agenda: false
step_reveal: false
---

# 封面标题
```

优先级：命令行参数 > Markdown frontmatter > 默认值。

## 视觉风格

- 背景参考 `raw/` 截图的深色科技风。
- 页面背景直接使用 `assets/bg.png`。
- 生成 HTML 时会把 `assets/bg.png` 嵌入为 base64，因此 `dist/template.html` 仍是单文件可打开。
- 背景上的点阵纹理会保留，并叠加一层弱化网格点阵；右侧地球区域会进一步淡化，避免干扰主体背景。
- 2 到 6 条列表会使用矩阵卡片排版，分别适配横向双卡、三卡、四宫格和六宫格页面。
- 内容页标题使用统一顶部位置，正文或卡片固定跟在标题下方，不做整体垂直居中。

## 交互

- `ArrowRight` / `ArrowDown` / `PageDown` / `Space`：下一条或下一页。
- `ArrowLeft` / `ArrowUp` / `PageUp` / `Backspace`：上一条或上一页。
- 鼠标单击页面空白处：下一条或下一页。
- 右下角箭头可点击翻页。
- 底部进度条显示当前页进度。
- 导出的 HTML 首次打开默认显示第 1 页；刷新页面会保持刷新前所在页。

## 验证

```powershell
& 'C:\Users\zhugeheng\AppData\Local\Programs\Python\Python312\python.exe' -m py_compile tools\md_to_ppt_html.py
& 'C:\Users\zhugeheng\AppData\Local\Programs\Python\Python312\python.exe' tools\md_to_ppt_html.py examples\template.md dist\template.html
node tools\verify_html_interaction.mjs file:///D:/codex/ppt-html/dist/template.html#4 dist/template-page4-after-key.png
```

交互验证会打开第 4 页，模拟一次右方向键，并输出截图到 `dist/template-page4-after-key.png`。
如需查看某页所有逐条内容，可在命令最后追加按键次数，例如：

```powershell
node tools\verify_html_interaction.mjs file:///D:/codex/ppt-html/dist/template.html#12 dist/template-matrix-4.png 4
```

首屏 1920x1080 渲染验证截图为 `dist/template-cover-1920.png`。
