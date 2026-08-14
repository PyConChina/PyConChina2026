from __future__ import annotations

from datetime import date, datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import QuerySet
from django.http import HttpResponse
from django.utils.translation import gettext as _
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, path
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page, ParentalKey, TranslatableMixin
from wagtail.snippets.models import register_snippet


# Create your models here.
class ScheduleListPage(RoutablePageMixin, Page):
    parent_page_types = ["home.HomePage"]
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("body"),
        InlinePanel("schedules", heading="Schedules", label="Schedules"),
    ]

    def get_cities(self):
        from base.models import ConferenceCity

        return ConferenceCity.objects.filter(locale=self.locale)

    def grouped_schedules(
        self, city=None
    ) -> dict[date, dict[Room | str, list[Schedule]]]:
        result: dict[date, dict[Room | str, list[Schedule]]] = {}
        schedules: QuerySet[Schedule] = self.schedules.order_by("date", "start_time")
        if city is not None:
            schedules = schedules.filter(city=city)
        for schedule in schedules:
            result.setdefault(schedule.date, {}).setdefault(
                schedule.room or "none_type", []
            ).append(schedule)
        for schedule_date, rooms in list(result.items()):
            main_venue = rooms.pop("none_type", [])
            result[schedule_date] = {"none_type": main_venue, **rooms}
        return result

    def get_schedule_groups(self):
        return [
            {"city": city, "dates": self.grouped_schedules(city)}
            for city in self.get_cities()
        ]

    @path("ical/")
    def ical(self, request):
        from uuid import uuid4

        from ics import Calendar, Event
        from ics.contentline import ContentLine

        cal = Calendar()
        schedules: QuerySet[Schedule] = self.schedules.order_by("date", "start_time")
        for schedule in schedules:
            event = Event()
            if schedule.room:
                venue = (
                    f"{schedule.room.name} ({schedule.room.address})"
                    if schedule.room.address
                    else schedule.room.name
                )
            else:
                venue = schedule.city.venue or _("Main Venue")
            location = f"{schedule.city.name} - {venue}"
            event.uid = str(uuid4())
            event.extra.append(ContentLine(name="SUMMARY", value=str(schedule)))
            event.begin = datetime.combine(schedule.date, schedule.start_time)
            event.end = datetime.combine(schedule.date, schedule.end_time)
            event.location = location
            if schedule.talk:
                event.description = (
                    _("Speaker")
                    + f": {schedule.talk.authors.first().name}\n\n{schedule.talk.body}"
                )
                event.url = request.build_absolute_uri(schedule.talk.url)
            cal.events.append(event)

        response = HttpResponse(cal.serialize(), content_type="text/calendar")
        response["Content-Disposition"] = 'attachment; filename="pycon-china-2026.ics"'
        return response


class Schedule(Orderable):
    page = ParentalKey(
        "schedule.ScheduleListPage",
        on_delete=models.CASCADE,
        related_name="schedules",
    )
    talk = models.OneToOneField(
        "talk.TalkPage",
        on_delete=models.SET_NULL,
        related_name="schedule",
        null=True,
        blank=True,
    )
    city = models.ForeignKey(
        "base.ConferenceCity",
        on_delete=models.PROTECT,
        related_name="schedules",
    )
    name = models.CharField(
        max_length=255, help_text="Name of the schedule", blank=True
    )
    start_time = models.TimeField(help_text="Start time")
    end_time = models.TimeField(help_text="End time")
    date = models.DateField(help_text="Date of the schedule")
    room = models.ForeignKey(
        "schedule.Room",
        on_delete=models.SET_NULL,
        related_name="schedules",
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return self.talk.title if self.talk else self.name

    def clean(self):
        super().clean()
        if self.talk_id and self.city_id and self.talk.city_id != self.city_id:
            raise ValidationError(
                {"talk": _("The talk and schedule must belong to the same city.")}
            )

    panels = [
        FieldPanel("talk"),
        FieldPanel("city"),
        FieldPanel("name"),
        FieldPanel("start_time"),
        FieldPanel("end_time"),
        FieldPanel("date"),
        FieldPanel("room"),
    ]


@register_snippet
class Room(TranslatableMixin, models.Model):
    name = models.CharField(max_length=32, help_text="Name of the room")
    address = models.CharField(
        max_length=255, help_text="Address of the room", blank=True
    )
    host = models.CharField(max_length=32, help_text="Host of the room", blank=True)
    panels = [FieldPanel("name"), FieldPanel("address"), FieldPanel("host")]

    def __str__(self) -> str:
        return self.name
