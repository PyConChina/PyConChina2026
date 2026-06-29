from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, cast

from PIL import Image, ImageDraw, ImageFont

if TYPE_CHECKING:
    from talk.models import TalkPage


STATIC_PATH = Path(__file__).resolve().parent / "static"


def render_poster(talk: TalkPage) -> Image.Image:
    from talk.models import Author

    """生成演讲海报图片"""
    # 创建画布
    font_size = 60
    padding = (100, 150)
    with Image.open(STATIC_PATH / "images/background.jpg") as image:
        img = image.copy()

    draw = ImageDraw.Draw(img)
    draw.textbbox
    font = ImageFont.truetype(
        STATIC_PATH / "fonts/AlibabaPuHuiTi-Regular.otf", font_size
    )
    title_font = ImageFont.truetype(
        STATIC_PATH / "fonts/AlibabaPuHuiTi-Bold.otf", font_size * 1.6
    )
    footer_font = ImageFont.truetype(
        STATIC_PATH / "fonts/AlibabaPuHuiTi-Regular.otf", font_size * 0.8
    )

    is_cjk = talk.locale.language_code.startswith("zh")

    title_text = wrap_text(
        talk.title, title_font, draw, img.width - sum(padding), is_cjk=is_cjk
    )
    draw.text((padding[0], 350), title_text, font=title_font, fill="black")

    if author := cast(Author, talk.authors.first()):
        author_font = ImageFont.truetype(
            STATIC_PATH / "fonts/AlibabaPuHuiTi-Bold.otf", font_size
        )
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

    draw.text((padding[0], 980), "PyCon China 2025", font=footer_font, fill="#888888")

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
