from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from wagtail.images import get_image_model
from wagtail.models import Locale, Page

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
            )
        )
        draft_talk.authors.add(cls.draft_speaker)
        draft_talk.save()

    def test_get_speakers_only_returns_authors_with_live_talks(self):
        self.assertQuerySetEqual(
            self.home.get_speakers(),
            [self.second_speaker, self.first_speaker],
        )

    def test_get_speakers_deduplicates_authors_with_multiple_talks(self):
        speaker_ids = list(self.home.get_speakers().values_list("id", flat=True))

        self.assertEqual(speaker_ids.count(self.second_speaker.id), 1)
