import uuid

import django.db.models.deletion
from django.db import migrations, models
from django.utils.text import slugify


def seed_conference_cities(apps, schema_editor):
    ConferenceCity = apps.get_model("base", "ConferenceCity")
    HomePage = apps.get_model("home", "HomePage")
    Page = apps.get_model("wagtailcore", "Page")
    Locale = apps.get_model("wagtailcore", "Locale")

    pages = {
        page.id: page
        for page in Page.objects.filter(id__in=HomePage.objects.values("page_ptr_id"))
    }
    homes_by_translation_key = {}
    for home in HomePage.objects.all():
        if not home.venue and not home.date:
            continue
        page = pages[home.page_ptr_id]
        homes_by_translation_key.setdefault(page.translation_key, []).append((home, page))

    for translation_key, homes in homes_by_translation_key.items():
        city_slug = ""
        for home, _page in homes:
            city_slug = slugify(home.venue or "")
            if city_slug:
                break
        city_slug = city_slug or f"city-{homes[0][0].page_ptr_id}"

        for home, page in homes:
            locale = Locale.objects.get(pk=page.locale_id)
            ConferenceCity.objects.create(
                translation_key=translation_key,
                locale=locale,
                name=home.venue or "Main City",
                slug=city_slug,
                venue=home.venue or "",
                start_date=home.date,
                end_date=home.date,
                position=10,
            )

        additional_translation_key = uuid.uuid4()
        for _home, page in homes:
            locale = Locale.objects.get(pk=page.locale_id)
            city_name = (
                "\u6df1\u5733"
                if locale.language_code.lower().startswith("zh")
                else "Shenzhen"
            )
            ConferenceCity.objects.create(
                translation_key=additional_translation_key,
                locale=locale,
                name=city_name,
                slug="shenzhen",
                position=20,
            )


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0003_update_pycon_2026_site_name"),
        ("home", "0007_alter_relatedlink_id"),
        ("wagtailcore", "0094_alter_page_locale"),
    ]

    operations = [
        migrations.CreateModel(
            name="ConferenceCity",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "translation_key",
                    models.UUIDField(default=uuid.uuid4, editable=False),
                ),
                ("name", models.CharField(max_length=64)),
                ("slug", models.SlugField(max_length=64)),
                ("venue", models.CharField(blank=True, max_length=255)),
                ("start_date", models.DateField(blank=True, null=True)),
                ("end_date", models.DateField(blank=True, null=True)),
                ("position", models.PositiveIntegerField(default=100)),
                (
                    "locale",
                    models.ForeignKey(
                        editable=False,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="wagtailcore.locale",
                        verbose_name="locale",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "conference cities",
                "ordering": ["position", "start_date", "name"],
                "unique_together": {("translation_key", "locale")},
                "constraints": [
                    models.UniqueConstraint(
                        fields=("locale", "slug"),
                        name="unique_conference_city_slug_per_locale",
                    )
                ],
            },
        ),
        migrations.RunPython(
            seed_conference_cities,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
