from django.db import models
from django.db.models import Min
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import RichTextField, StreamField
from wagtail import blocks
from wagtail.models import Orderable, Page, ParentalKey


class ContentBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=True, form_classname="title")
    paragraph = blocks.RichTextBlock()


class HomePage(Page):
    body = StreamField([('paragraph', ContentBlock())])

    content_panels = Page.content_panels + [
        FieldPanel("body"),
        InlinePanel("links", heading="Related Links", label="Related Links"),
    ]

    def get_cities(self):
        from base.models import ConferenceCity

        return ConferenceCity.objects.filter(locale=self.locale)

    def get_talk_index(self):
        from talk.models import TalkListPage

        return TalkListPage.objects.child_of(self).live().first()

    def get_schedule_index(self):
        from schedule.models import ScheduleListPage

        return ScheduleListPage.objects.child_of(self).live().first()

    def get_speakers(self):
        from talk.models import Author

        return (
            Author.objects.filter(
                locale=self.locale,
                talkpage__live=True,
                talkpage__locale=self.locale,
            )
            .select_related("avatar")
            .annotate(first_talk_position=Min("talkpage__position"))
            .order_by("first_talk_position", "name")
        )


class ArticlePage(Page):
    parent_page_types = ["home.HomePage"]
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]


class RelatedLink(Orderable):
    page = ParentalKey(HomePage, on_delete=models.CASCADE, related_name="links")
    title = models.CharField(max_length=255)
    url = models.URLField()
