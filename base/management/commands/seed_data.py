from django.core.management.base import BaseCommand

from base.models import Difficulty, Exercise, ExerciseCategory


EXERCISE_SEED_DATA = [
    {
        "name": "Bench Press",
        "category": ExerciseCategory.CHEST,
        "difficulty": Difficulty.INTERMEDIATE,
        "muscle_group": "Chest, Triceps, Front Delts",
        "is_premium": False,
        "tutorial_url": "https://youtu.be/tuwHzzPdaGc",
    },
    {
        "name": "Dumbbell Bench Press",
        "category": ExerciseCategory.CHEST,
        "difficulty": Difficulty.BEGINNER,
        "muscle_group": "Chest, Triceps, Front Delts",
        "is_premium": False,
        "tutorial_url": "https://youtu.be/dGqI0Z5ul4k",
    },
    {
        "name": "Incline Dumbbell Press",
        "category": ExerciseCategory.CHEST,
        "difficulty": Difficulty.INTERMEDIATE,
        "muscle_group": "Upper Chest, Triceps, Front Delts",
        "is_premium": False,
        "tutorial_url": "https://youtu.be/8nNi8jbbUPE",
    },
    {
        "name": "Squat",
        "category": ExerciseCategory.LEGS,
        "difficulty": Difficulty.INTERMEDIATE,
        "muscle_group": "Quads, Glutes, Core",
        "is_premium": False,
        "tutorial_url": "https://youtu.be/R2dMsNhN3DE",
    },
    {
        "name": "Deadlift",
        "category": ExerciseCategory.BACK,
        "difficulty": Difficulty.ADVANCED,
        "muscle_group": "Back, Hamstrings, Glutes",
        "is_premium": True,
        "tutorial_url": "https://youtu.be/CkrqLaDGvOA",
    },
    {
        "name": "Pull-ups",
        "category": ExerciseCategory.BACK,
        "difficulty": Difficulty.INTERMEDIATE,
        "muscle_group": "Lats, Biceps, Upper Back",
        "is_premium": False,
        "tutorial_url": "https://youtu.be/iKrKgWR9wbY",
    },
    {
        "name": "Barbell Row",
        "category": ExerciseCategory.BACK,
        "difficulty": Difficulty.INTERMEDIATE,
        "muscle_group": "Lats, Rhomboids, Biceps",
        "is_premium": False,
        "tutorial_url": "https://youtu.be/paCfxhgW6bI",
    },
    {
        "name": "Military Press",
        "category": ExerciseCategory.SHOULDERS,
        "difficulty": Difficulty.INTERMEDIATE,
        "muscle_group": "Shoulders, Triceps, Upper Chest",
        "is_premium": False,
        "tutorial_url": "https://youtu.be/j7ULT6dznNc",
    },
    {
        "name": "Incline Dumbbell Curl",
        "category": ExerciseCategory.ARMS,
        "difficulty": Difficulty.BEGINNER,
        "muscle_group": "Biceps, Forearms",
        "is_premium": False,
        "tutorial_url": "https://youtu.be/UeleXjsE-98",
    },
    {
        "name": "Overhead Tricep Extension (Cable)",
        "category": ExerciseCategory.ARMS,
        "difficulty": Difficulty.BEGINNER,
        "muscle_group": "Triceps",
        "is_premium": False,
        "tutorial_url": "https://youtu.be/VjmgzEmODnI",
    },
    {
        "name": "Leg Press",
        "category": ExerciseCategory.LEGS,
        "difficulty": Difficulty.BEGINNER,
        "muscle_group": "Quads, Glutes, Hamstrings",
        "is_premium": False,
        "tutorial_url": "https://youtu.be/sEM_zo9w2ss",
    },
    {
        "name": "Lat Pulldown",
        "category": ExerciseCategory.BACK,
        "difficulty": Difficulty.BEGINNER,
        "muscle_group": "Lats, Biceps, Upper Back",
        "is_premium": False,
        "tutorial_url": "https://youtu.be/iKrKgWR9wbY",
    },
    {
        "name": "Push-up",
        "category": ExerciseCategory.CHEST,
        "difficulty": Difficulty.BEGINNER,
        "muscle_group": "Chest, Triceps, Shoulders, Core",
        "is_premium": False,
        "tutorial_url": "https://youtu.be/KEFQyLkDYtI",
    },
    {
        "name": "Cable Chest Fly",
        "category": ExerciseCategory.CHEST,
        "difficulty": Difficulty.BEGINNER,
        "muscle_group": "Chest, Front Delts",
        "is_premium": False,
        "tutorial_url": "https://youtu.be/JHqmhZ12rr0",
    },
    {
        "name": "T-Bar Row",
        "category": ExerciseCategory.BACK,
        "difficulty": Difficulty.INTERMEDIATE,
        "muscle_group": "Mid Back, Lats, Biceps",
        "is_premium": True,
        "tutorial_url": "https://youtu.be/kHW23afzaUs",
    },
    {
        "name": "Face Pull",
        "category": ExerciseCategory.SHOULDERS,
        "difficulty": Difficulty.BEGINNER,
        "muscle_group": "Rear Delts, Upper Back, Rotator Cuff",
        "is_premium": False,
        "tutorial_url": "https://youtu.be/7ZvpXA_mFpQ",
    },
    {
        "name": "Cable Upright Row",
        "category": ExerciseCategory.SHOULDERS,
        "difficulty": Difficulty.BEGINNER,
        "muscle_group": "Side Delts, Traps",
        "is_premium": False,
        "tutorial_url": "https://youtu.be/kZpdmn_djFI",
    },
    {
        "name": "Rear Delt Fly",
        "category": ExerciseCategory.SHOULDERS,
        "difficulty": Difficulty.BEGINNER,
        "muscle_group": "Rear Delts, Upper Back",
        "is_premium": False,
        "tutorial_url": "https://youtu.be/Baavi8rJWBI",
    },
    {
        "name": "Hammer Preacher Curl",
        "category": ExerciseCategory.ARMS,
        "difficulty": Difficulty.BEGINNER,
        "muscle_group": "Biceps, Brachialis, Forearms",
        "is_premium": False,
        "tutorial_url": "https://youtu.be/ZdcFOgFi1Dg",
    },
    {
        "name": "Tricep Extension",
        "category": ExerciseCategory.ARMS,
        "difficulty": Difficulty.BEGINNER,
        "muscle_group": "Triceps",
        "is_premium": False,
        "tutorial_url": "https://youtu.be/mpZ9VRisAyw",
    },
    {
        "name": "Overhead Tricep Extension",
        "category": ExerciseCategory.ARMS,
        "difficulty": Difficulty.BEGINNER,
        "muscle_group": "Triceps",
        "is_premium": False,
        "tutorial_url": "https://youtu.be/NRENeEgaIgA",
    },
    {
        "name": "Romanian Deadlift",
        "category": ExerciseCategory.LEGS,
        "difficulty": Difficulty.INTERMEDIATE,
        "muscle_group": "Hamstrings, Glutes, Lower Back",
        "is_premium": False,
        "tutorial_url": "https://youtu.be/-m45n1_x32E",
    },
    {
        "name": "Leg Curl",
        "category": ExerciseCategory.LEGS,
        "difficulty": Difficulty.BEGINNER,
        "muscle_group": "Hamstrings",
        "is_premium": False,
        "tutorial_url": "https://youtu.be/3BWiLFc8Dbg",
    },
    {
        "name": "Walking Lunge",
        "category": ExerciseCategory.LEGS,
        "difficulty": Difficulty.BEGINNER,
        "muscle_group": "Quads, Glutes, Hamstrings",
        "is_premium": False,
        "tutorial_url": "https://youtu.be/uRSsOoZG9z8",
    },
    {
        "name": "Seated Calf Raise",
        "category": ExerciseCategory.LEGS,
        "difficulty": Difficulty.BEGINNER,
        "muscle_group": "Calves",
        "is_premium": False,
        "tutorial_url": "https://youtu.be/Yh5TXz99xwY",
    },
    {
        "name": "Dead Bug",
        "category": ExerciseCategory.CORE,
        "difficulty": Difficulty.BEGINNER,
        "muscle_group": "Core, Hip Flexors",
        "is_premium": False,
        "tutorial_url": "https://youtu.be/eEhoSeBFoBk",
    },
    {
        "name": "Plank to Hip Raise",
        "category": ExerciseCategory.CORE,
        "difficulty": Difficulty.BEGINNER,
        "muscle_group": "Obliques, Core",
        "is_premium": False,
        "tutorial_url": "https://youtu.be/9Wd3xH6-QYw",
    },
    {
        "name": "Weighted Crunch",
        "category": ExerciseCategory.CORE,
        "difficulty": Difficulty.BEGINNER,
        "muscle_group": "Upper Abs",
        "is_premium": False,
        "tutorial_url": "https://youtu.be/6kHg3JAFNFo",
    },
    {
        "name": "Dumbbell Lateral Raise",
        "category": ExerciseCategory.SHOULDERS,
        "difficulty": Difficulty.BEGINNER,
        "muscle_group": "Side Delts, Traps",
        "is_premium": False,
        "tutorial_url": None,
    },
    {
        "name": "Standing Calf Raise",
        "category": ExerciseCategory.LEGS,
        "difficulty": Difficulty.BEGINNER,
        "muscle_group": "Calves",
        "is_premium": False,
        "tutorial_url": None,
    },
    {
        "name": "Plank",
        "category": ExerciseCategory.CORE,
        "difficulty": Difficulty.BEGINNER,
        "muscle_group": "Core, Shoulders",
        "is_premium": False,
        "tutorial_url": None,
    },
    {
        "name": "Cable Crunch",
        "category": ExerciseCategory.CORE,
        "difficulty": Difficulty.BEGINNER,
        "muscle_group": "Upper Abs",
        "is_premium": False,
        "tutorial_url": None,
    },
    {
        "name": "Seated Cable Row",
        "category": ExerciseCategory.BACK,
        "difficulty": Difficulty.BEGINNER,
        "muscle_group": "Lats, Rhomboids, Rear Delts",
        "is_premium": False,
        "tutorial_url": None,
    },
    {
        "name": "Hammer Curl",
        "category": ExerciseCategory.ARMS,
        "difficulty": Difficulty.BEGINNER,
        "muscle_group": "Biceps, Brachialis, Forearms",
        "is_premium": False,
        "tutorial_url": None,
    },
    {
        "name": "Leg Extension",
        "category": ExerciseCategory.LEGS,
        "difficulty": Difficulty.BEGINNER,
        "muscle_group": "Quads",
        "is_premium": False,
        "tutorial_url": None,
    },
    {
        "name": "Treadmill Run",
        "category": ExerciseCategory.CARDIO,
        "difficulty": Difficulty.BEGINNER,
        "muscle_group": "Cardiovascular System, Legs",
        "is_premium": False,
        "tutorial_url": None,
    },
    {
        "name": "Rowing Machine",
        "category": ExerciseCategory.CARDIO,
        "difficulty": Difficulty.INTERMEDIATE,
        "muscle_group": "Cardiovascular System, Back, Legs",
        "is_premium": False,
        "tutorial_url": None,
    },
    {
        "name": "Jump Rope",
        "category": ExerciseCategory.CARDIO,
        "difficulty": Difficulty.BEGINNER,
        "muscle_group": "Cardiovascular System, Calves, Shoulders",
        "is_premium": False,
        "tutorial_url": None,
    },
]


class Command(BaseCommand):
    help = "Seed base app data (exercise library) from frontend dummy lists."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing exercises before seeding.",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            deleted_count, _ = Exercise.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Deleted {deleted_count} exercise rows."))

        created_count = 0
        updated_count = 0

        for item in EXERCISE_SEED_DATA:
            _, created = Exercise.objects.update_or_create(
                name=item["name"],
                defaults={
                    "category": item["category"],
                    "difficulty": item["difficulty"],
                    "muscle_group": item["muscle_group"],
                    "tutorial_url": item.get("tutorial_url"),
                    "is_premium": item["is_premium"],
                    "is_active": True,
                },
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed complete: {created_count} created, {updated_count} updated, total={Exercise.objects.count()}"
            )
        )
