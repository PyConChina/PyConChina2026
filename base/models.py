from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.contrib.settings.models import (
    BaseGenericSetting,
    register_setting,
)
from wagtail.models import Orderable, ParentalKey, TranslatableMixin
from wagtail.snippets.models import register_snippet


@register_snippet
class ConferenceCity(TranslatableMixin, models.Model):
    name = models.CharField(max_length=64)
    slug = models.SlugField(max_length=64)
    venue = models.CharField(max_length=255, blank=True)
    map_url = models.URLField(
        blank=True,
        help_text="Link to the venue in a map service",
    )
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    registration_url = models.URLField(blank=True)
    position = models.PositiveIntegerField(default=100)

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
        FieldPanel("venue"),
        FieldPanel("map_url"),
        FieldPanel("start_date"),
        FieldPanel("end_date"),
        FieldPanel("registration_url"),
        FieldPanel("position"),
    ]

    class Meta(TranslatableMixin.Meta):
        ordering = ["position", "start_date", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["locale", "slug"],
                name="unique_conference_city_slug_per_locale",
            ),
        ]
        verbose_name_plural = "conference cities"

    def __str__(self) -> str:
        return self.name

    def clean(self):
        super().clean()
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError(
                {"end_date": _("End date must not be earlier than start date.")}
            )


@register_setting
class NavigationSettings(BaseGenericSetting, ClusterableModel):
    panels = [
        InlinePanel("social_links", label="Social Links"),
    ]


class SocialLink(Orderable):
    page = ParentalKey("base.NavigationSettings", related_name="social_links")
    name = models.CharField(max_length=32)
    url = models.URLField()
    icon = models.CharField(max_length=32, blank=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("url"),
        FieldPanel("icon"),
    ]
