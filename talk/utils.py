from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from django.contrib.staticfiles import finders
from django.core.exceptions import ObjectDoesNotExist
from django.utils import translation
from django.utils.translation import gettext
from PIL import Image, ImageColor, ImageDraw, ImageFont

if TYPE_CHECKING:
    from talk.models import TalkPage


Color = str | tuple[int, int, int]
Box = tuple[int, int, int, int]

POSTER_CACHE_VERSION = 3
POSTER_SIZE = (1920, 1080)

BG_BASE = "#3daa84"
BG_DOT = "#4fb089"
PAPER = "#ffffff"
INK = "#1a1a1a"
INK_SOFT = "#3a3a3a"
GRAY_PIXEL = "#adb0b5"
PY_YELLOW = "#f9ca33"
PY_RED = "#ec4567"
PY_PURPLE = "#8312dc"
PY_BLUE = "#149ada"
PY_GREEN = "#75be4e"
CREAM = "#f5dc85"

BRAND_COLORS = (
    PY_RED,
    PY_YELLOW,
    PY_BLUE,
    CREAM,
    PY_PURPLE,
    PY_PURPLE,
    PY_BLUE,
    PY_YELLOW,
    PY_RED,
    CREAM,
)

TALK_TYPE_MESSAGE_IDS = {
    "keynote": "Keynote",
    "lightning": "Lightning",
    "roundtable": "Roundtable",
    "workshop": "Workshop",
}


def get_static_asset_path(relative_path: str) -> Path:
    asset_path = finders.find(relative_path)
    if not asset_path:
        raise FileNotFoundError(f"Static asset not found: {relative_path}")
    if isinstance(asset_path, (list, tuple)):
        asset_path = asset_path[0]
    return Path(asset_path)


def mix_color(color: Color, target: Color, amount: float) -> tuple[int, int, int]:
    source_rgb = ImageColor.getrgb(color) if isinstance(color, str) else color
    target_rgb = ImageColor.getrgb(target) if isinstance(target, str) else target
    return tuple(
        round(source * (1 - amount) + target_component * amount)
        for source, target_component in zip(source_rgb, target_rgb, strict=True)
    )


def draw_baseplate(draw: ImageDraw.ImageDraw) -> None:
    draw.rectangle((0, 0, *POSTER_SIZE), fill=BG_BASE)
    spacing = 36
    radius = 5
    for y in range(14, POSTER_SIZE[1], spacing):
        for x in range(14, POSTER_SIZE[0], spacing):
            draw.ellipse(
                (x - radius, y - radius, x + radius, y + radius),
                fill=BG_DOT,
            )


def draw_brick(
    draw: ImageDraw.ImageDraw,
    box: Box,
    color: Color,
    *,
    depth: int = 14,
    radius: int = 24,
    studs: bool = True,
) -> None:
    left, top, right, bottom = box
    dark_edge = mix_color(color, INK, 0.32)
    highlight = mix_color(color, PAPER, 0.16)
    stud_shadow = mix_color(color, INK, 0.18)
    stud_highlight = mix_color(color, PAPER, 0.22)

    draw.rounded_rectangle(
        (left, top + depth, right, bottom + depth),
        radius=radius,
        fill=dark_edge,
    )

    if studs:
        for x in range(left + 42, right - 20, 54):
            draw.ellipse(
                (x - 13, top - 13, x + 13, top + 13),
                fill=stud_shadow,
            )
            draw.ellipse(
                (x - 9, top - 10, x + 9, top + 7),
                fill=stud_highlight,
            )

    draw.rounded_rectangle(box, radius=radius, fill=color)
    draw.line(
        (left + radius, top + 5, right - radius, top + 5),
        fill=highlight,
        width=6,
    )


def draw_chip(
    draw: ImageDraw.ImageDraw,
    position: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: Color,
) -> Box:
    left, top = position
    text_box = draw.textbbox((0, 0), text, font=font)
    width = text_box[2] - text_box[0]
    height = text_box[3] - text_box[1]
    box = (left, top, left + width + 44, top + height + 30)
    draw_brick(draw, box, fill, depth=8, radius=12, studs=False)
    draw.text(
        (left + 22, top + 12 - text_box[1]),
        text,
        font=font,
        fill=INK,
    )
    return box


def split_long_token(
    token: str,
    font: ImageFont.FreeTypeFont,
    draw: ImageDraw.ImageDraw,
    max_width: int,
) -> list[str]:
    chunks: list[str] = []
    current = ""
    for character in token:
        candidate = f"{current}{character}"
        if current and draw.textlength(candidate, font=font) > max_width:
            chunks.append(current)
            current = character
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks


