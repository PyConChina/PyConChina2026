from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from search import views as search_views

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

translatable_patterns = [
    path("search/", search_views.search, name="search"),
    path("", include(wagtail_urls)),
]

urlpatterns = urlpatterns + [
    path(f"{settings.URL_PREFIX}documents/", include(wagtaildocs_urls)),
    path(f"{settings.URL_PREFIX}en/", include(translatable_patterns)),
    path(settings.URL_PREFIX, include(translatable_patterns)),
]
