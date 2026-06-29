from django.db import migrations


OLD_SITE_NAME = "PyCon China 2025"
NEW_SITE_NAME = "PyCon China 2026"


def update_site_name(apps, schema_editor):
    Site = apps.get_model("wagtailcore", "Site")
    Site.objects.filter(site_name=OLD_SITE_NAME).update(site_name=NEW_SITE_NAME)


def restore_site_name(apps, schema_editor):
    Site = apps.get_model("wagtailcore", "Site")
    Site.objects.filter(site_name=NEW_SITE_NAME).update(site_name=OLD_SITE_NAME)


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0002_remove_navigationsettings_github_url_and_more"),
    ]

    operations = [
        migrations.RunPython(update_site_name, restore_site_name),
    ]
