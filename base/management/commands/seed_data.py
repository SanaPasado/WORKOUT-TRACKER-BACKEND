from django.core.management.base import BaseCommand

from base.models import Difficulty, Exercise, ExerciseCategory


EXERCISE_SEED_DATA = [
    {
        "exercise_name": "Jump Rope Intervals",
        "description": "Perform alternating fast and moderate jump-rope rounds to improve cardio conditioning.",
        "category": ExerciseCategory.CARDIO,
        "difficulty_level": Difficulty.MEDIUM,
        "video_url": "https://www.youtube.com/watch?v=1BZM6E4wLjM",
        "muscle_groups_targeted": "Calves, Shoulders, Core",
        "equipment_needed": "Jump rope",
        "is_premium": False,
    },
    {
        "exercise_name": "Bodyweight Squat",
        "description": "Keep your chest tall and knees tracking over toes while lowering with control.",
        "category": ExerciseCategory.STRENGTH,
        "difficulty_level": Difficulty.EASY,
        "video_url": "https://www.youtube.com/watch?v=aclHkVaku9U",
        "muscle_groups_targeted": "Quads, Glutes, Core",
        "equipment_needed": "None",
        "is_premium": False,
    },
    {
        "exercise_name": "Romanian Deadlift",
        "description": "Hinge from the hips with a neutral spine to load the hamstrings effectively.",
        "category": ExerciseCategory.STRENGTH,
        "difficulty_level": Difficulty.HARD,
        "video_url": "https://www.youtube.com/watch?v=2SHsk9AzdjA",
        "muscle_groups_targeted": "Hamstrings, Glutes, Lower Back",
        "equipment_needed": "Barbell or dumbbells",
        "is_premium": True,
    },
    {
        "exercise_name": "Seated Hamstring Stretch",
        "description": "Sit tall and reach forward gently, maintaining a long spine for a hamstring stretch.",
        "category": ExerciseCategory.STRETCHING,
        "difficulty_level": Difficulty.EASY,
        "video_url": "https://www.youtube.com/watch?v=vZfK-9W4QzI",
        "muscle_groups_targeted": "Hamstrings, Calves",
        "equipment_needed": "Mat",
        "is_premium": False,
    },
    {
        "exercise_name": "Shoulder Mobility Flow",
        "description": "Controlled shoulder circles and band work to improve range of motion.",
        "category": ExerciseCategory.FLEXIBILITY,
        "difficulty_level": Difficulty.MEDIUM,
        "video_url": "https://www.youtube.com/watch?v=JOLHu9rI2vY",
        "muscle_groups_targeted": "Deltoids, Upper Back",
        "equipment_needed": "Light resistance band",
        "is_premium": True,
    },
]


class Command(BaseCommand):
    help = "Seed initial exercise library data"

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        for item in EXERCISE_SEED_DATA:
            _, created = Exercise.objects.update_or_create(
                exercise_name=item["exercise_name"],
                defaults=item,
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Exercise seed complete: {created_count} created, {updated_count} updated."
            )
        )
