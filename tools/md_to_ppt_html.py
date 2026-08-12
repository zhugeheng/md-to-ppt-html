#!/usr/bin/env python3
"""Convert a small Markdown deck into standalone PPT-style HTML."""

from __future__ import annotations

import argparse
import base64
import html
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Block:
    type: str
    text: str = ""
    items: list[dict[str, str]] = field(default_factory=list)
    point_style: str = ""
    alt: str = ""
    src: str = ""
    headers: list[str] = field(default_factory=list)
    rows: list[list[str]] = field(default_factory=list)


@dataclass
class Slide:
    title: str
    level: int = 2
    raw_lines: list[str] = field(default_factory=list)
    layout: str = "content"
    point_style: str = "auto"
    point_style_explicit: bool = False
    blocks: list[Block] = field(default_factory=list)
    agenda_items: list[str] = field(default_factory=list)


@dataclass
class ExportOptions:
    show_agenda: bool = True
    step_reveal: bool = True


POINT_MARKER_STYLES = {
    "[]": "matrix-feature",
    "·": "cards",
    "::": "matrix-list",
}
POINT_MARKER_RE = re.compile(r"^\s*(\[\]|·|::)\s+(.+)$")
SPECIAL_RE = re.compile(r"^(#{1,6}\s+|[-*]\s+|\d+\.\s+|(?:\[\]|·|::)\s+|>\s?|\||!\[[^\]]*\]\([^)]+\)|<!--\s*point-style\s*:)")
POINT_STYLE_RE = re.compile(r"^\s*<!--\s*point-style\s*:\s*([a-zA-Z0-9_-]+)\s*-->\s*$")
POINT_STYLE_ALIASES = {
    "auto": "auto",
    "stacked": "cards",
    "cards": "cards",
    "card": "cards",
    "matrix": "matrix",
    "grid": "matrix",
    "matrix-list": "matrix-list",
    "list": "matrix-list",
    "compare": "matrix-list",
    "matrix-feature": "matrix-feature",
    "feature": "matrix-feature",
}

FRONTMATTER_ALIASES = {
    "agenda": "show_agenda",
    "show_agenda": "show_agenda",
    "show-agenda": "show_agenda",
    "step_reveal": "step_reveal",
    "step-reveal": "step_reveal",
    "stepReveal": "step_reveal",
}


def parse_bool(value: str) -> bool | None:
    normalized = value.strip().strip("\"'").lower()
    if normalized in {"true", "yes", "y", "1", "on"}:
        return True
    if normalized in {"false", "no", "n", "0", "off"}:
        return False
    return None


def split_frontmatter(source: str) -> tuple[dict[str, bool], str]:
    lines = source.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    if not lines or lines[0].strip() != "---":
        return {}, source

    end = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end = index
            break
    if end is None:
        return {}, source

    values: dict[str, bool] = {}
    for line in lines[1:end]:
        match = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.+?)\s*$", line)
        if not match:
            continue
        key = FRONTMATTER_ALIASES.get(match.group(1).strip())
        parsed = parse_bool(match.group(2))
        if key and parsed is not None:
            values[key] = parsed
    return values, "\n".join(lines[end + 1 :])


def merge_options(frontmatter: dict[str, bool], agenda: bool | None = None, step_reveal: bool | None = None) -> ExportOptions:
    options = ExportOptions()
    if "show_agenda" in frontmatter:
        options.show_agenda = frontmatter["show_agenda"]
    if "step_reveal" in frontmatter:
        options.step_reveal = frontmatter["step_reveal"]
    if agenda is not None:
        options.show_agenda = agenda
    if step_reveal is not None:
        options.step_reveal = step_reveal
    return options


def inline_md(text: str) -> str:
    escaped = html.escape(text.strip())
    escaped = re.sub(r"(`+)([^`]+)\1", r"<code>\2</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", escaped)
    escaped = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: f'<a href="{html.escape(m.group(2), quote=True)}">{m.group(1)}</a>',
        escaped,
    )
    return escaped


def clean_markup(text: str) -> str:
    return re.sub(r"[*_`]+", "", text).strip()


def split_title_detail(text: str) -> dict[str, str]:
    raw = text.strip()
    match = re.match(r"^(.+?)[：:]\s*(.+)$", raw)
    if match:
        return {"title": match.group(1).strip(), "detail": match.group(2).strip()}
    return {"title": raw, "detail": ""}


def list_item_count(slide: Slide, block_type: str = "bullet_list") -> int:
    return sum(len(block.items) for block in slide.blocks if block.type == block_type)


def split_detail_points(detail: str) -> list[str]:
    if not detail:
        return []
    points = [part.strip() for part in re.split(r"\s*[；;｜|]\s*", detail) if part.strip()]
    return points if len(points) > 1 else []


def split_table_row(line: str) -> list[str]:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [cell.strip() for cell in stripped.split("|")]


def is_table_separator(line: str) -> bool:
    cells = split_table_row(line)
    if not cells:
        return False
    return all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def is_table_start(lines: list[str], index: int) -> bool:
    if index + 1 >= len(lines):
        return False
    return lines[index].strip().startswith("|") and is_table_separator(lines[index + 1])


def parse_status_marker(text: str) -> tuple[str, str] | None:
    stripped = clean_markup(text)
    match = re.match(r"^(✓|✔|✅|✗|×|✕|❌)\s*(.*)$", stripped)
    if not match:
        return None
    marker = match.group(1)
    state = "no" if marker in {"✗", "×", "✕", "❌"} else "ok"
    return state, match.group(2).strip()


def is_status_table(block: Block) -> bool:
    if len(block.headers) != 2 or not block.rows:
        return False
    first_header = clean_markup(block.headers[0])
    if not re.search(r"(状态|支持|是否|有无|可用|结果)", first_header):
        return False
    return all(row and parse_status_marker(row[0]) is not None for row in block.rows)


def extract_slide_options(slide: Slide) -> None:
    kept_lines = []
    for line in slide.raw_lines:
        match = POINT_STYLE_RE.match(line)
        if match:
            requested = match.group(1).strip().lower()
            slide.point_style = POINT_STYLE_ALIASES.get(requested, "auto")
            slide.point_style_explicit = requested in POINT_STYLE_ALIASES and slide.point_style != "auto"
            continue
        kept_lines.append(line)
    slide.raw_lines = kept_lines


