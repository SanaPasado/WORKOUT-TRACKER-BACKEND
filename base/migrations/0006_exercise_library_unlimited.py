from django.db import migrations, models


FALLBACK_VIDEO_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


def migrate_exercise_values(apps, schema_editor):
    Exercise = apps.get_model("base", "Exercise")

    category_map = {
        "CARDIO": "cardio",
        "CHEST": "strength",
        "BACK": "strength",
        "SHOULDERS": "strength",
        "ARMS": "strength",
        "LEGS": "strength",
        "CORE": "flexibility",
        "cardio": "cardio",
        "strength": "strength",
        "stretching": "stretching",
        "flexibility": "flexibility",
    }

    difficulty_map = {
        "BEGINNER": "easy",
        "INTERMEDIATE": "medium",
        "ADVANCED": "hard",
        "EXPERT": "hard",
        "easy": "easy",
        "medium": "medium",
        "hard": "hard",
    }

    for exercise in Exercise.objects.all().iterator():
        updated_fields = []

        mapped_category = category_map.get((exercise.category or "").strip(), "strength")
        if exercise.category != mapped_category:
            exercise.category = mapped_category
            updated_fields.append("category")

        mapped_difficulty = difficulty_map.get((exercise.difficulty_level or "").strip(), "medium")
        if exercise.difficulty_level != mapped_difficulty:
            exercise.difficulty_level = mapped_difficulty
            updated_fields.append("difficulty_level")

        video_url = (exercise.video_url or "").strip()
        if not video_url:
            exercise.video_url = FALLBACK_VIDEO_URL
            updated_fields.append("video_url")

        if updated_fields:
            exercise.save(update_fields=updated_fields)


def noop_reverse(apps, schema_editor):
    return


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
        migrations.RunPython(migrate_exercise_values, noop_reverse),
        migrations.AlterField(
            model_name="exercise",
            name="exercise_name",
            field=models.CharField(max_length=120),
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
                choices=[
                    ("easy", "Easy"),
                    ("medium", "Medium"),
                    ("hard", "Hard"),
                ],
                max_length=10,
            ),
        ),
        migrations.AlterField(
            model_name="exercise",
            name="video_url",
            field=models.URLField(),
        ),
        migrations.AlterField(
            model_name="exercise",
            name="muscle_groups_targeted",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterModelOptions(
            name="exercise",
            options={"ordering": ["exercise_name"]},
        ),
    ]
