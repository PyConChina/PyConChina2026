from django.test import TestCase
from wagtail.models import Locale, Page, Site

from base.models import ConferenceCity
from home.models import HomePage
from talk.models import TalkListPage, TalkPage, TalkType


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
        self.assertNotContains(response, "Shanghai lightning talk")
