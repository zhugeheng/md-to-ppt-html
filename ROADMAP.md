# ROADMAP

## Current Stage

首版已完成并进行背景修正：Markdown 转 PPT 风格 HTML 工具、示例模板、生成文件、全屏 1920x1080 样式、`assets/bg.png` 背景接入、点阵弱化、矩阵卡片排版、目录单列排版、分点样式指定、分点样式自动均衡、交互验证、用户级 Python PATH 配置、全局 Codex skill 封装和本地实时编辑预览页面均已完成。

## Completed

- 已基于当前 `examples/template.md` 重新生成并提交 `dist/template.html`，作为仓库内可直接打开的使用示例；其余 `dist/` 生成物继续忽略。
- 已从 GitHub 仓库移除 `dist/` 生成目录，并在 `.gitignore` 中忽略该目录；本地生成物保留。
- 已按要求删除 `examples/` 中的测试 Markdown：`section-width-test.md`、`symbol-style-test.md`、`wrap-test.md`；`dist/` 生成物保持不变。
- 已初始化本地 Git 仓库并首次推送至 GitHub：`https://github.com/zhugeheng/md-to-ppt-html`；保留远程原有 `LICENSE`，未上传 `raw/` 参考截图或 `dist/chrome-*` 浏览器临时目录。

