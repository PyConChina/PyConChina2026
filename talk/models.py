import io

from django import forms
from django.core.cache import cache
from django.db import models
from django.http import HttpResponse
from modelcluster.fields import ParentalManyToManyField
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, path
from wagtail.fields import RichTextField
from wagtail.models import Page, TranslatableMixin
from wagtail.snippets.models import register_snippet


class TalkType(models.TextChoices):
    KEYNOTE = "keynote", "主题"
    LIGHTNING = "lightning", "闪电"
    ROUNDTABLE = "roundtable", "圆桌"
    WORKSHOP = "workshop", "工作坊"


# Create your models here.
class TalkListPage(Page):
    parent_page_types = ["home.HomePage"]
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    def get_talks(self):
        return (
            self.get_children()
            .live()
            .filter(talkpage__type__in=(TalkType.KEYNOTE, TalkType.LIGHTNING))
            .order_by("talkpage__position", "id")
        )


class TalkPage(RoutablePageMixin, Page):
    parent_page_types = ["talk.TalkListPage"]
    abstract = models.TextField(blank=True)
    body = RichTextField(blank=True)
    type = models.CharField(
        max_length=32, choices=TalkType.choices, default=TalkType.KEYNOTE
    )
    authors = ParentalManyToManyField("talk.Author")
    position = models.IntegerField(default=100, help_text="Position in the list")

    content_panels = Page.content_panels + [
        FieldPanel("authors", widget=forms.CheckboxSelectMultiple),
        FieldPanel("abstract"),
        FieldPanel("body"),
        FieldPanel("type"),
        FieldPanel("position"),
    ]

    def save(self, clean=True, user=None, log_action=False, **kwargs):
        super().save(clean=clean, user=user, log_action=log_action, **kwargs)
        # Sync position changes across translations
        self.get_translations().update(position=self.position)

    @path("poster/")
    def poster(self, request):
        from talk.utils import render_poster

        response = HttpResponse(content_type="image/png")
        key = f"talk_poster_{self.pk}"
        if (image_bytes := cache.get(key, None)) is None:
            img = render_poster(self)
            image_buffer = io.BytesIO()
            img.save(image_buffer, "PNG")
            image_bytes = image_buffer.getvalue()
            cache.set(key, image_bytes, 60 * 60 * 24)
        response.write(image_bytes)
        response["Cache-Control"] = "public, max-age=86400"
        return response


@register_snippet
class Author(TranslatableMixin, models.Model):
    name = models.CharField(max_length=255, help_text="Name of the author")
    avatar = models.ForeignKey(
        "wagtailimages.Image", on_delete=models.CASCADE, related_name="+"
    )
    bio = models.CharField(max_length=255, blank=True, help_text="Bio of the author")
    introduction = RichTextField(blank=True, help_text="Introduction of the author")

    panels = [
        FieldPanel("name"),
        FieldPanel("avatar"),
        FieldPanel("bio"),
        FieldPanel("introduction"),
    ]

    def __str__(self):
        return self.name
