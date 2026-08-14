import uuid

import django.db.models.deletion
from django.db import migrations, models


def assign_schedule_cities(apps, schema_editor):
    ConferenceCity = apps.get_model("base", "ConferenceCity")
    Locale = apps.get_model("wagtailcore", "Locale")
    Page = apps.get_model("wagtailcore", "Page")
    Schedule = apps.get_model("schedule", "Schedule")

    city_by_locale = {}
    for city in ConferenceCity.objects.order_by("position", "id"):
        city_by_locale.setdefault(city.locale_id, city)
    page_ids = Schedule.objects.values_list("page_id", flat=True).distinct()
    pages = {page.id: page for page in Page.objects.filter(id__in=page_ids)}

    for schedule in Schedule.objects.all():
        locale_id = pages[schedule.page_id].locale_id
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
        schedule.city_id = city.id
        schedule.save(update_fields=["city"])


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0004_conferencecity"),
        ("schedule", "0006_alter_room_id_alter_schedule_id"),
        ("talk", "0010_talkpage_city"),
    ]

    operations = [
        migrations.AddField(
            model_name="schedule",
            name="city",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="schedules",
                to="base.conferencecity",
            ),
        ),
        migrations.RunPython(assign_schedule_cities, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="schedule",
            name="city",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="schedules",
                to="base.conferencecity",
            ),
        ),
    ]
