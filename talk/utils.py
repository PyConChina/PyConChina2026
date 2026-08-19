from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from django.contrib.staticfiles import finders
from PIL import Image, ImageDraw, ImageFont

if TYPE_CHECKING:
    from talk.models import TalkPage


def get_static_asset_path(relative_path: str) -> Path:
    asset_path = finders.find(relative_path)
    if not asset_path:
        raise FileNotFoundError(f"Static asset not found: {relative_path}")
    if isinstance(asset_path, (list, tuple)):
        asset_path = asset_path[0]
    return Path(asset_path)


def render_poster(talk: TalkPage) -> Image.Image:
    """Render a shareable image for a talk."""

    font_size = 60
    padding = (100, 150)
    regular_font_path = get_static_asset_path("fonts/AlibabaPuHuiTi-Regular.otf")
    bold_font_path = get_static_asset_path("fonts/AlibabaPuHuiTi-Bold.otf")

    with Image.open(get_static_asset_path("images/background.jpg")) as image:
        img = image.copy()

    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(regular_font_path, font_size)
    title_font = ImageFont.truetype(bold_font_path, font_size * 1.6)
    footer_font = ImageFont.truetype(regular_font_path, font_size * 0.8)

    is_cjk = talk.locale.language_code.startswith("zh")

    title_text = wrap_text(
        talk.title, title_font, draw, img.width - sum(padding), is_cjk=is_cjk
    )
    draw.text((padding[0], 350), title_text, font=title_font, fill="black")

    if author := talk.authors.first():
        author_font = ImageFont.truetype(bold_font_path, font_size)
        draw.text((450, 100), author.name, font=author_font, fill="black")
        if author.bio:
            draw.text(
                (450, 180),
                wrap_text(
                    author.bio, font, draw, img.width - 450 - padding[1], is_cjk=is_cjk
                ),
                font=font,
                fill="black",
            )

    draw.text((padding[0], 980), "PyCon China 2026", font=footer_font, fill="#888888")

    return img


def wrap_text(
    text: str,
    font: ImageFont.FreeTypeFont,
    draw: ImageDraw.ImageDraw,
    max_width: int,
    is_cjk: bool = False,
) -> str:
    if is_cjk:
        words = list(text)
    else:
        words = text.split(" ")
    lines = []
    current_line = ""
    for word in words:
        test_line = (
            f"{current_line} {word}".strip() if not is_cjk else f"{current_line}{word}"
        )
        width = draw.textlength(test_line, font=font)
        if width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return "\n".join(lines)
