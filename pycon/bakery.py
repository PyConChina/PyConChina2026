from __future__ import annotations

from pathlib import Path
from urllib.parse import unquote, urlparse

from bakery.views import BuildableMixin
from django.conf import settings
from wagtail.models import Page
from wagtail.documents import get_document_model
from wagtailbakery.views import AllPublishedPagesView


class LocalizedAllPublishedPagesView(AllPublishedPagesView):
    def get_queryset(self):
        return Page.objects.all().public().live()

    def get_url(self, obj):
        url = super().get_url(obj)
        if not url:
            return url

        language_code = obj.locale.language_code
        if language_code == settings.LANGUAGE_CODE:
            return url

        prefix = f"/{settings.URL_PREFIX}"
        language_prefix = f"{prefix}{language_code}/"
        if url == prefix:
            return language_prefix
        if url.startswith(prefix):
            return url.replace(prefix, language_prefix, 1)
        return url


class AllDocumentsView(BuildableMixin):
    @property
    def build_method(self):
        return self.build_queryset

    def get_queryset(self):
        return get_document_model().objects.all()

    def get_build_path(self, obj):
        path = unquote(urlparse(obj.url).path.lstrip("/"))
        return Path(settings.BUILD_DIR) / path

    def build_object(self, obj):
        target_path = self.get_build_path(obj)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with obj.file.open("rb") as source, target_path.open("wb") as target:
            target.write(source.read())

    def build_queryset(self):
        for obj in self.get_queryset():
            self.build_object(obj)