def wrap_text_lines(
    text: str,
    font: ImageFont.FreeTypeFont,
    draw: ImageDraw.ImageDraw,
    max_width: int,
    *,
    is_cjk: bool,
) -> list[str]:
    tokens = list(text) if is_cjk else text.split()
    separator = "" if is_cjk else " "
    lines: list[str] = []
    current = ""

    for token in tokens:
        if draw.textlength(token, font=font) > max_width:
            token_parts = split_long_token(token, font, draw, max_width)
        else:
            token_parts = [token]

        for token_part in token_parts:
            candidate = (
                f"{current}{separator}{token_part}" if current else token_part
            )
            if current and draw.textlength(candidate, font=font) > max_width:
                lines.append(current)
                current = token_part
            else:
                current = candidate

    if current:
        lines.append(current)
    return lines


def fit_multiline_text(
    text: str,
    font_path: Path,
    draw: ImageDraw.ImageDraw,
    max_width: int,
    max_height: int,
    *,
    max_size: int,
    min_size: int,
    is_cjk: bool,
) -> tuple[ImageFont.FreeTypeFont, str, int]:
    for size in range(max_size, min_size - 1, -4):
        font = ImageFont.truetype(font_path, size)
        spacing = max(10, round(size * 0.24))
        lines = wrap_text_lines(text, font, draw, max_width, is_cjk=is_cjk)
        wrapped_text = "\n".join(lines)
        text_box = draw.multiline_textbbox(
            (0, 0),
            wrapped_text,
            font=font,
            spacing=spacing,
        )
        if text_box[2] <= max_width and text_box[3] - text_box[1] <= max_height:
            return font, wrapped_text, spacing

    font = ImageFont.truetype(font_path, min_size)
    spacing = max(10, round(min_size * 0.24))
    lines = wrap_text_lines(text, font, draw, max_width, is_cjk=is_cjk)
    visible_lines = lines.copy()
    while len(visible_lines) > 1:
        wrapped_text = "\n".join(visible_lines)
        text_box = draw.multiline_textbbox(
            (0, 0),
            wrapped_text,
            font=font,
            spacing=spacing,
        )
        if text_box[3] - text_box[1] <= max_height:
            break
        visible_lines.pop()

    if len(visible_lines) < len(lines):
        ellipsis = "…"
        last_line = visible_lines[-1].rstrip()
        while last_line and draw.textlength(
            f"{last_line}{ellipsis}", font=font
        ) > max_width:
            last_line = last_line[:-1].rstrip()
        visible_lines[-1] = f"{last_line}{ellipsis}"

    return font, "\n".join(visible_lines), spacing


def draw_wordmark(
    draw: ImageDraw.ImageDraw,
    pixel_font_path: Path,
) -> None:
    font = ImageFont.truetype(pixel_font_path, 52)
    year_font = ImageFont.truetype(pixel_font_path, 48)
    text = "PYCON CHINA"
    x = 110
    y = 74
    color_index = 0

    for character in text:
        if character == " ":
            x += 34
            continue
        color = BRAND_COLORS[color_index]
        color_index += 1
        draw.text(
            (x + 7, y + 8),
            character,
            font=font,
            fill=mix_color(color, INK, 0.55),
            stroke_width=3,
            stroke_fill=INK,
        )
        draw.text(
            (x, y),
            character,
            font=font,
            fill=color,
            stroke_width=3,
            stroke_fill=INK,
        )
        x += round(draw.textlength(character, font=font)) + 6

    draw.text(
        (x + 32, y + 3),
        "2026",
        font=year_font,
        fill=GRAY_PIXEL,
        stroke_width=3,
        stroke_fill=INK,
    )

    tagline_font = ImageFont.truetype(pixel_font_path, 25)
    tagline = "AI FOR GOOD"
    tagline_width = round(draw.textlength(tagline, font=tagline_font)) + 44
    draw_chip(
        draw,
        (POSTER_SIZE[0] - tagline_width - 110, 82),
        tagline,
        tagline_font,
        PY_YELLOW,
    )


def get_talk_type_label(talk: TalkPage) -> str:
    message_id = TALK_TYPE_MESSAGE_IDS.get(talk.type, "Talk")
    return gettext(message_id).upper()


