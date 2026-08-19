from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0005_conferencecity_registration_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="conferencecity",
            name="map_url",
            field=models.URLField(
                blank=True,
                help_text="Link to the venue in a map service",
            ),
        ),
    ]
