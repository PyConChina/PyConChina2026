import uuid

import django.db.models.deletion
from django.db import migrations, models


def assign_talk_cities(apps, schema_editor):
    ConferenceCity = apps.get_model("base", "ConferenceCity")
    Locale = apps.get_model("wagtailcore", "Locale")
    Page = apps.get_model("wagtailcore", "Page")
    TalkPage = apps.get_model("talk", "TalkPage")

    city_by_locale = {}
    for city in ConferenceCity.objects.order_by("position", "id"):
        city_by_locale.setdefault(city.locale_id, city)
    pages = {
        page.id: page
        for page in Page.objects.filter(id__in=TalkPage.objects.values("page_ptr_id"))
    }

    for talk in TalkPage.objects.all():
        locale_id = pages[talk.page_ptr_id].locale_id
        city = city_by_locale.get(locale_id)
        if city is None:
            locale = Locale.objects.get(pk=locale_id)
            city = ConferenceCity.objects.create(
                translation_key=uuid.uuid4(),
                locale=locale,
                name="Main City",
                slug="main-city",
                position=10,
            )
            city_by_locale[locale_id] = city
        talk.city_id = city.id
        talk.save(update_fields=["city"])


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0004_conferencecity"),
        ("talk", "0009_alter_author_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="talkpage",
            name="city",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="talks",
                to="base.conferencecity",
            ),
        ),
        migrations.RunPython(assign_talk_cities, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="talkpage",
            name="city",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="talks",
                to="base.conferencecity",
            ),
        ),
    ]