def get_event_details(talk: TalkPage) -> tuple[str, str, str]:
    city = talk.city
    try:
        schedule = talk.schedule
    except ObjectDoesNotExist:
        schedule = None

    if schedule is not None:
        date_text = schedule.date.strftime("%Y.%m.%d")
        time_text = (
            f"{schedule.start_time.strftime('%H:%M')}"
            f"–{schedule.end_time.strftime('%H:%M')}"
        )
        venue = schedule.room.name if schedule.room else city.venue
        return city.name, f"{date_text}  {time_text}", venue

    date_text = city.start_date.strftime("%Y.%m.%d") if city.start_date else ""
    return city.name, date_text, city.venue


def get_speaker_details(talk: TalkPage) -> tuple[str, str]:
    authors = list(talk.authors.all())
    names = " / ".join(author.name for author in authors) or "—"
    bios = " / ".join(author.bio.strip() for author in authors if author.bio.strip())
    return names, bios


def render_poster(talk: TalkPage) -> Image.Image:
    """Render a branded, shareable image for a talk."""

    regular_font_path = get_static_asset_path("fonts/AlibabaPuHuiTi-Regular.otf")
    bold_font_path = get_static_asset_path("fonts/AlibabaPuHuiTi-Bold.otf")
    pixel_font_path = get_static_asset_path("fonts/PressStart2P-Regular.ttf")

    image = Image.new("RGB", POSTER_SIZE, BG_BASE)
    draw = ImageDraw.Draw(image)
    draw_baseplate(draw)
    draw_wordmark(draw, pixel_font_path)

    language_code = talk.locale.language_code
    is_cjk = language_code.startswith("zh")
    with translation.override(language_code):
        talk_type_label = get_talk_type_label(talk)
        city_name, date_and_time, venue = get_event_details(talk)
        venue = venue or gettext("Venue to be announced.")

    title_box = (110, 270, 1810, 720)
    draw_brick(draw, title_box, PY_BLUE)

    chip_font = ImageFont.truetype(bold_font_path, 30)
    draw_chip(draw, (158, 315), talk_type_label, chip_font, PY_YELLOW)

    title_font, title_text, title_spacing = fit_multiline_text(
        talk.title,
        bold_font_path,
        draw,
        1570,
        275,
        max_size=100,
        min_size=48,
        is_cjk=is_cjk,
    )
    draw.multiline_text(
        (158, 405),
        title_text,
        font=title_font,
        fill=INK,
        spacing=title_spacing,
    )

    speaker_box = (110, 790, 1070, 990)
    draw_brick(draw, speaker_box, PAPER)

    author_names, author_bios = get_speaker_details(talk)
    author_font, author_text, author_spacing = fit_multiline_text(
        author_names,
        bold_font_path,
        draw,
        860,
        60,
        max_size=44,
        min_size=30,
        is_cjk=is_cjk,
    )
    draw.multiline_text(
        (155, 830),
        author_text,
        font=author_font,
        fill=INK,
        spacing=author_spacing,
    )
    if author_bios:
        bio_font, bio_text, bio_spacing = fit_multiline_text(
            author_bios,
            regular_font_path,
            draw,
            860,
            72,
            max_size=28,
            min_size=22,
            is_cjk=is_cjk,
        )
        draw.multiline_text(
            (155, 905),
            bio_text,
            font=bio_font,
            fill=INK_SOFT,
            spacing=bio_spacing,
        )

    event_box = (1110, 790, 1810, 990)
    draw_brick(draw, event_box, PY_YELLOW)
    city_font, city_text, city_spacing = fit_multiline_text(
        city_name,
        bold_font_path,
        draw,
        610,
        58,
        max_size=42,
        min_size=28,
        is_cjk=is_cjk,
    )
    draw.multiline_text(
        (1155, 825),
        city_text,
        font=city_font,
        fill=INK,
        spacing=city_spacing,
    )

    meta_font = ImageFont.truetype(regular_font_path, 30)
    if date_and_time:
        draw.text((1155, 895), date_and_time, font=meta_font, fill=INK)

    venue_font, venue_text, venue_spacing = fit_multiline_text(
        venue,
        regular_font_path,
        draw,
        610,
        50,
        max_size=28,
        min_size=22,
        is_cjk=is_cjk,
    )
    draw.multiline_text(
        (1155, 940),
        venue_text,
        font=venue_font,
        fill=INK_SOFT,
        spacing=venue_spacing,
    )

    footer_font = ImageFont.truetype(pixel_font_path, 18)
    draw.text(
        (110, 1034),
        "CN.PYCON.ORG/2026",
        font=footer_font,
        fill=PAPER,
    )

    return image
