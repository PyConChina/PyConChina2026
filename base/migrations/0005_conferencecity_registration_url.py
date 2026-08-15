from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0004_conferencecity"),
    ]

    operations = [
        migrations.AddField(
            model_name="conferencecity",
            name="registration_url",
            field=models.URLField(blank=True),
        ),
    ]
