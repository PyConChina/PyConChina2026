from datetime import date, time

from django.core.exceptions import ValidationError
from django.test import TestCase
from wagtail.models import Locale, Page, Site

from base.models import ConferenceCity
from home.models import HomePage
from schedule.models import Room, Schedule, ScheduleListPage
from talk.models import TalkListPage, TalkPage


class ScheduleListPageCityTests(TestCase):
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
        cls.schedule_list = cls.home.add_child(
            instance=ScheduleListPage(
                title="Schedule",
                slug="schedule",
                locale=cls.locale,
            )
        )
        cls.shanghai = ConferenceCity.objects.create(
            name="Shanghai",
            slug="shanghai",
            venue="Shanghai venue",
            map_url="https://example.com/maps/shanghai",
            locale=cls.locale,
            position=10,
        )
        cls.beijing = ConferenceCity.objects.create(
            name="Beijing",
            slug="beijing",
            locale=cls.locale,
            position=20,
        )
        cls.main_hall = Room.objects.create(
            name="Main Hall",
            locale=cls.locale,
        )
        cls.shanghai_talk = cls.talk_list.add_child(
            instance=TalkPage(
                title="Shanghai talk",
                slug="shanghai-talk",
                locale=cls.locale,
                city=cls.shanghai,
            )
        )
        Schedule.objects.create(
            page=cls.schedule_list,
            city=cls.shanghai,
            talk=cls.shanghai_talk,
            date=date(2026, 9, 5),
            start_time=time(9),
            end_time=time(10),
        )
        Schedule.objects.create(
            page=cls.schedule_list,
            city=cls.beijing,
            name="Registration",
            date=date(2026, 9, 12),
            start_time=time(8),
            end_time=time(9),
            room=cls.main_hall,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        Site.clear_site_root_paths_cache()

    def test_grouped_schedules_filters_by_city(self):
        shanghai_dates = self.schedule_list.grouped_schedules(self.shanghai)
        beijing_dates = self.schedule_list.grouped_schedules(self.beijing)

        self.assertEqual(list(shanghai_dates), [date(2026, 9, 5)])
        self.assertEqual(list(beijing_dates), [date(2026, 9, 12)])

    def test_schedule_rejects_talk_from_another_city(self):
        schedule = Schedule(
            page=self.schedule_list,
            city=self.beijing,
            talk=self.shanghai_talk,
            date=date(2026, 9, 12),
            start_time=time(10),
            end_time=time(11),
        )

        with self.assertRaises(ValidationError):
            schedule.clean()

    def test_schedule_page_renders_city_sections(self):
        response = self.client.get(
            "/2026/schedule/", HTTP_HOST="localhost"
        )

        self.assertContains(response, 'id="city-shanghai"')
        self.assertContains(response, 'id="city-beijing"')
        self.assertContains(response, 'data-city-tabs')
        self.assertContains(response, 'aria-controls="city-shanghai"')
        self.assertContains(response, 'data-city-tab-panel', count=2)
        self.assertContains(response, "Shanghai talk")
        self.assertContains(response, "Registration")
        self.assertContains(response, "Main Hall")
        self.assertContains(response, 'href="https://example.com/maps/shanghai"')
        self.assertContains(response, 'class="city-map-link"', count=1)
        self.assertContains(response, "grid-template-columns: repeat(1, 1fr)")