def bullet_items(slide: Slide) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for block in slide.blocks:
        if block.type == "bullet_list":
            items.extend(block.items)
    return items


def apply_point_marker_style(slide: Slide) -> None:
    for block in slide.blocks:
        if block.type == "bullet_list" and block.point_style:
            slide.point_style = block.point_style
            slide.point_style_explicit = True
            return


def inferred_matrix_style(slide: Slide) -> str:
    items = bullet_items(slide)
    has_detail_points = any(split_detail_points(item["detail"]) for item in items)
    return "matrix-list" if has_detail_points else "matrix-feature"


def choose_auto_point_styles(slides: list[Slide]) -> None:
    used_counts = {"cards": 0, "matrix-list": 0, "matrix-feature": 0}
    previous_style = ""

    for slide in slides:
        if slide.layout not in {"cards", "matrix"}:
            continue

        if slide.point_style_explicit:
            resolved = inferred_matrix_style(slide) if slide.point_style == "matrix" else slide.point_style
            if resolved in used_counts:
                used_counts[resolved] += 1
                previous_style = resolved
            continue

        item_count = list_item_count(slide)
        if item_count < 2 or item_count > 6:
            slide.point_style = "cards"
            slide.layout = "cards"
            used_counts["cards"] += 1
            previous_style = "cards"
            continue

        preferred = inferred_matrix_style(slide)
        alternate = "matrix-feature" if preferred == "matrix-list" else "matrix-list"
        candidates = [preferred, "cards", alternate]
        if item_count >= 5:
            candidates = [preferred, alternate, "cards"]

        def score(style: str) -> float:
            value = used_counts[style] * 0.4
            if style == previous_style:
                value += 1.4
            if style == preferred:
                value += 0
            elif style == "cards":
                value += 0.35
            else:
                value += 0.75
            return value

        selected = min(candidates, key=score)
        slide.point_style = selected
        slide.layout = "cards" if selected == "cards" else "matrix"
        used_counts[selected] += 1
        previous_style = selected


def parse_markdown(source: str, options: ExportOptions | None = None) -> list[Slide]:
    options = options or ExportOptions()
    slides: list[Slide] = []
    current: Slide | None = None

    def finish() -> None:
        nonlocal current
        if current is not None:
            current.raw_lines = trim_blank_edges(current.raw_lines)
            extract_slide_options(current)
            current.blocks = parse_blocks(current.raw_lines)
            apply_point_marker_style(current)
            slides.append(current)
            current = None

    for line in source.splitlines():
        heading = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if heading and len(heading.group(1)) <= 2:
            finish()
            current = Slide(title=heading.group(2).strip(), level=len(heading.group(1)))
            continue

        if line.strip() == "---":
            finish()
            continue

        if current is None and line.strip():
            current = Slide(title="", level=2)
        if current is not None:
            current.raw_lines.append(line.rstrip())

    finish()
    classify_slides(slides)
    choose_auto_point_styles(slides)
    return add_agenda(slides) if options.show_agenda else slides


def trim_blank_edges(lines: list[str]) -> list[str]:
    start = 0
    end = len(lines)
    while start < end and not lines[start].strip():
        start += 1
    while end > start and not lines[end - 1].strip():
        end -= 1
    return lines[start:end]


def parse_blocks(lines: list[str]) -> list[Block]:
    blocks: list[Block] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            i += 1
            continue

        if stripped.startswith("### "):
            blocks.append(Block("subheading", text=stripped[4:].strip()))
            i += 1
            continue

        if is_table_start(lines, i):
            headers = split_table_row(lines[i])
            i += 2
            rows: list[list[str]] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                row = split_table_row(lines[i])
                if len(row) < len(headers):
                    row.extend([""] * (len(headers) - len(row)))
                rows.append(row[: len(headers)])
                i += 1
            blocks.append(Block("table", headers=headers, rows=rows))
            continue

        image = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", stripped)
        if image:
            blocks.append(Block("image", alt=image.group(1), src=image.group(2)))
            i += 1
            continue

        if stripped.startswith(">"):
            collected: list[str] = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                collected.append(lines[i].strip().lstrip(">").strip())
                i += 1
            blocks.append(Block("quote", text=" ".join(collected)))
            continue

        point_marker = POINT_MARKER_RE.match(stripped)
        if point_marker:
            items: list[dict[str, str]] = []
            point_style = POINT_MARKER_STYLES[point_marker.group(1)]
            while i < len(lines):
                marker_match = POINT_MARKER_RE.match(lines[i].strip())
                if not marker_match:
                    break
                items.append(split_title_detail(marker_match.group(2).strip()))
                i += 1
            blocks.append(Block("bullet_list", items=items, point_style=point_style))
            continue

        if re.match(r"^[-*]\s+", stripped):
            items: list[dict[str, str]] = []
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                item = re.sub(r"^\s*[-*]\s+", "", lines[i]).strip()
                items.append(split_title_detail(item))
                i += 1
            blocks.append(Block("bullet_list", items=items))
            continue

        if re.match(r"^\d+\.\s+", stripped):
            items = []
            while i < len(lines) and re.match(r"^\s*\d+\.\s+", lines[i]):
                item = re.sub(r"^\s*\d+\.\s+", "", lines[i]).strip()
                items.append(split_title_detail(item))
                i += 1
            blocks.append(Block("ordered_list", items=items))
            continue

        para: list[str] = []
        while i < len(lines):
            next_line = lines[i].strip()
            if not next_line:
                break
            if para and SPECIAL_RE.match(next_line):
                break
            para.append(next_line)
            i += 1
        blocks.append(Block("paragraph", text=" ".join(para)))

    return blocks


def classify_slides(slides: list[Slide]) -> None:
    for slide in slides:
        if slide.level == 1:
            slide.layout = "cover"
            continue

        block_types = [block.type for block in slide.blocks]
        has_text = any(
            block.text or block.items or block.src or block.headers or block.rows
            for block in slide.blocks
            if block.type != "subheading"
        )

        if not has_text:
            slide.layout = "section"
        elif "table" in block_types:
            table = next((block for block in slide.blocks if block.type == "table"), None)
            slide.layout = "status_list" if table is not None and is_status_table(table) else "compare_table"
        elif "image" in block_types:
            slide.layout = "image_text"
        elif "ordered_list" in block_types:
            slide.layout = "timeline"
        elif "quote" in block_types:
            slide.layout = "quote"
        elif "bullet_list" in block_types:
            item_count = list_item_count(slide)
            if slide.point_style == "cards":
                slide.layout = "cards"
            elif slide.point_style.startswith("matrix") and 2 <= item_count <= 6:
                slide.layout = "matrix"
            else:
                slide.layout = "matrix" if 2 <= item_count <= 6 else "cards"
        else:
            word_count = len("".join(block.text for block in slide.blocks))
            slide.layout = "statement" if word_count <= 90 else "content"


