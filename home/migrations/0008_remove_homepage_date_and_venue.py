from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0004_conferencecity"),
        ("home", "0007_alter_relatedlink_id"),
    ]

    operations = [
        migrations.RemoveField(model_name="homepage", name="date"),
        migrations.RemoveField(model_name="homepage", name="venue"),
    ]
