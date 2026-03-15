from django.db import migrations, models
import django.utils.timezone


def migrate_exercise_records(apps, schema_editor):
    Exercise = apps.get_model("base", "Exercise")

    category_map = {
        "CARDIO": "cardio",
        "CHEST": "strength",
        "BACK": "strength",
        "SHOULDERS": "strength",
        "ARMS": "strength",
        "LEGS": "strength",
        "CORE": "strength",
    }
    difficulty_map = {
        "BEGINNER": "easy",
        "INTERMEDIATE": "medium",
        "ADVANCED": "hard",
    }
    valid_hosts = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"}

    for exercise in Exercise._base_manager.order_by("pk").iterator():
        category_value = category_map.get(exercise.category, "strength")
        difficulty_value = difficulty_map.get(exercise.difficulty_level, "easy")
        video_url = (exercise.video_url or "").strip()

        if not video_url:
            exercise.delete()
            continue

        host = video_url.split("//", 1)[-1].split("/", 1)[0].lower()
        if host not in valid_hosts:
            exercise.delete()
            continue

        exercise.category = category_value
        exercise.difficulty_level = difficulty_value
        exercise.muscle_groups_targeted = (exercise.muscle_groups_targeted or "").strip()
        exercise.description = (exercise.description or "").strip()
        exercise.equipment_needed = (exercise.equipment_needed or "").strip()
        exercise.save(
            update_fields=[
                "category",
                "difficulty_level",
                "muscle_groups_targeted",
                "description",
                "equipment_needed",
                "video_url",
            ]
        )


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0005_userprofile_premium_fields"),
    ]

    operations = [
        migrations.RenameField(
            model_name="exercise",
            old_name="name",
            new_name="exercise_name",
        ),
        migrations.RenameField(
            model_name="exercise",
            old_name="difficulty",
            new_name="difficulty_level",
        ),
        migrations.RenameField(
            model_name="exercise",
            old_name="muscle_group",
            new_name="muscle_groups_targeted",
        ),
        migrations.RenameField(
            model_name="exercise",
            old_name="tutorial_url",
            new_name="video_url",
        ),
        migrations.AddField(
            model_name="exercise",
            name="description",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="exercise",
            name="equipment_needed",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="exercise",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="exercise",
            name="exercise_name",
            field=models.CharField(db_index=True, max_length=160),
        ),
        migrations.AlterField(
            model_name="exercise",
            name="muscle_groups_targeted",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.RunPython(migrate_exercise_records, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="exercise",
            name="category",
            field=models.CharField(
                choices=[
                    ("cardio", "Cardio"),
                    ("strength", "Strength"),
                    ("stretching", "Stretching"),
                    ("flexibility", "Flexibility"),
                ],
                db_index=True,
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="exercise",
            name="difficulty_level",
            field=models.CharField(
                choices=[("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard")],
                db_index=True,
                max_length=10,
            ),
        ),
        migrations.AlterField(
            model_name="exercise",
            name="video_url",
            field=models.URLField(),
        ),
        migrations.RemoveField(
            model_name="exercise",
            name="is_active",
        ),
        migrations.RemoveField(
            model_name="exercise",
            name="is_premium",
        ),
        migrations.AlterModelOptions(
            name="exercise",
            options={"ordering": ["exercise_name", "id"]},
        ),
        migrations.AddIndex(
            model_name="exercise",
            index=models.Index(fields=["category", "difficulty_level"], name="base_exerci_categor_7a8c2a_idx"),
        ),
    ]