def add_agenda(slides: list[Slide]) -> list[Slide]:
    if not slides:
        return slides

    sections = [slide.title for slide in slides if slide.layout == "section"]
    if not sections:
        return slides

    agenda = Slide(title="目录", layout="agenda", agenda_items=sections)
    if slides[0].layout == "cover":
        return [slides[0], agenda, *slides[1:]]
    return [agenda, *slides]


def render_deck(slides: list[Slide], title: str, options: ExportOptions | None = None) -> str:
    options = options or ExportOptions()
    slide_html = "\n".join(render_slide(slide, index + 1, len(slides)) for index, slide in enumerate(slides))
    result = HTML_TEMPLATE
    result = result.replace("__TITLE__", html.escape(title))
    result = result.replace("__SLIDES__", slide_html)
    result = result.replace("__TOTAL__", str(len(slides)))
    result = result.replace("__DECK_BG__", deck_background_data_uri())
    result = result.replace("__STEP_REVEAL__", "true" if options.step_reveal else "false")
    return result


def render_slide(slide: Slide, page: int, total: int) -> str:
    content = {
        "cover": render_cover,
        "agenda": render_agenda,
        "section": render_section,
        "cards": render_cards,
        "matrix": render_matrix,
        "quote": render_quote,
        "timeline": render_timeline,
        "image_text": render_image_text,
        "compare_table": render_compare_table,
        "status_list": render_status_list,
        "statement": render_statement,
        "content": render_content,
    }[slide.layout](slide)

    return f"""<section class="slide layout-{slide.layout}" data-page="{page}" data-total="{total}">
  <div class="slide-bg"></div>
  <div class="slide-inner">
{content}
  </div>
</section>"""


def render_cover(slide: Slide) -> str:
    paragraphs = [block.text for block in slide.blocks if block.type == "paragraph"]
    subtitle = paragraphs[0] if paragraphs else "Markdown to HTML Presentation"
    kicker = paragraphs[1] if len(paragraphs) > 1 else "AI Learning Path · Practice"
    return f"""    <div class="cover-copy">
      <p class="kicker">{inline_md(kicker)}</p>
      <h1>{inline_md(slide.title)}</h1>
      <p class="subtitle">{inline_md(subtitle)}</p>
    </div>
    <div class="brand-mark">ppt-html</div>"""


def render_agenda(slide: Slide) -> str:
    rows = []
    for index, item in enumerate(slide.agenda_items, 1):
        number, text = split_section_number(item, index)
        rows.append(f"""      <li>
        <span>{number}</span>
        <strong>{inline_md(text)}</strong>
      </li>""")
    return f"""    <div class="agenda">
      <h2>{inline_md(slide.title)}</h2>
      <ol>
{chr(10).join(rows)}
      </ol>
    </div>"""


def render_section(slide: Slide) -> str:
    number, text = split_section_number(slide.title, 1)
    return f"""    <div class="section-title">
      <div class="section-number">{number}</div>
      <h2>{inline_md(text)}</h2>
    </div>"""


def render_cards(slide: Slide) -> str:
    cards = []
    for block in slide.blocks:
        if block.type != "bullet_list":
            continue
        for item in block.items:
            cards.append(f"""      <article class="point-card fragment">
        <span class="dot"></span>
        <div>
          <h3>{inline_md(item["title"])}</h3>
          {f'<p>{inline_md(item["detail"])}</p>' if item["detail"] else ""}
        </div>
      </article>""")
    return f"""    <div class="content-stack">
      <h2>{inline_md(slide.title)}</h2>
      <div class="card-list">
{chr(10).join(cards)}
      </div>
    </div>"""


def render_matrix(slide: Slide) -> str:
    items: list[dict[str, str]] = []
    for block in slide.blocks:
        if block.type == "bullet_list":
            items.extend(block.items)

    count = len(items)
    has_detail_points = any(split_detail_points(item["detail"]) for item in items)
    if slide.point_style == "matrix-list":
        style = "list"
    elif slide.point_style == "matrix-feature":
        style = "feature"
    else:
        style = "list" if has_detail_points else "feature"
    cards = []

    for index, item in enumerate(items):
        points = split_detail_points(item["detail"])
        if points:
            detail_html = "<ul>" + "".join(f"<li>{inline_md(point)}</li>" for point in points) + "</ul>"
        elif item["detail"]:
            detail_html = f"<p>{inline_md(item['detail'])}</p>"
        else:
            detail_html = ""

        emphasis = " is-emphasis" if style == "list" and index == 1 else ""
        cards.append(f"""      <article class="matrix-card{emphasis} fragment">
        <span class="matrix-icon"></span>
        <h3>{inline_md(item["title"])}</h3>
        {detail_html}
      </article>""")

    return f"""    <div class="matrix-wrap matrix-style-{style}">
      <h2>{inline_md(slide.title)}</h2>
      <div class="matrix-grid matrix-count-{count}">
{chr(10).join(cards)}
      </div>
    </div>"""


def render_quote(slide: Slide) -> str:
    quote = next((block.text for block in slide.blocks if block.type == "quote"), "")
    paragraphs = [block.text for block in slide.blocks if block.type == "paragraph"]
    caption = paragraphs[0] if paragraphs else slide.title
    return f"""    <figure class="quote-block">
      <div class="quote-mark" aria-hidden="true"><span></span><span></span></div>
      <blockquote>{inline_md(quote)}</blockquote>
      <figcaption>- {inline_md(caption)}</figcaption>
    </figure>"""


def render_timeline(slide: Slide) -> str:
    items: list[dict[str, str]] = []
    for block in slide.blocks:
        if block.type == "ordered_list":
            items.extend(block.items)

    rows = []
    for index, item in enumerate(items, 1):
        rows.append(f"""      <li class="fragment">
        <span>{index}</span>
        <div>
          <h3>{inline_md(item["title"])}</h3>
          {f'<p>{inline_md(item["detail"])}</p>' if item["detail"] else ""}
        </div>
      </li>""")
    return f"""    <div class="timeline">
      <h2>{inline_md(slide.title)}</h2>
      <ol>
{chr(10).join(rows)}
      </ol>
    </div>"""