- 已创建 `AGENTS.md`，明确目录、生成物和验证规则。
- 已创建 `tools/md_to_ppt_html.py`，实现 Markdown 转 PPT 风格 HTML 的 Python 转换器。
- 已创建 `tools/verify_html_interaction.mjs`，用于本地 Chrome headless 键盘交互验证。
- 已创建 `examples/template.md`，用 `raw/` 截图中的产品思维内容填充模板。
- 已创建 `README.md`，说明使用方式和 Markdown 编写规则。
- 已将生成页面改为按 `1920x1080` 设计基准并铺满浏览器视口，不再产生左右黑边。
- 已改为直接使用 `assets/bg.png` 作为整页背景，并以 base64 方式嵌入生成 HTML，保持 `dist/template.html` 单文件可打开。
- 已弱化背景点阵效果：`bg.png` 自带点阵保留，生成 HTML 的叠加点阵整体降低透明度，并在右侧地球区域退到透明。
- 已补齐 `raw/微信图片_20260619101019_231_230.png` 和 `raw/微信图片_20260619101024_235_230.png` 对应的矩阵卡片排版：2 到 6 条列表自动排为 `1x2`、`1x3`、`2x2` 或 `2x3`，最多两行。
- 已更新 `examples/template.md`，加入“只做痛点，不碰痒点”和“四种典型机会缺口”两页示例内容。
- 已修正 `tools/verify_html_interaction.mjs`，支持按传入 hash 验证指定页面，并支持可选按键次数。
- 已统一内容页标题位置：标题固定靠上，正文或卡片跟随标题下方，不再整体垂直居中。
- 已按参考图方向继续上移内容页大标题：取消百分比顶部内边距导致的标题下沉，`.slide-inner` 顶部改为固定 `4.6rem`，统一标题锚点改为 `0`，封面标题区和引用页引用块也同步上移。
- 已统一页面左上边距：新增 `--edge-offset: 4.6rem`，`.slide-inner` 左右内边距与顶部一致；封面、章节、引用和陈述页等绝对定位内容同步使用该边界。
- 已调整分点字体层级：分点标题和正文缩小，正文统一使用偏灰色弱化。
- 已调整引用页样式：顶部引号、正文大小和署名灰度更接近参考图。
- 已调整矩阵页细节：`matrix-list` 的第二个卡片带青绿色边框，`matrix-feature` 的青绿色方形图标降低亮度和发光。
- 已支持 Markdown 显式指定分点样式：`cards`、`matrix`、`matrix-list`、`matrix-feature`；未指定时自动选择，并尽量避免相邻分点页重复同一种样式。
- 已生成 `dist/template.html`。
- 已生成 `dist/template-cover.png` 和 `dist/template-page4-after-key.png` 作为渲染验证截图。
- 已生成 `dist/template-cover-1920.png` 作为 1920x1080 全屏渲染验证截图。
- 已将 Python 3.12 安装目录和 `Scripts` 目录写入当前用户级 PATH。
- 已封装全局 Codex skill：`C:\Users\zhugeheng\.codex\skills\markdown-ppt-html`，包含转换脚本、交互验证脚本、内置 `assets/bg.png` 和 Markdown 模板；转换脚本会优先使用当前项目的 `assets/bg.png`，否则回退到 skill 内置背景。
- 已创建 `tools/live_editor.html`，提供左侧 Markdown 编辑、右侧 PPT 风格 HTML 实时预览、Markdown 文件导入、模板恢复和右上角 HTML 下载按钮。
- 已修正 `tools/live_editor.html` 右侧预览：iframe 使用 `1920x1080` 原始画布并按容器比例缩放，预览页结构和 CSS 同步为 `dist/template.html` 的正式输出样式，目录、矩阵、卡片、进度条和右下角控件均按正式页面渲染。
- 已修正实时编辑器初始定位：自动插入的目录页标记为合成页，光标到页面的联动计算跳过合成目录页，打开页面和光标位于 Markdown 顶部时均显示第 1 页封面。
- 已为实时编辑器新增 Markdown 本地保存：右上角新增 `保存 Markdown` 按钮，编辑输入、导入文件和恢复模板时会写入浏览器 `localStorage`，刷新页面后优先恢复上次编辑内容。
- 已为实时编辑器手动保存新增消息提示：点击 `保存 Markdown` 后会在页面右上区域显示 `Markdown 已保存成功`，保存失败时显示失败提示。
- 已美化实时编辑器左侧 Markdown 编辑区滚动条：去除浏览器默认白边，改为深色轨道、青绿色渐变滑块和深色滚动角。
- 已拆分实时编辑器预览 HTML 和导出 HTML：右侧预览模式直接显示当前页所有分点内容并直接翻页，点击 `下载 HTML` 导出的正式 HTML 仍保留方向键逐条显示。
- 已新增标准 Markdown 表格自动版式：表格会渲染为深色科技风对比表格页，适合多对象、多维度横向比较；`examples/template.md` 和实时编辑器内置模板已加入 `AI 编程助手对比` 示例。
- 已同步全局 `markdown-ppt-html` skill：转换脚本、内置模板和 `SKILL.md` 说明已包含标准 Markdown 表格对比版式。
- 已新增两列状态表格自动版式：当标准 Markdown 表格第一列为 `状态` / `支持` / `是否` 等，并使用 `✓`、`✗` 作为状态值时，自动渲染为对勾/叉号状态清单页，适合能力区分、权益说明和支持/不支持列表；`examples/template.md` 和实时编辑器内置模板已加入 `能力权益区分` 示例。
- 已修复分点标题长文本换行：卡片、矩阵和时间线标题统一支持长文本自动换行，并为相关 grid 文本容器设置 `min-width: 0`；后续进一步将卡片和时间线 grid 文本列改为 `minmax(0, 1fr)`，并为标题补充 `display: block`、`max-width: 100%`、`white-space: normal`、`line-break: anywhere`，避免长标题撑出页面；修复已同步到实时编辑器和全局 `markdown-ppt-html` skill。
- 已修正列表标题/说明拆分规则：移除 `标题：说明` 解析中原有的 28 字标题长度限制，避免较长标题如 `魔法选手 —— Claude Code/Codex+自家模型` 无法拆出说明，导致整句进入标题区域。
- 已精简实时编辑器右上角操作区：移除 `导入` 和 `模板` 按钮及对应文件输入/事件逻辑，仅保留 `保存 Markdown` 和 `下载 HTML`。
- 已修复数字时间线分点圆圈变椭圆问题：`.timeline span` 改为显式等宽等高、禁止收缩，并使用 `border-radius: 50%` 和固定 `line-height`，同步到正式导出、实时编辑器和全局 `markdown-ppt-html` skill。
- 已扩展反引号强调样式：分点标题/说明拆分时不再清除 Markdown 内联标记，反引号内容可在标题、正文、引用、列表、时间线、卡片、矩阵和表格中统一渲染为强调标签样式；同步到实时编辑器和全局 `markdown-ppt-html` skill。
- 已修复章节页标题默认宽度过窄问题：`.section-title` 增加左右边界和显式可用宽度，章节页 `h2` 改为基于完整容器限制宽度，避免中文章节标题在 6 个字符左右提前换行；同步到实时编辑器和全局 `markdown-ppt-html` skill。
- 已调整为最终符号化分点样式指定语法：`[]` 指定第 4 页那种大方块分点（`matrix-feature`），`·` 指定第 7 页那种小方点卡片（`cards`），`::` 指定第 11 页那种标题加多个小分点（`matrix-list`），数字列表继续指定序列型分点（`timeline`），`-` / `*` 继续保持自动选择；临时旧符号已移除且不兼容，新语法已同步到实时编辑器、模板和全局 `markdown-ppt-html` skill。
- 已优化 `::` 对应的 `matrix-list` 1x3 布局宽度：仅对 `.matrix-style-list .matrix-count-3` 放宽到整页可用宽度，并缩小列间距与单卡左右内边距，减少标题和说明文字过早换行；同步到实时编辑器和全局 `markdown-ppt-html` skill。
- 已增强导出 HTML 的 PPT 式导航交互：`ArrowDown` 支持下一条/下一页，`ArrowUp` 支持上一条/上一页，鼠标单击页面空白处支持下一条/下一页；右下角按钮阻止点击冒泡，避免按钮点击触发两次翻页；同步到实时编辑器导出逻辑和全局 `markdown-ppt-html` skill。
- 已将背景资源移动到 `assets/bg.png`，并同步更新转换脚本、实时编辑器、README 和全局 `markdown-ppt-html` skill；`assets/earth-bg.png` 已按要求移除。
- 已将目录页改为单列显示：`.agenda ol` 从两列网格改为 `minmax(0, 1fr)` 单列，并限制目录内容宽度，正式导出、实时编辑器、现有 `dist/*.html` 生成物和全局 skill 已同步。
- 已修复导出 HTML 打开/刷新页码行为：首次打开导出文件时忽略旧 hash 并默认显示第 1 页；翻页后会写入当前页 hash，并使用当前标签页的 `sessionStorage` 标记识别刷新场景，刷新页面时恢复刷新前所在页；正式转换器、实时编辑器导出脚本、现有 `dist/*.html` 和全局 `markdown-ppt-html` skill 已同步。
- 已修复实时编辑器输入时焦点被右侧预览 iframe 抢走的问题：预览模式下不再执行 iframe 内部 `document.body.focus()`，并在 Markdown textarea 原本持有焦点时，预览刷新后显式恢复编辑器焦点。
- 已加固导出 HTML 刷新保持页码逻辑：在 `sessionStorage` 之外增加同一标签页的 `window.name` 标记作为兜底，避免部分浏览器或本地文件场景下刷新仍回到第 1 页；同时为导出页增加 `user-select: none`，避免鼠标点击或拖动翻页时出现蓝色文字选区。
- 已修复实时编辑器导出 HTML 的刷新页码根因：导出文件内含 `<base href="...live_editor.html">` 时，原先 `history.replaceState(..., "#页码")` 会受 base 影响，导致当前导出文件 hash 没有被真实更新；已改为基于 `location.href.split("#")[0]` 拼出当前文件绝对 URL 后再写入 hash，并保留 `history.state` 标记。
- 已新增导出控制参数：Python 转换器支持 `--agenda` / `--no-agenda` 和 `--step-reveal` / `--no-step-reveal`；Markdown frontmatter 支持 `agenda: false`、`step_reveal: false`；实时编辑器导出逻辑读取 Markdown frontmatter/default，但不在右上角显示对应控件。优先级为命令行参数 > Markdown frontmatter > 默认值。
- 已按要求隐藏实时编辑器右上角的 `目录页` 与 `逐条动画` 控件：保留隐藏输入供导出逻辑读取 Markdown frontmatter/default，界面上仅显示 `保存 Markdown` 和 `下载 HTML`。

