from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0004_workoutlog"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="is_premium",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="premium_order_id",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="premium_provider",
            field=models.CharField(blank=True, default="", max_length=32),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="premium_since",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