def render_image_text(slide: Slide) -> str:
    image = next((block for block in slide.blocks if block.type == "image"), None)
    text_blocks = [block for block in slide.blocks if block.type != "image"]
    text_html = render_plain_blocks(text_blocks)
    image_html = ""
    if image is not None:
        src = html.escape(image.src, quote=True)
        alt = html.escape(image.alt, quote=True)
        image_html = f'<img src="{src}" alt="{alt}">'

    return f"""    <div class="image-text">
      <div class="image-copy">
        <h2>{inline_md(slide.title)}</h2>
{text_html}
      </div>
      <figure class="image-frame">
        {image_html}
      </figure>
    </div>"""


def render_compare_table(slide: Slide) -> str:
    table = next((block for block in slide.blocks if block.type == "table"), None)
    if table is None:
        return render_content(slide)

    headers = table.headers
    rows = table.rows
    head_html = "".join(f"<th>{inline_md(header)}</th>" for header in headers)
    body_rows = []
    for row in rows:
        cells = []
        for index, cell in enumerate(row):
            tag = "th" if index == 0 else "td"
            scope = ' scope="row"' if index == 0 else ""
            cells.append(f"<{tag}{scope}>{render_status_cell(cell)}</{tag}>")
        body_rows.append(f"        <tr>{''.join(cells)}</tr>")

    return f"""    <div class="compare-table-wrap">
      <h2>{inline_md(slide.title)}</h2>
      <div class="compare-table-frame">
        <table class="compare-table">
          <thead>
            <tr>{head_html}</tr>
          </thead>
          <tbody>
{chr(10).join(body_rows)}
          </tbody>
        </table>
      </div>
    </div>"""


def render_status_cell(text: str) -> str:
    status = parse_status_marker(text)
    if status is None:
        return inline_md(text)
    state, label = status
    icon = "✓" if state == "ok" else "×"
    content = inline_md(label) if label else ("支持" if state == "ok" else "不支持")
    return f'<span class="status-cell status-{state}"><span class="status-icon">{icon}</span><span>{content}</span></span>'


def render_status_list(slide: Slide) -> str:
    table = next((block for block in slide.blocks if block.type == "table"), None)
    if table is None:
        return render_content(slide)

    items = []
    for row in table.rows:
        status = parse_status_marker(row[0])
        if status is None:
            continue
        state, marker_text = status
        label = row[1] if len(row) > 1 and row[1] else marker_text
        icon = "✓" if state == "ok" else "×"
        items.append(f"""        <li class="status-item status-{state}">
          <span class="status-icon">{icon}</span>
          <span>{inline_md(label)}</span>
        </li>""")

    return f"""    <div class="status-list-wrap">
      <h2>{inline_md(slide.title)}</h2>
      <ul class="status-list">
{chr(10).join(items)}
      </ul>
    </div>"""


def render_statement(slide: Slide) -> str:
    return f"""    <div class="statement">
      <h2>{inline_md(slide.title)}</h2>
{render_plain_blocks(slide.blocks)}
    </div>"""


def render_content(slide: Slide) -> str:
    return f"""    <div class="content-stack">
      <h2>{inline_md(slide.title)}</h2>
{render_plain_blocks(slide.blocks)}
    </div>"""


def render_plain_blocks(blocks: list[Block]) -> str:
    html_parts: list[str] = []
    for block in blocks:
        if block.type == "paragraph":
            html_parts.append(f"      <p>{inline_md(block.text)}</p>")
        elif block.type == "subheading":
            html_parts.append(f"      <h3>{inline_md(block.text)}</h3>")
        elif block.type in {"bullet_list", "ordered_list"}:
            tag = "ol" if block.type == "ordered_list" else "ul"
            items = "".join(f"<li>{inline_md(item['title'])}</li>" for item in block.items)
            html_parts.append(f"      <{tag}>{items}</{tag}>")
        elif block.type == "table":
            html_parts.append("      <p>表格内容请使用对比表格版式查看。</p>")
        elif block.type == "quote":
            html_parts.append(f"      <blockquote>{inline_md(block.text)}</blockquote>")
    return "\n".join(html_parts)


def split_section_number(title: str, fallback: int) -> tuple[str, str]:
    cleaned = clean_markup(title)
    match = re.match(r"^(\d{1,2})[\s.、-]*(.+)$", cleaned)
    if match:
        return match.group(1).zfill(2), match.group(2).strip()
    return str(fallback).zfill(2), cleaned


