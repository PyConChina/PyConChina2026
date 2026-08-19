from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from wagtail.images import get_image_model
from wagtail.models import Locale, Page, Site

from base.models import ConferenceCity
from home.models import HomePage
from talk.models import Author, TalkListPage, TalkPage


class HomePageSpeakersTests(TestCase):
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
        cls.city = ConferenceCity.objects.create(
            name="Shanghai",
            slug="shanghai",
            venue="Main venue",
            map_url="https://example.com/maps/shanghai",
            registration_url="https://example.com/register/shanghai",
            locale=cls.locale,
            position=10,
        )
        cls.talk_list = cls.home.add_child(
            instance=TalkListPage(
                title="Talks",
                slug="talks",
                locale=cls.locale,
            )
        )
        image = get_image_model().objects.create(
            title="Speaker portrait",
            file=SimpleUploadedFile(
                "speaker.gif",
                b"GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;",
                content_type="image/gif",
            ),
        )
        cls.first_speaker = Author.objects.create(
            name="First speaker",
            avatar=image,
            locale=cls.locale,
        )
        cls.second_speaker = Author.objects.create(
            name="Second speaker",
            avatar=image,
            locale=cls.locale,
        )
        cls.no_talk_speaker = Author.objects.create(
            name="No talk speaker",
            avatar=image,
            locale=cls.locale,
        )
        cls.draft_speaker = Author.objects.create(
            name="Draft speaker",
            avatar=image,
            locale=cls.locale,
        )

        first_talk = cls.talk_list.add_child(
            instance=TalkPage(
                title="First talk",
                slug="first-talk",
                locale=cls.locale,
                position=20,
                city=cls.city,
            )
        )
        first_talk.authors.add(cls.first_speaker)
        first_talk.authors.add(cls.second_speaker)
        first_talk.save()

        second_talk = cls.talk_list.add_child(
            instance=TalkPage(
                title="Second talk",
                slug="second-talk",
                locale=cls.locale,
                position=10,
                city=cls.city,
            )
        )
        second_talk.authors.add(cls.second_speaker)
        second_talk.save()

        draft_talk = cls.talk_list.add_child(
            instance=TalkPage(
                title="Draft talk",
                slug="draft-talk",
                locale=cls.locale,
                position=1,
                live=False,
                city=cls.city,
            )
        )
        draft_talk.authors.add(cls.draft_speaker)
        draft_talk.save()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        Site.clear_site_root_paths_cache()

    def test_get_speakers_only_returns_authors_with_live_talks(self):
        self.assertQuerySetEqual(
            self.home.get_speakers(),
            [self.second_speaker, self.first_speaker],
        )

    def test_get_speakers_deduplicates_authors_with_multiple_talks(self):
        speaker_ids = list(self.home.get_speakers().values_list("id", flat=True))

        self.assertEqual(speaker_ids.count(self.second_speaker.id), 1)

    def test_get_cities_only_returns_current_locale(self):
        english, _ = Locale.objects.get_or_create(language_code="en")
        ConferenceCity.objects.create(
            name="Shanghai",
            slug="shanghai",
            locale=english,
        )

        self.assertQuerySetEqual(self.home.get_cities(), [self.city])

    def test_homepage_renders_city_destinations(self):
        ConferenceCity.objects.create(
            name="Shenzhen",
            slug="shenzhen",
            locale=self.locale,
            position=20,
        )

        response = self.client.get("/2026/", HTTP_HOST="localhost")

        self.assertContains(response, "Shanghai")
        self.assertContains(response, '#city-shanghai')
        self.assertContains(
            response,
            'href="https://example.com/register/shanghai"',
        )
        self.assertContains(
            response,
            'href="https://example.com/maps/shanghai"',
        )
        self.assertContains(response, 'class="city-map-link"', count=1)
        self.assertContains(response, 'class="home-city-register"', count=1)
