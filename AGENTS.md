# ppt-html Project Rules

## Scope

This project builds a local Markdown-to-PPT-style-HTML converter.

## Directory Layout

- `raw/`: reference screenshots only. Do not modify these files.
- `assets/`: reusable visual assets extracted or created for the deck theme.
- `tools/`: source code for conversion tools.
- `examples/`: input Markdown templates and examples.
- `dist/`: generated HTML output. Files here may be regenerated.
- `README.md`: user-facing usage instructions.
- `ROADMAP.md`: current project progress and verification record.

## Naming

- Python scripts use lowercase words joined by underscores.
- Example Markdown files use lowercase words joined by hyphens.
- Generated HTML files should match the input Markdown basename.

## Implementation Rules

- Keep the converter dependency-free unless a dependency is explicitly justified.
- Generated HTML should be standalone: embedded CSS and JavaScript, no CDN dependency.
- Markdown parsing should prefer simple predictable rules over broad Markdown compatibility.
- Do not modify `raw/` screenshots.
- Do not add unrelated refactors or features.

## Verification

Run this after code changes:

```powershell
python tools/md_to_ppt_html.py examples/template.md dist/template.html
```

For syntax validation:

```powershell
python -m py_compile tools/md_to_ppt_html.py
```

If `python` is not on PATH, use the installed interpreter path directly, for example:

```powershell
& 'C:\Users\zhugeheng\AppData\Local\Programs\Python\Python312\python.exe' -m py_compile tools\md_to_ppt_html.py
```

For browser interaction validation:

```powershell
node tools\verify_html_interaction.mjs file:///D:/codex/ppt-html/dist/template.html#4 dist/template-page4-after-key.png
```

Open `dist/template.html` in a browser and check:

- Page navigation with left/right arrow keys.
- Bullet reveal behavior before advancing pages.
- Bottom progress bar.
- Bottom-right page number and navigation arrows.
- Layouts for cover, agenda, section, matrix cards, stacked cards, quote, timeline, and image/text pages.