def deck_background_data_uri() -> str:
    project_root = Path(__file__).resolve().parents[1]
    asset_path = project_root / "assets" / "bg.png"
    if not asset_path.exists():
        return ""
    encoded = base64.b64encode(asset_path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


HTML_TEMPLATE = r"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>__TITLE__</title>
  <style>
    :root {
      --bg: #050711;
      --panel: rgba(22, 27, 52, 0.72);
      --panel-strong: rgba(29, 36, 68, 0.9);
      --line: rgba(123, 255, 235, 0.13);
      --text: #f5f7fb;
      --muted: #9ea5bb;
      --body-muted: rgba(190, 196, 216, 0.72);
      --accent: #52ffe5;
      --accent-soft: rgba(82, 255, 229, 0.18);
      --shadow: rgba(0, 0, 0, 0.38);
      --deck-bg: url("__DECK_BG__");
      --edge-offset: 4.6rem;
      --title-offset: 0;
      --title-gap: 3rem;
    }

    * { box-sizing: border-box; }

    html, body {
      width: 100%;
      height: 100%;
      margin: 0;
      overflow: hidden;
      background: var(--bg);
      color: var(--text);
      font-family: "Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", sans-serif;
      -webkit-user-select: none;
      user-select: none;
    }

    body {
      min-width: 100vw;
      min-height: 100vh;
    }

    #deck {
      position: relative;
      width: 100vw;
      height: 100vh;
      overflow: hidden;
      background: var(--bg);
    }

    .slide {
      position: absolute;
      inset: 0;
      display: none;
      overflow: hidden;
    }

    .slide.active {
      display: block;
    }

    .slide-bg {
      position: absolute;
      inset: 0;
      background:
        linear-gradient(90deg, rgba(5, 7, 17, 0.12), rgba(5, 7, 17, 0.02)),
        var(--deck-bg) center / cover no-repeat,
        radial-gradient(circle at 52% 0%, rgba(83, 113, 255, 0.08), transparent 35%),
        linear-gradient(112deg, #050612 0%, #070818 45%, #041212 100%);
    }

    .slide-bg::before {
      display: none;
    }

    .slide-bg::after {
      content: "";
      position: absolute;
      inset: 0;
      opacity: 0.12;
      background-image:
        linear-gradient(rgba(255, 255, 255, 0.014) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.01) 1px, transparent 1px),
        radial-gradient(circle at 88% 28%, rgba(82, 255, 229, 0.12) 0 1px, transparent 1.6px);
      background-size: 64px 64px, 64px 64px, 11px 11px;
      mask-image: linear-gradient(90deg, rgba(0, 0, 0, 0.58) 0%, rgba(0, 0, 0, 0.42) 52%, rgba(0, 0, 0, 0.08) 66%, transparent 78%, transparent 100%);
    }

    .slide-inner {
      position: relative;
      z-index: 1;
      height: 100%;
      padding: var(--edge-offset) var(--edge-offset) 7.8%;
    }

    h1, h2, h3, p, blockquote, figure {
      margin: 0;
    }

    h1 {
      max-width: 76%;
      color: var(--accent);
      font-size: clamp(56px, 7.6vw, 122px);
      line-height: 1.08;
      font-weight: 900;
      text-shadow: 0 0 28px rgba(82, 255, 229, 0.24), 0 8px 0 rgba(0, 0, 0, 0.32);
    }

    h2 {
      font-size: clamp(34px, 4.4vw, 70px);
      line-height: 1.14;
      font-weight: 850;
      letter-spacing: 0;
    }

    h3 {
      font-size: clamp(18px, 2.1vw, 32px);
      line-height: 1.25;
      font-weight: 800;
      overflow-wrap: anywhere;
      word-break: break-word;
    }

    p, li, figcaption {
      color: var(--muted);
      font-size: clamp(17px, 1.9vw, 30px);
      line-height: 1.65;
      letter-spacing: 0;
    }

    strong { color: var(--text); }
    code {
      display: inline-block;
      padding: 0.08em 0.34em;
      border: 1px solid rgba(255, 148, 76, 0.24);
      border-radius: 0.18em;
      background: rgba(255, 148, 76, 0.12);
      color: #ffb374;
      font-family: Consolas, "Courier New", monospace;
      font-size: 0.88em;
      font-weight: 750;
      line-height: 1.18;
      vertical-align: 0.06em;
      white-space: normal;
      overflow-wrap: anywhere;
    }

    .cover-copy {
      position: absolute;
      left: var(--edge-offset);
      top: 17.5%;
    }

    .kicker {
      margin-bottom: 2.3rem;
      color: var(--accent);
      font-family: Consolas, "Courier New", monospace;
      font-size: clamp(16px, 1.5vw, 28px);
      letter-spacing: 0.18em;
    }

    .subtitle {
      margin-top: 2.3rem;
      max-width: 70%;
      color: #c9cad5;
      font-size: clamp(22px, 2.2vw, 36px);
    }

    .brand-mark {
      position: absolute;
      left: var(--edge-offset);
      bottom: 13%;
      color: rgba(255, 255, 255, 0.34);
      font-family: Consolas, "Courier New", monospace;
      font-size: clamp(15px, 1.3vw, 23px);
      letter-spacing: 0.12em;
    }

    .agenda h2 {
      margin-bottom: 4.2%;
    }

    .agenda ol {
      display: grid;
      grid-template-columns: minmax(0, 1fr);
      gap: 1.25rem;
      width: min(74rem, 100%);
      padding: 0;
      margin: 0;
      list-style: none;
    }

    .agenda li {
      display: flex;
      align-items: baseline;
      gap: 1.4rem;
      min-height: 4.7rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.11);
    }

    .agenda span {
      color: var(--accent);
      font-family: Consolas, "Courier New", monospace;
      font-size: clamp(28px, 3.1vw, 48px);
      font-weight: 900;
    }

    .agenda strong {
      color: var(--text);
      font-size: clamp(21px, 2.15vw, 34px);
    }

    .section-title {
      position: absolute;
      left: var(--edge-offset);
      right: var(--edge-offset);
      bottom: 25%;
      width: calc(100% - var(--edge-offset) * 2);
    }

    .section-number {
      margin-bottom: -1.4rem;
      color: rgba(82, 255, 229, 0.2);
      font-size: clamp(116px, 15vw, 240px);
      line-height: 0.9;
      font-weight: 900;
    }

    .section-title h2 {
      max-width: min(82rem, 100%);
      color: var(--accent);
      font-size: clamp(54px, 7vw, 112px);
      text-shadow: 0 0 28px rgba(82, 255, 229, 0.26), 0 7px 0 rgba(0, 0, 0, 0.35);
    }

    .content-stack {
      width: 100%;
      height: 100%;
      padding-top: var(--title-offset);
    }

    .content-stack h2,
    .matrix-wrap h2,
    .timeline h2,
    .image-copy h2 {
      margin-bottom: var(--title-gap);
    }

    .card-list {
      display: grid;
      gap: 1.25rem;
    }

    .point-card {
      display: grid;
      grid-template-columns: 1.5rem minmax(0, 1fr);
      gap: 1.4rem;
      align-items: center;
      min-height: 7.8rem;
      padding: 1.5rem 2rem;
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 8px;
      background: linear-gradient(90deg, var(--panel-strong), rgba(7, 22, 27, 0.72));
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05), 0 18px 50px var(--shadow);
    }

    .point-card > div {
      min-width: 0;
    }

    .point-card h3,
    .point-card p,
    .timeline h3,
    .timeline p,
    .matrix-card h3 {
      display: block;
      max-width: 100%;
      white-space: normal;
      overflow-wrap: anywhere;
      word-break: break-word;
      line-break: anywhere;
    }

    .dot {
      width: 0.68rem;
      height: 0.68rem;
      border-radius: 3px;
      background: var(--accent);
      box-shadow: 0 0 14px rgba(82, 255, 229, 0.75);
    }

    .point-card p {
      margin-top: 0.35rem;
      color: var(--body-muted);
      font-size: clamp(15px, 1.55vw, 24px);
      line-height: 1.5;
    }

    .matrix-wrap {
      height: 100%;
      padding-top: var(--title-offset);
    }

    .matrix-grid {
      display: grid;
      gap: 2rem;
      width: min(100%, 86rem);
    }

    .matrix-count-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .matrix-count-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
    .matrix-count-4 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .matrix-count-5,
    .matrix-count-6 { grid-template-columns: repeat(3, minmax(0, 1fr)); }

    .matrix-card {
      min-height: 10.6rem;
      padding: 1.8rem 2.15rem;
      border: 1px solid rgba(255, 255, 255, 0.09);
      border-radius: 8px;
      background: linear-gradient(105deg, rgba(20, 22, 50, 0.86), rgba(6, 24, 30, 0.72));
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05), 0 24px 68px rgba(0, 0, 0, 0.32);
    }

    .matrix-card h3 {
      font-size: clamp(22px, 2.2vw, 36px);
      overflow-wrap: anywhere;
      word-break: break-word;
    }

    .matrix-card p,
    .matrix-card li {
      color: var(--body-muted);
      font-size: clamp(15px, 1.55vw, 24px);
      line-height: 1.45;
    }

    .matrix-card p {
      margin-top: 0.75rem;
    }

    .matrix-icon {
      display: inline-block;
      width: clamp(30px, 2.5vw, 44px);
      aspect-ratio: 1;
      margin-bottom: 1.35rem;
      border-radius: 8px;
      background: rgba(82, 255, 229, 0.82);
      box-shadow: 0 0 12px rgba(82, 255, 229, 0.34), inset 0 -5px 10px rgba(0, 0, 0, 0.14);
    }

    .matrix-style-list .matrix-grid {
      width: min(100%, 90rem);
      gap: 2rem;
    }

    .matrix-style-list .matrix-count-3 {
      width: min(100%, calc(100vw - var(--edge-offset) * 2));
      gap: 1.35rem;
    }

    .matrix-style-list .matrix-card {
      min-height: 15rem;
      padding: 2.1rem 2.5rem;
      background: linear-gradient(105deg, rgba(20, 22, 50, 0.88), rgba(5, 24, 29, 0.78));
    }

    .matrix-style-list .matrix-count-3 .matrix-card {
      padding-inline: 2rem;
    }

    .matrix-style-list .matrix-card.is-emphasis {
      border-color: rgba(82, 255, 229, 0.72);
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06), 0 0 0 1px rgba(82, 255, 229, 0.22), 0 24px 72px rgba(0, 0, 0, 0.35);
    }

    .matrix-style-list .matrix-icon {
      display: none;
    }

    .matrix-style-list h3 {
      padding-bottom: 0.85rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.12);
    }

    .matrix-style-list ul {
      margin: 1.05rem 0 0;
      padding-left: 1.2em;
    }

    .matrix-style-list li + li {
      margin-top: 0.32rem;
    }

    .matrix-style-feature .matrix-count-4 .matrix-card,
    .matrix-style-feature .matrix-count-5 .matrix-card,
    .matrix-style-feature .matrix-count-6 .matrix-card {
      min-height: 13.4rem;
    }

    .quote-block {
      position: absolute;
      left: var(--edge-offset);
      top: 18%;
      width: 78%;
    }

    .quote-mark {
      display: flex;
      gap: 0.9rem;
      height: 4.4rem;
      align-items: flex-start;
      filter: drop-shadow(0 0 14px rgba(82, 255, 229, 0.34));
    }

    .quote-mark span {
      display: block;
      width: 1.45rem;
      height: 3.4rem;
      border-radius: 0.25rem;
      background: var(--accent);
      transform: skewX(-12deg);
      box-shadow: inset 0 -0.45rem 0 rgba(0, 0, 0, 0.16);
    }

    blockquote {
      max-width: 84rem;
      margin-top: 2.15rem;
      color: var(--text);
      font-size: clamp(38px, 4.6vw, 74px);
      line-height: 1.35;
      font-weight: 850;
    }

    figcaption {
      margin-top: 2.2rem;
      color: rgba(198, 202, 218, 0.68);
      font-size: clamp(18px, 1.65vw, 28px);
    }

    .timeline {
      height: 100%;
      padding-top: var(--title-offset);
    }

    .timeline ol {
      position: relative;
      display: grid;
      gap: 1.65rem;
      width: min(58rem, 72%);
      padding: 0;
      margin: 0;
      list-style: none;
    }

    .timeline li {
      display: grid;
      grid-template-columns: 4.8rem minmax(0, 1fr);
      gap: 1.8rem;
      align-items: start;
    }

    .timeline li > div {
      min-width: 0;
    }

    .timeline li::before {
      content: "";
      position: absolute;
      left: 2.35rem;
      top: 4rem;
      bottom: 4rem;
      width: 2px;
      background: rgba(255, 255, 255, 0.2);
      z-index: -1;
    }

    .timeline span {
      display: grid;
      place-items: center;
      width: 3.9rem;
      height: 3.9rem;
      min-width: 3.9rem;
      min-height: 3.9rem;
      aspect-ratio: 1 / 1;
      border-radius: 50%;
      box-sizing: border-box;
      flex: 0 0 3.9rem;
      background: var(--accent);
      color: #02100f;
      font-family: Consolas, "Courier New", monospace;
      font-size: clamp(24px, 2.8vw, 42px);
      font-weight: 900;
      line-height: 1;
      box-shadow: 0 0 24px rgba(82, 255, 229, 0.35);
    }

    .timeline p {
      margin-top: 0.4rem;
    }

    .image-text {
      display: grid;
      grid-template-columns: minmax(0, 0.95fr) minmax(18rem, 0.9fr);
      gap: 6%;
      height: 100%;
      align-items: start;
      padding-top: var(--title-offset);
    }

    .image-copy p {
      margin-top: 1.2rem;
      max-width: 39rem;
    }

    .image-frame {
      min-height: 21rem;
      padding: 1rem;
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 8px;
      background: linear-gradient(135deg, rgba(25, 37, 63, 0.88), rgba(5, 28, 30, 0.8));
      box-shadow: 0 24px 70px rgba(0, 0, 0, 0.35);
    }

    .image-frame img {
      display: block;
      width: 100%;
      height: 100%;
      max-height: 24rem;
      object-fit: contain;
      border-radius: 4px;
    }

    .compare-table-wrap {
      height: 100%;
      padding-top: var(--title-offset);
    }

    .compare-table-wrap h2 {
      margin-bottom: 2.35rem;
    }

    .compare-table-frame {
      width: min(100%, 94rem);
      border: 1px solid rgba(82, 255, 229, 0.16);
      border-radius: 8px;
      overflow: hidden;
      background:
        linear-gradient(135deg, rgba(30, 35, 64, 0.82), rgba(5, 25, 30, 0.72)),
        rgba(7, 13, 24, 0.82);
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05), 0 28px 76px rgba(0, 0, 0, 0.34);
    }

    .compare-table {
      width: 100%;
      border-collapse: collapse;
      table-layout: fixed;
    }

    .compare-table th,
    .compare-table td {
      padding: 1.05rem 1.35rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      border-right: 1px solid rgba(255, 255, 255, 0.06);
      color: rgba(220, 224, 238, 0.82);
      font-size: clamp(14px, 1.22vw, 22px);
      line-height: 1.58;
      text-align: left;
      vertical-align: middle;
      word-break: break-word;
    }

    .compare-table th:last-child,
    .compare-table td:last-child {
      border-right: 0;
    }

    .compare-table tr:last-child th,
    .compare-table tr:last-child td {
      border-bottom: 0;
    }

    .compare-table thead th {
      padding-top: 1.25rem;
      padding-bottom: 1.25rem;
      background: linear-gradient(90deg, rgba(82, 255, 229, 0.13), rgba(82, 255, 229, 0.04));
      color: #f3fffd;
      font-size: clamp(15px, 1.32vw, 24px);
      font-weight: 850;
    }

    .compare-table thead th:first-child {
      width: 18%;
      color: var(--accent);
    }

    .compare-table tbody th {
      width: 18%;
      color: #f3fffd;
      font-weight: 850;
      background: rgba(255, 255, 255, 0.025);
    }

    .compare-table tbody tr:nth-child(even) {
      background: rgba(255, 255, 255, 0.025);
    }

    .compare-table code {
      padding: 0.18rem 0.42rem;
      border-radius: 5px;
      font-size: 0.9em;
    }

    .status-cell,
    .status-item {
      display: inline-flex;
      align-items: center;
      gap: 0.72rem;
    }

    .status-icon {
      display: inline-grid;
      place-items: center;
      width: 1.1em;
      min-width: 1.1em;
      color: #55f0b3;
      font-family: Consolas, "Courier New", monospace;
      font-weight: 900;
      line-height: 1;
      text-shadow: 0 0 14px rgba(85, 240, 179, 0.34);
    }

    .status-no .status-icon {
      color: rgba(153, 151, 190, 0.86);
      text-shadow: none;
    }

    .status-no {
      color: rgba(198, 199, 220, 0.76);
    }

    .status-list-wrap {
      height: 100%;
      padding-top: var(--title-offset);
    }

    .status-list-wrap h2 {
      margin-bottom: 2.8rem;
    }

    .status-list {
      display: grid;
      gap: 1.2rem;
      width: min(52rem, 72%);
      padding: 0;
      margin: 0;
      list-style: none;
    }

    .status-item {
      min-height: 3.2rem;
      padding: 0.25rem 0;
      color: rgba(238, 242, 252, 0.9);
      font-size: clamp(20px, 2.1vw, 34px);
      line-height: 1.35;
      font-weight: 700;
    }

    .status-item .status-icon {
      width: 1.35em;
      min-width: 1.35em;
      font-size: 0.9em;
    }

    .statement {
      position: absolute;
      left: var(--edge-offset);
      top: var(--title-offset);
      width: 80%;
    }

    .statement h2 {
      margin-bottom: var(--title-gap);
      font-size: clamp(43px, 5.2vw, 86px);
    }

    .statement p {
      max-width: 62rem;
      color: rgba(205, 209, 224, 0.76);
    }

    .fragment {
      opacity: 0;
      transform: translateY(16px);
      transition: opacity 240ms ease, transform 240ms ease;
    }

    .fragment.visible {
      opacity: 1;
      transform: translateY(0);
    }

    #progress {
      position: absolute;
      left: 0;
      bottom: 0;
      width: 100%;
      height: 4px;
      z-index: 5;
      background: rgba(255, 255, 255, 0.08);
    }

    #progress span {
      display: block;
      height: 100%;
      width: 0%;
      background: var(--accent);
      box-shadow: 0 0 18px rgba(82, 255, 229, 0.75);
      transition: width 220ms ease;
    }

    #controls {
      position: absolute;
      right: 2.2%;
      bottom: 2.5%;
      z-index: 6;
      display: flex;
      align-items: center;
      gap: 0.7rem;
      color: var(--accent);
      font-family: Consolas, "Courier New", monospace;
    }

    #controls button {
      width: 2.15rem;
      height: 2.15rem;
      padding: 0;
      border: 0;
      background: transparent;
      color: var(--accent);
      font-size: 3.2rem;
      line-height: 1;
      cursor: pointer;
      text-shadow: 0 0 14px rgba(82, 255, 229, 0.45);
    }

    #counter {
      min-width: 4.4rem;
      text-align: center;
      color: #d8fff9;
      font-size: clamp(16px, 1.55vw, 28px);
    }

    @media (max-aspect-ratio: 4 / 3) {
      :root { --edge-offset: 3.5rem; }
      .slide-inner { padding: var(--edge-offset) var(--edge-offset) 10%; }
      .agenda ol { grid-template-columns: 1fr; gap: 1.1rem; }
      .image-text { grid-template-columns: 1fr; gap: 2rem; }
      .compare-table-frame { width: 100%; overflow-x: auto; }
      .compare-table { min-width: 54rem; }
      .status-list { width: 100%; }
      .matrix-grid,
      .matrix-style-list .matrix-grid { grid-template-columns: 1fr; gap: 1rem; }
      .matrix-card,
      .matrix-style-list .matrix-card { min-height: auto; padding: 1.4rem 1.5rem; }
      .image-frame { min-height: 12rem; }
      .timeline ol { width: 100%; }
      .section-title h2, h1 { max-width: 94%; }
      blockquote { font-size: clamp(34px, 7.4vw, 68px); }
    }
  </style>