## In Progress

- 待用户试用后反馈版式细节。

## Todo

- 根据实际 Markdown 内容继续扩展更多自动排版类型。
- 如果需要常用命令更短，后续可补充批处理脚本。

## Blockers

- 无。

## Latest Verification

- 示例 HTML 验证：`tools/md_to_ppt_html.py` 编译通过，并成功根据当前 `examples/template.md` 生成 `dist/template.html`；HTML 结构检查确认包含进度条和导航控件。
- `dist/` 远程清理验证：Git 已不再跟踪 `dist/`，本地目录文件数量保持为 3,075。
- 测试示例清理验证：`examples/` 中不再存在文件名包含 `test` 的文件。
- GitHub 首次推送验证：本地 `main` 已跟踪 `origin/main` 且工作区干净；`git ls-remote --heads origin main` 返回远程 `main` 提交 `3f612f9`。

- 背景资源迁移与目录单列验证：`tools/live_editor.html` 内联脚本 Node 语法校验通过，确认背景路径为 `../assets/bg.png` 且不再包含 `../bg.png`；静态断言确认 `tools/md_to_ppt_html.py`、`tools/live_editor.html`、`dist/template.html` 和全局 skill 脚本均包含 `grid-template-columns: minmax(0, 1fr)`、不再包含旧 `grid-template-columns: 1fr 1fr`；`node tools\verify_html_interaction.mjs file:///D:/codex/ppt-html/dist/template.html#2 dist/template-agenda-single-column.png 0` 通过，生成目录页截图；Chrome headless 计算样式确认目录页 `gridTemplateColumns` 为单个 `1184px`、`columnCount: 1`、5 个目录项左边距一致。
- Python 编译和重新生成命令本轮未能在沙箱内完成：当前 shell 未加载 `python`，`py -3.12` 在沙箱内提示 `No installed Python found`；提权调用实际 Python 路径被自动审批层因额度限制拦截。已用 Node 静态断言和 Chrome headless 渲染检查完成替代验证。
- 导出 HTML 打开/刷新页码验证：Node 静态检查确认 `tools/md_to_ppt_html.py`、`tools/live_editor.html`、全局 skill 脚本和 `dist/*.html` 均包含 `hasOpenedInThisTab` 与 `sessionStorage` 新逻辑，`tools/live_editor.html` 和 8 个 `dist/*.html` 内联脚本均通过 `new Function` 语法检查；Chrome headless 打开 `file:///D:/codex/ppt-html/dist/template.html#19` 实测首次落到 `1 / 19` 且 hash 被替换为 `#1`，点击两次翻到 `3 / 19` 后刷新，页面仍保持 `3 / 19`，导航类型为 `reload`。
- 实时编辑器焦点验证：`tools/live_editor.html` 内联脚本通过 Node `new Function` 语法检查；Chrome headless 打开 `file:///D:/codex/ppt-html/tools/live_editor.html`，聚焦 `#editor` 后触发 Markdown 输入、普通打字和 `Backspace`，三次检查 `document.activeElement` 均保持为 `#editor`，右侧 iframe 未抢焦点，预览页码正常更新为 `2 / 2`。
- 刷新页码与文字选区加固验证：Node 语法检查确认 `tools/live_editor.html` 和 8 个 `dist/*.html` 内联脚本均可解析；静态检查确认正式转换器、实时编辑器导出逻辑、全局 skill 和 `dist/*.html` 均包含 `window.name` 双标记逻辑与 `user-select: none`；Chrome headless 打开 `dist/template.html#19` 首次落到 `1 / 19`，点击两次到 `3 / 19` 后刷新仍保持 `3 / 19`；拖拽页面后 `document.getSelection()` 为空；额外清空 `sessionStorage` 后刷新仍保持 `3 / 19`，验证 `window.name` 兜底生效。
- 实时编辑器导出 HTML 刷新页码复验：Chrome headless 打开 `tools/live_editor.html` 后直接读取运行时 `currentHtml`，确认导出 HTML 包含 `replacePageUrl()`、`location.href.split("#")`、`markdownPptHtmlOpened`、`<base href=...>` 和 `user-select: none`，并写出 `dist/live-editor-export-refresh-test.html`；再打开该导出文件 `#19`，首次显示 `1 / 19`，点击两次后 hash 变为 `#3` 且显示 `3 / 19`，刷新后仍保持 `#3` 与 `3 / 19`，`history.state.markdownPptHtmlOpened` 为 `true`。
- 导出控制参数验证：`tools/live_editor.html` 内联脚本通过 Node `new Function` 语法检查；Chrome headless 打开实时编辑器确认默认模板 frontmatter 下 `目录页`、`逐条动画` 开关均为开启，导出 HTML 包含 `layout-agenda` 和 `const stepReveal = true`；将 Markdown 改为 `agenda: false`、`step_reveal: false` 后，开关自动变为关闭，导出 HTML 不含 `layout-agenda` 且包含 `const stepReveal = false`；手动重新打开两个开关后，导出 HTML 再次包含目录页和逐条动画。`README.md`、`examples/template.md` 和全局 `markdown-ppt-html` skill 已同步说明与模板。
- Python 编译命令本轮仍受当前 shell 环境限制：`python -m py_compile tools\md_to_ppt_html.py` 提示找不到 `python`，`py -3.12 -m py_compile tools\md_to_ppt_html.py` 提示 `No installed Python found`；已用浏览器实测和 JS 静态检查验证实时编辑器与导出 HTML 行为。
- 实时编辑器右上角控件隐藏验证：`tools/live_editor.html` 内联脚本通过 Node `new Function` 语法检查；静态检查确认 `showAgenda` 和 `stepReveal` 仍存在但均为 hidden，且不再包含 `.switch` CSS 和 `class="switch"`；Chrome headless 打开 `tools/live_editor.html` 后确认 `.actions` 可见文本仅为 `✓ 保存 Markdown` 和 `⇩ 下载 HTML`，右上角按钮数量为 2，label 数量为 0。
- `& 'C:\Users\zhugeheng\AppData\Local\Programs\Python\Python312\python.exe' -m py_compile tools\md_to_ppt_html.py`：通过。
- `& 'C:\Users\zhugeheng\AppData\Local\Programs\Python\Python312\python.exe' tools\md_to_ppt_html.py examples\template.md dist\template.html`：通过，生成 `dist/template.html`。
- Chrome headless 首屏截图：通过，生成 `dist/template-cover.png`。
- Chrome headless 1920x1080 首屏截图：通过，生成 `dist/template-cover-1920.png`；页面铺满视口，未出现左右黑边。
- `node tools\verify_html_interaction.mjs file:///D:/codex/ppt-html/dist/template.html#4 dist/template-page4-after-key.png`：通过；第 4 页按一次右方向键后仍在第 4 页，visible fragment 从 0 变为 1，页码为 `4 / 15`。
- 用户级 PATH 写入验证：提权环境中 `python --version` 返回 `Python 3.12.10`，`where.exe python` 首项为 `C:\Users\zhugeheng\AppData\Local\Programs\Python\Python312\python.exe`。
- 地球背景最终修正验证：`python -m py_compile tools\md_to_ppt_html.py` 通过；`python tools\md_to_ppt_html.py examples\template.md dist\template.html` 通过；Chrome headless 1920x1080 截图已更新 `dist/template-cover-1920.png`；地球表现为右侧大背景，主体在屏幕外，仅露出大弧线和点阵。
- 最终交互复验：`node tools\verify_html_interaction.mjs file:///D:/codex/ppt-html/dist/template.html#4 dist/template-page4-after-key.png` 通过；第 4 页按一次右方向键后仍在第 4 页，visible fragment 从 0 变为 1。
- `bg.png` 背景接入验证：`bg.png` 尺寸为 `1672x941`，比例约 `1.777`；`python tools\md_to_ppt_html.py examples\template.md dist\template.html` 通过；Chrome headless 1920x1080 截图已更新 `dist/template-cover-1920.png`；方向键逐条显示复验通过。
- 点阵弱化验证：`python -m py_compile tools\md_to_ppt_html.py` 通过；`python tools\md_to_ppt_html.py examples\template.md dist\template.html` 通过；Chrome headless 1920x1080 截图已更新 `dist/template-cover-1920.png`；`node tools\verify_html_interaction.mjs file:///D:/codex/ppt-html/dist/template.html#4 dist/template-page4-after-key.png` 通过，visible fragment 从 0 变为 1。
- 矩阵卡片布局验证：`python -m py_compile tools\md_to_ppt_html.py` 通过；`python tools\md_to_ppt_html.py examples\template.md dist\template.html` 通过；生成页面总页数为 `17`；第 11 页 `matrix-count-2` 截图为 `dist/template-matrix-2.png`，第 12 页 `matrix-count-4` 截图为 `dist/template-matrix-4.png`；第 4 页逐条显示复验通过，visible fragment 从 0 变为 1。
- 分点版式细节验证：`python -m py_compile tools\md_to_ppt_html.py` 通过；`python tools\md_to_ppt_html.py examples\template.md dist\template.html` 通过；第 4 页自动 `matrix-feature` 截图为 `dist/template-matrix-auto-3.png`；第 7 页自动 `cards` 截图为 `dist/template-cards-auto-7.png`；第 11 页显式 `matrix-list` 截图为 `dist/template-matrix-2.png`；第 12 页显式 `matrix-feature` 截图为 `dist/template-matrix-4.png`；第 16 页自动 `cards` 截图为 `dist/template-cards-auto-16.png`；第 5 页引用页截图为 `dist/template-quote-5.png`。
- 标题上移验证：`python -m py_compile tools\md_to_ppt_html.py` 通过；`python tools\md_to_ppt_html.py examples\template.md dist\template.html` 通过；已更新 `dist/template-cover-1920.png`、`dist/template-cards-auto-7.png`、`dist/template-matrix-4.png`；截图确认标题整体更靠上，内容跟随标题下方且间距保持一致。
- 标题与引用页二次修正验证：`python -m py_compile tools\md_to_ppt_html.py` 通过；`python tools\md_to_ppt_html.py examples\template.md dist\template.html` 通过；`node tools\verify_html_interaction.mjs file:///D:/codex/ppt-html/dist/template.html#5 dist/template-quote-5.png 0` 通过；第 7 页和第 12 页截图已更新，确认大标题明显上移；第 5 页截图已更新，引用符号改为两个青绿色块状引号。
- 左上边距统一验证：`python -m py_compile tools\md_to_ppt_html.py` 通过；`python tools\md_to_ppt_html.py examples\template.md dist\template.html` 通过；`node tools\verify_html_interaction.mjs file:///D:/codex/ppt-html/dist/template.html#1 dist/template-cover-1920.png 0` 通过；第 5 页和第 7 页截图已更新，确认封面未裁切，普通内容页和引用页左边距与顶部边距一致。
- 全局 skill 封装验证：`python -m py_compile C:\Users\zhugeheng\.codex\skills\markdown-ppt-html\scripts\md_to_ppt_html.py` 通过。
- 全局 skill 生成验证：`python C:\Users\zhugeheng\.codex\skills\markdown-ppt-html\scripts\md_to_ppt_html.py C:\Users\zhugeheng\.codex\skills\markdown-ppt-html\assets\template.md dist\skill-template.html` 通过，生成 `dist/skill-template.html`。
- 全局 skill 结构核对：`SKILL.md` frontmatter、`agents/openai.yaml`、`assets/bg.png`、`assets/template.md`、`scripts/md_to_ppt_html.py`、`scripts/verify_html_interaction.mjs` 均已存在；`dist/skill-template.html` 中已生成 18 页并包含封面、目录、章节、矩阵、引用、卡片、时间线、图文页、对比表格页和块状引用符号。
- `quick_validate.py` 已尝试运行，但当前 Python 环境缺少 `yaml` 模块导致中断；未擅自安装 PyYAML，已用编译、生成和结构核对完成替代验证。
- 实时编辑器静态核对：`rg -n "downloadHtml|下载 HTML|Blob|markdown-ppt-preview.html" tools\live_editor.html` 确认右上角下载按钮、Blob 下载逻辑和默认下载文件名存在。
- 实时编辑器脚本语法验证：提取 `tools/live_editor.html` 内联 `<script>` 并用 Node `new Function(script)` 编译通过；确认 `downloadHtml`、`preview` iframe、`editor` textarea、Blob 下载逻辑和下载文件名均存在。
- 实时编辑器模拟生成验证：Node VM 执行 `tools/live_editor.html` 内联脚本后生成 17 页 iframe HTML，确认包含正式 `agenda`、`matrix-wrap`、`point-card`、`#controls`、`#progress`，且不再包含旧的 `agenda-list` 和 `pager` 临时结构；预览缩放变量计算为 `0.5`。
- 实时编辑器浏览器截图验证：headless Chrome 使用独立用户目录打开 `file:///D:/codex/ppt-html/tools/live_editor.html` 通过，输出 `dist/live-editor.png`；检测结果为下载按钮文本 `⇩ 下载 HTML`，iframe CSS 尺寸 `1920px x 1080px`，缩放比例 `0.3962962962962963`，生成 17 页，目录项可见，`#controls` 和 `#progress` 存在。
- 实时编辑器封面初始定位验证：Node VM 模拟执行确认光标在顶部时 `slidePageForCursor` 返回 `1`，iframe 初始页索引为 `0`，第 1 页为 `cover`，第 2 页为合成 `agenda`；headless Chrome 真实打开 `tools/live_editor.html` 后检测 `previewMeta` 为 `1 / 17`，iframe active page 为 `1`，active layout 为 `slide layout-cover active`，标题为 `从你天天用的产品里找金矿`。
- 实时编辑器本地保存验证：内联 JS 语法校验通过；headless Chrome 真实打开 `tools/live_editor.html`，写入测试 Markdown，触发输入和 `保存 Markdown`，刷新页面后检测 `editor.value` 与保存内容一致，结果 `restored: true`。
- 实时编辑器保存提示验证：内联 JS 语法校验通过；headless Chrome 真实点击 `保存 Markdown` 后检测 `saveToast.textContent` 为 `Markdown 已保存成功`，`saveToast` 包含 `show` 状态，`syncText` 为 `Markdown 已保存`。
- 实时编辑器滚动条样式验证：内联 JS 语法校验通过；headless Chrome 检测左侧 textarea `scrollbar-width` 为 `thin`，`scrollbar-color` 为青绿色/深色组合，WebKit 滚动条宽度为 `10px`，轨道和滑块均使用非白色背景，滚动角样式规则存在。
- 实时编辑器预览分点直显验证：Node VM 模拟执行确认 `previewHtml` 为 `data-preview-mode="true"`，`currentHtml` 不含预览模式且包含逐条显示 gate；headless Chrome 切到右侧预览第 4 页后检测 `bodyPreviewMode` 为 `true`，`fragmentCount` 为 `3`，`visibleCount` 为 `3`，首个分点透明度为 `1`，同时导出 HTML 检测 `exportPreviewMode: false`、`exportStepReveal: true`。
- 对比表格版式验证：`python -m py_compile tools\md_to_ppt_html.py` 通过；`python tools\md_to_ppt_html.py examples\template.md dist\template.html` 通过；生成 HTML 总页数为 `18`，第 13 页为 `layout-compare_table`，包含 `compare-table-wrap`、`AGENTS.md`、`CLAUDE.md` 和 6 个 `<tr>`；headless Chrome 截图 `dist/template-compare-table-13.png` 通过，页码为 `13 / 18`；实时编辑器 Node VM 验证生成 18 页且包含 1 个 `compare_table` 页面。
- 全局 skill 表格版式验证：`python -m py_compile C:\Users\zhugeheng\.codex\skills\markdown-ppt-html\scripts\md_to_ppt_html.py` 通过；`python C:\Users\zhugeheng\.codex\skills\markdown-ppt-html\scripts\md_to_ppt_html.py C:\Users\zhugeheng\.codex\skills\markdown-ppt-html\assets\template.md dist\skill-template.html` 通过；`dist/skill-template.html` 总页数为 `18`，包含 1 个 `layout-compare_table` 页面和 `AGENTS.md` 表格内容。
- 状态清单表格版式验证：`python -m py_compile tools\md_to_ppt_html.py` 通过；`python tools\md_to_ppt_html.py examples\template.md dist\template.html` 通过；`dist/template.html` 总页数为 `19`，包含 1 个 `layout-status_list` 页面、1 个 `layout-compare_table` 页面和 6 个 `status-item`；headless Chrome 截图 `dist/template-status-list-14.png` 通过，页码为 `14 / 19`；实时编辑器 Node VM 验证生成 19 页且包含 1 个 `status_list` 页面；全局 skill 生成的 `dist/skill-template.html` 同样包含 1 个 `layout-status_list` 页面和 6 个状态项。
- 分点标题长文本换行验证：新增 `examples/wrap-test.md`；`python -m py_compile tools\md_to_ppt_html.py` 通过；`python tools\md_to_ppt_html.py examples\wrap-test.md dist\wrap-test.html` 通过；headless Chrome 检测第 2 页第 3 个标题 `titleHeight` 为 `120`、`wraps: true`、`overflowRight: false`、`overflowWrap: anywhere`、`wordBreak: break-word`，截图输出 `dist/wrap-test-page2.png`；针对 `tools/live_editor.html` 再次真实注入用户截图同类内容验证，活动预览页第 3 个标题 `h3Height` 为 `80`、`wraps: true`、`overflowRight: false`、`lineBreak: anywhere`、grid 列为 `76.7969px 822.406px`；全局 skill 脚本 `python -m py_compile C:\Users\zhugeheng\.codex\skills\markdown-ppt-html\scripts\md_to_ppt_html.py` 通过。
- 用户原文列表拆分验证：`examples/wrap-test.md` 已使用 `3. **魔法选手 —— Claude Code/Codex+自家模型**：适合复杂项目、产品规划和大型项目编码`；UTF-8 文件内容注入 `tools/live_editor.html` 后，headless Chrome 检测第 3 条 `hasP: true`，`h3Text` 为 `魔法选手 —— Claude Code/Codex+自家模型`，`pText` 为 `适合复杂项目、产品规划和大型项目编码`，且 `h3OverflowRight: false`、`pOverflowRight: false`；`dist/wrap-test.html` 中确认生成 `<h3>魔法选手 —— Claude Code/Codex+自家模型</h3>` 和 `<p>适合复杂项目、产品规划和大型项目编码</p>`；全局 skill 脚本语法验证通过。
- 实时编辑器按钮精简验证：内联 JS 语法校验通过；静态检查确认 `loadFile`、`restoreTemplate`、`fileInput` 已不存在，`saveMarkdown` 和 `downloadHtml` 仍存在。
- 数字分点圆圈修复验证：`python -m py_compile tools\md_to_ppt_html.py` 通过；`python tools\md_to_ppt_html.py examples\wrap-test.md dist\wrap-test.html` 和 `python tools\md_to_ppt_html.py examples\template.md dist\template.html` 通过；headless Chrome 测量 `dist/wrap-test.html#2` 与 `dist/template.html#9` 的 3 个 `.timeline span` 均为 `62.39 x 62.39`、`delta: 0`、`borderRadius: 50%`；实时编辑器右侧 iframe 第 9 页同样为 `62.39 x 62.39`、`delta: 0`；全局 skill 脚本 `python -m py_compile C:\Users\zhugeheng\.codex\skills\markdown-ppt-html\scripts\md_to_ppt_html.py` 通过。
- 反引号强调样式扩展验证：`python -m py_compile tools\md_to_ppt_html.py` 通过；`python tools\md_to_ppt_html.py examples\wrap-test.md dist\wrap-test.html` 和 `python tools\md_to_ppt_html.py examples\template.md dist\template.html` 通过；`dist/wrap-test.html` 确认非表格时间线标题生成 `<code>WorkBuddy</code>`、说明生成 `<code>脚本</code>`；headless Chrome 实测两处 `code` 均为 `inline-block`、橙色文字、半透明橙色背景和边框；实时编辑器右侧 iframe 注入同一 Markdown 后得到相同计算样式；全局 skill 脚本编译通过，并生成 `dist/skill-wrap-test.html`，确认同样包含非表格 `<code>` 输出。
- 章节页标题宽度修复验证：新增 `examples/section-width-test.md` 覆盖 `## 01 AI 的发展及现状`；`python -m py_compile tools\md_to_ppt_html.py` 通过；`python tools\md_to_ppt_html.py examples\section-width-test.md dist\section-width-test.html` 和 `python tools\md_to_ppt_html.py examples\template.md dist\template.html` 通过；headless Chrome 实测 `dist/section-width-test.html#3` 中标题 `AI 的发展及现状` 为 1 行，章节容器宽度约 `1772.8px`，标题可用宽度 `1312px`；实时编辑器右侧 iframe 注入同一 Markdown 后第 3 页同样为 1 行；全局 skill 脚本编译通过，并生成 `dist/skill-section-width-test.html`，确认包含同样的章节标题宽度 CSS。
- 最终符号化分点样式验证：`examples/symbol-style-test.md` 已改为 `[]`、`·`、`::` 和数字列表；`python -m py_compile tools\md_to_ppt_html.py` 通过；`python tools\md_to_ppt_html.py examples\symbol-style-test.md dist\symbol-style-test.html` 和 `python tools\md_to_ppt_html.py examples\template.md dist\template.html` 通过；`dist/symbol-style-test.html` 确认 `[]` 生成 `layout-matrix` + `matrix-style-feature`，`·` 生成 `layout-cards`，`::` 生成 `layout-matrix` + `matrix-style-list`，数字列表生成 `layout-timeline`；实时编辑器右侧 iframe 注入同一 Markdown 后得到相同页面结构；全局 skill 脚本编译通过，并生成 `dist/skill-symbol-style-test.html`；源文件、模板、README、ROADMAP 和全局 skill 中均确认不再包含临时旧符号。
- `::` 1x3 布局宽度验证：`examples/symbol-style-test.md` 的 `::` 页已扩展为 3 项以覆盖 1x3 场景；`python -m py_compile tools\md_to_ppt_html.py` 通过；`python tools\md_to_ppt_html.py examples\symbol-style-test.md dist\symbol-style-test.html` 和 `python tools\md_to_ppt_html.py examples\template.md dist\template.html` 通过；headless Chrome 实测 `dist/symbol-style-test.html#4` 中 `matrix-style-list matrix-count-3` 网格宽度为 `1772.8px`，列宽约 `576.53px`，列间距 `21.6px`，单卡左内边距 `32px`；实时编辑器右侧 iframe 注入同一 Markdown 后得到相同测量结果；全局 skill 脚本编译通过，并生成 `dist/skill-symbol-style-test.html`。
- PPT 式导航交互验证：`python -m py_compile tools\md_to_ppt_html.py` 通过；`python tools\md_to_ppt_html.py examples\template.md dist\template.html` 通过；实时编辑器内联 JS 语法校验通过并确认包含 `ArrowDown`、`ArrowUp`、页面单击监听和按钮 `stopPropagation`；headless Chrome 实测 `dist/template.html#4` 中 `ArrowDown` 使 visible fragment 从 0 到 1，页面空白单击从 1 到 2，`ArrowUp` 回退到 1；另测 `dist/template.html#1` 中页面单击从第 1 页跳到第 2 页，`ArrowUp` 回到第 1 页，`ArrowDown` 到第 2 页；全局 skill 脚本编译通过，并生成 `dist/skill-template.html`。
