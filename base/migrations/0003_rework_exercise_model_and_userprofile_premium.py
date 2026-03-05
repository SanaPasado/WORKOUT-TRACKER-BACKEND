from django.db import migrations, models


def normalize_exercise_data(apps, schema_editor):
    Exercise = apps.get_model("base", "Exercise")

    category_map = {
        "CHEST": "strength",
        "BACK": "strength",
        "SHOULDERS": "strength",
        "ARMS": "strength",
        "LEGS": "strength",
        "CORE": "strength",
        "CARDIO": "cardio",
        "cardio": "cardio",
        "strength": "strength",
        "stretching": "stretching",
        "flexibility": "flexibility",
    }

    difficulty_map = {
        "BEGINNER": "easy",
        "INTERMEDIATE": "medium",
        "ADVANCED": "hard",
        "easy": "easy",
        "medium": "medium",
        "hard": "hard",
    }

    fallback_video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    for exercise in Exercise.objects.all():
        exercise.category = category_map.get(exercise.category, "strength")
        exercise.difficulty_level = difficulty_map.get(exercise.difficulty_level, "medium")
        if not exercise.video_url:
            exercise.video_url = fallback_video_url
        exercise.save(update_fields=["category", "difficulty_level", "video_url"])


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0002_exercise_tutorial_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="is_premium",
            field=models.BooleanField(default=False),
        ),
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
        migrations.AlterModelOptions(
            name="exercise",
            options={"ordering": ["exercise_name"]},
        ),
        migrations.AlterField(
            model_name="exercise",
            name="description",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="exercise",
            name="equipment_needed",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
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
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="exercise",
            name="difficulty_level",
            field=models.CharField(
                choices=[("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard")],
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="exercise",
            name="muscle_groups_targeted",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.RunPython(normalize_exercise_data, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="exercise",
            name="video_url",
            field=models.URLField(),
        ),
        migrations.RemoveField(
            model_name="exercise",
            name="created_at",
        ),
        migrations.RemoveField(
            model_name="exercise",
            name="is_active",
        ),
    ]