</head>
<body>
  <main id="deck" aria-label="Markdown generated presentation">
__SLIDES__
    <div id="progress"><span></span></div>
    <nav id="controls" aria-label="Presentation controls">
      <button id="prev" type="button" aria-label="Previous slide">‹</button>
      <span id="counter">1 / __TOTAL__</span>
      <button id="next" type="button" aria-label="Next slide">›</button>
    </nav>
  </main>
  <script>
    const slides = Array.from(document.querySelectorAll(".slide"));
    const progress = document.querySelector("#progress span");
    const counter = document.querySelector("#counter");
    const stepReveal = __STEP_REVEAL__;
    const reveals = slides.map(() => 0);

    function pageFromHash() {
      return Math.min(Math.max(parseInt(location.hash.slice(1), 10) || 1, 1), slides.length) - 1;
    }

    function isReloadNavigation() {
      const navigation = performance.getEntriesByType && performance.getEntriesByType("navigation")[0];
      if (navigation) {
        return navigation.type === "reload";
      }
      return performance.navigation && performance.navigation.type === 1;
    }

    function hasDeckHistoryState() {
      return Boolean(history.state && history.state.markdownPptHtmlOpened);
    }

    function hasOpenedInThisTab() {
      if (hasDeckHistoryState()) {
        return true;
      }
      const sessionKey = `markdown-ppt-html-opened:${location.pathname}`;
      const windowMarker = `|${sessionKey}|`;
      let opened = false;
      try {
        opened = sessionStorage.getItem(sessionKey) === "1";
        sessionStorage.setItem(sessionKey, "1");
      } catch {
        opened = false;
      }
      if (!opened) {
        opened = window.name.includes(windowMarker);
      }
      if (!window.name.includes(windowMarker)) {
        window.name = `${window.name || ""}${windowMarker}`;
      }
      return opened || isReloadNavigation();
    }

    let page = hasOpenedInThisTab() ? pageFromHash() : 0;

    function fragmentsFor(index) {
      return Array.from(slides[index].querySelectorAll(".fragment"));
    }

    function replacePageUrl() {
      const targetHash = `#${page + 1}`;
      const targetUrl = `${location.href.split("#")[0]}${targetHash}`;
      try {
        history.replaceState({ markdownPptHtmlOpened: true }, "", targetUrl);
      } catch {
        if (location.hash !== targetHash) {
          location.hash = targetHash;
        }
      }
    }

    function update() {
      slides.forEach((slide, index) => {
        slide.classList.toggle("active", index === page);
        fragmentsFor(index).forEach((fragment, fragmentIndex) => {
          fragment.classList.toggle("visible", !stepReveal || fragmentIndex < reveals[index]);
        });
      });
      counter.textContent = `${page + 1} / ${slides.length}`;
      progress.style.width = `${((page + 1) / slides.length) * 100}%`;
      replacePageUrl();
    }

    function next() {
      const fragments = fragmentsFor(page);
      if (stepReveal && reveals[page] < fragments.length) {
        reveals[page] += 1;
      } else if (page < slides.length - 1) {
        page += 1;
      }
      update();
    }

    function prev() {
      if (stepReveal && reveals[page] > 0) {
        reveals[page] -= 1;
      } else if (page > 0) {
        page -= 1;
        reveals[page] = stepReveal ? fragmentsFor(page).length : 0;
      }
      update();
    }

    function isControlTarget(target) {
      return target && target.closest && target.closest("#controls");
    }

    function navigateFromPointer(event) {
      if (event.button && event.button !== 0) {
        return;
      }
      if (isControlTarget(event.target)) {
        return;
      }
      document.body.focus({ preventScroll: true });
      next();
    }

    function handleKeydown(event) {
      const key = event.key || event.code || "";
      const keyCode = event.keyCode || event.which;
      const forward = key === "ArrowRight" || key === "Right" || key === "ArrowDown" || key === "Down" || key === "PageDown" || key === " " || key === "Space" || key === "Spacebar" || keyCode === 39 || keyCode === 40 || keyCode === 34 || keyCode === 32;
      const backward = key === "ArrowLeft" || key === "Left" || key === "ArrowUp" || key === "Up" || key === "PageUp" || key === "Backspace" || keyCode === 37 || keyCode === 38 || keyCode === 33 || keyCode === 8;
      if (forward) {
        event.preventDefault();
        next();
        return;
      }
      if (backward) {
        event.preventDefault();
        prev();
      }
    }

    document.body.tabIndex = -1;
    document.body.focus({ preventScroll: true });
    document.querySelector("#next").addEventListener("click", (event) => {
      event.stopPropagation();
      next();
    });
    document.querySelector("#prev").addEventListener("click", (event) => {
      event.stopPropagation();
      prev();
    });
    document.addEventListener("click", navigateFromPointer);
    window.addEventListener("keydown", handleKeydown, true);
    update();
  </script>
