import io
from datetime import date, time
from types import SimpleNamespace

from django.test import TestCase
from PIL import Image, ImageDraw
from wagtail.models import Locale, Page, Site

from base.models import ConferenceCity
from home.models import HomePage
from schedule.models import Room, Schedule, ScheduleListPage
from talk.models import TalkListPage, TalkPage, TalkType
from talk.utils import (
    POSTER_SIZE,
    fit_multiline_text,
    get_speaker_details,
    get_static_asset_path,
)


class TalkListPageCityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.locale = Locale.get_default()
        root = Page.get_first_root_node()
        cls.home = root.add_child(
            instance=HomePage(
                title="Conference home",
                slug="conference-home",
                locale=cls.locale,
                body=[],
            )
        )
        Site.objects.update(root_page=cls.home)
        Site.clear_site_root_paths_cache()
        cls.talk_list = cls.home.add_child(
            instance=TalkListPage(
                title="Talks",
                slug="talks",
                locale=cls.locale,
            )
        )
        cls.shanghai = ConferenceCity.objects.create(
            name="Shanghai",
            slug="shanghai",
            venue="Shanghai venue",
            map_url="https://example.com/maps/shanghai",
            start_date=date(2026, 9, 5),
            locale=cls.locale,
            position=10,
        )
        cls.beijing = ConferenceCity.objects.create(
            name="Beijing",
            slug="beijing",
            locale=cls.locale,
            position=20,
        )
        cls.shanghai_talk = cls.talk_list.add_child(
            instance=TalkPage(
                title="Shanghai talk",
                slug="shanghai-talk",
                locale=cls.locale,
                city=cls.shanghai,
                position=20,
            )
        )
        cls.beijing_talk = cls.talk_list.add_child(
            instance=TalkPage(
                title="Beijing talk",
                slug="beijing-talk",
                locale=cls.locale,
                city=cls.beijing,
                position=10,
            )
        )
        cls.lightning_talk = cls.talk_list.add_child(
            instance=TalkPage(
                title="Shanghai lightning talk",
                slug="shanghai-lightning-talk",
                locale=cls.locale,
                city=cls.shanghai,
                type=TalkType.LIGHTNING,
                position=30,
            )
        )
        cls.schedule_list = cls.home.add_child(
            instance=ScheduleListPage(
                title="Schedule",
                slug="schedule",
                locale=cls.locale,
            )
        )
        cls.main_room = Room.objects.create(
            name="Main room",
            locale=cls.locale,
        )
        Schedule.objects.create(
            page=cls.schedule_list,
            talk=cls.shanghai_talk,
            city=cls.shanghai,
            date=date(2026, 9, 5),
            start_time=time(14, 30),
            end_time=time(15, 15),
            room=cls.main_room,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        Site.clear_site_root_paths_cache()

    def test_get_talks_filters_by_city(self):
        talks = list(self.talk_list.get_talks(self.shanghai))

        self.assertEqual(talks, [self.shanghai_talk])

    def test_get_talks_excludes_lightning_talks(self):
        talks = list(self.talk_list.get_talks())

        self.assertNotIn(self.lightning_talk, talks)

    def test_talk_list_renders_city_sections(self):
        response = self.client.get(
            "/2026/talks/", HTTP_HOST="localhost"
        )

        self.assertContains(response, 'id="city-shanghai"')
        self.assertContains(response, 'id="city-beijing"')
        self.assertContains(response, 'data-city-tabs')
        self.assertContains(response, 'aria-controls="city-shanghai"')
        self.assertContains(response, 'data-city-tab-panel', count=2)
        self.assertContains(response, "Shanghai talk")
        self.assertContains(response, "Beijing talk")
        self.assertContains(response, 'href="https://example.com/maps/shanghai"')
        self.assertContains(response, 'class="city-map-link"', count=1)
        self.assertNotContains(response, "Shanghai lightning talk")

        content = response.content.decode()
        city_index = content.index('id="city-shanghai-title"')
        date_index = content.index('class="talk-city-date"', city_index)
        venue_index = content.index('class="talk-city-venue"', date_index)
        self.assertLess(city_index, date_index)
        self.assertLess(date_index, venue_index)

    def test_poster_route_returns_png(self):
        response = self.client.get(
            "/2026/talks/shanghai-talk/poster/",
            HTTP_HOST="localhost",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/png")
        self.assertTrue(response.content.startswith(b"\x89PNG\r\n\x1a\n"))
        with Image.open(io.BytesIO(response.content)) as poster:
            self.assertEqual(poster.size, POSTER_SIZE)
            self.assertEqual(poster.mode, "RGB")

    def test_poster_text_fits_within_bounded_area(self):
        canvas = Image.new("RGB", (800, 400))
        draw = ImageDraw.Draw(canvas)
        font, text, spacing = fit_multiline_text(
            "可靠的人工智能系统" * 32,
            get_static_asset_path("fonts/AlibabaPuHuiTi-Bold.otf"),
            draw,
            500,
            160,
            max_size=72,
            min_size=36,
            is_cjk=True,
        )

        text_box = draw.multiline_textbbox(
            (0, 0),
            text,
            font=font,
            spacing=spacing,
        )
        self.assertLessEqual(text_box[2], 500)
        self.assertLessEqual(text_box[3] - text_box[1], 160)
        self.assertTrue(text.endswith("…"))

    def test_poster_speaker_details_include_bio(self):
        authors = [
            SimpleNamespace(name="First speaker", bio="First bio"),
            SimpleNamespace(name="Second speaker", bio="Second bio"),
        ]
        talk = SimpleNamespace(
            authors=SimpleNamespace(all=lambda: authors),
        )

        names, bios = get_speaker_details(talk)

        self.assertEqual(names, "First speaker / Second speaker")
        self.assertEqual(bios, "First bio / Second bio")
