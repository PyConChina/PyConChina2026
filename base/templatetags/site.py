from __future__ import annotations

from datetime import time
from typing import TYPE_CHECKING

from django import template
from django.conf import settings
from django.utils import translation
from wagtail.models import Page, Site

if TYPE_CHECKING:
    from schedule.models import Schedule

register = template.Library()


@register.simple_tag(takes_context=True)
def get_site_root(context):
    language_code = translation.get_language()
    if "request" in context:
        site = Site.find_for_request(context["request"])
    else:
        site = Site.objects.first()
    return site.root_page.get_translations(inclusive=True).get(
        locale__language_code=language_code
    )


def get_time_delta_minutes(a: time, b: time) -> int:
    return (b.hour * 60 + b.minute) - (a.hour * 60 + a.minute)


@register.simple_tag
def get_span(schedule: Schedule, start_time: time) -> tuple[int, int]:
    return (
        get_time_delta_minutes(start_time, schedule.start_time),
        get_time_delta_minutes(start_time, schedule.end_time),
    )


@register.filter
def divide(value: int, by: int) -> int:
    return value // int(by)


@register.simple_tag
def get_translations(page: Page) -> list[Page]:
    if not isinstance(page, Page):
        return []
    return list(page.get_translations(inclusive=True).live())


@register.simple_tag(takes_context=True)
def i18n_url(context, page: Page) -> str:
    url = page.get_url(request=context.get("request"))
    if not url:
        return url
    if page.locale.language_code != settings.LANGUAGE_CODE:
        url = url.replace(
            f"/{settings.URL_PREFIX}",
            f"/{settings.URL_PREFIX}{page.locale.language_code}/",
        )
    return url


@register.simple_tag
def get_coc_page() -> Page | None:
    language_code = translation.get_language()
    page = Page.objects.filter(slug="coc", locale__language_code=language_code).first()
    return page