</body>
</html>
"""


def convert(input_path: Path, output_path: Path, options: ExportOptions | None = None) -> None:
    source = input_path.read_text(encoding="utf-8")
    frontmatter, body = split_frontmatter(source)
    options = options or merge_options(frontmatter)
    slides = parse_markdown(body, options)
    if not slides:
        raise ValueError("No slides were found in the Markdown file.")

    title = slides[0].title or input_path.stem
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_deck(slides, title, options), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert Markdown to standalone PPT-style HTML.")
    parser.add_argument("input", type=Path, help="Input Markdown file.")
    parser.add_argument("output", type=Path, help="Output HTML file.")
    agenda_group = parser.add_mutually_exclusive_group()
    agenda_group.add_argument("--agenda", dest="agenda", action="store_true", help="Force agenda slide generation.")
    agenda_group.add_argument("--no-agenda", dest="agenda", action="store_false", help="Disable agenda slide generation.")
    parser.set_defaults(agenda=None)
    reveal_group = parser.add_mutually_exclusive_group()
    reveal_group.add_argument("--step-reveal", dest="step_reveal", action="store_true", help="Force bullet fragment reveal animation.")
    reveal_group.add_argument("--no-step-reveal", dest="step_reveal", action="store_false", help="Show all bullet points immediately.")
    parser.set_defaults(step_reveal=None)
    args = parser.parse_args()
    source = args.input.read_text(encoding="utf-8")
    frontmatter, body = split_frontmatter(source)
    options = merge_options(frontmatter, agenda=args.agenda, step_reveal=args.step_reveal)
    slides = parse_markdown(body, options)
    if not slides:
        raise ValueError("No slides were found in the Markdown file.")
    title = slides[0].title or args.input.stem
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_deck(slides, title, options), encoding="utf-8")
    print(f"Generated {args.output}")


if __name__ == "__main__":
    main()
