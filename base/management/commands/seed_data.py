from django.core.management.base import BaseCommand

from base.models import DifficultyLevel, Exercise, ExerciseCategory


EXERCISE_SEED_DATA = [
    {
        "exercise_name": "Bench Press",
        "description": "A foundational upper-body push exercise for building chest, triceps, and pressing strength.",
        "category": ExerciseCategory.STRENGTH,
        "difficulty_level": DifficultyLevel.MEDIUM,
        "muscle_groups_targeted": "Chest, triceps, anterior deltoids",
        "equipment_needed": "Barbell, bench, weight plates",
        "video_url": "https://youtu.be/tuwHzzPdaGc",
    },
    {
        "exercise_name": "Dumbbell Bench Press",
        "description": "A chest press variation that improves unilateral strength and shoulder stability.",
        "category": ExerciseCategory.STRENGTH,
        "difficulty_level": DifficultyLevel.EASY,
        "muscle_groups_targeted": "Chest, triceps, anterior deltoids",
        "equipment_needed": "Dumbbells, flat bench",
        "video_url": "https://youtu.be/dGqI0Z5ul4k",
    },
    {
        "exercise_name": "Incline Dumbbell Press",
        "description": "Targets the upper chest while reinforcing shoulder-friendly pressing mechanics.",
        "category": ExerciseCategory.STRENGTH,
        "difficulty_level": DifficultyLevel.MEDIUM,
        "muscle_groups_targeted": "Upper chest, triceps, anterior deltoids",
        "equipment_needed": "Adjustable bench, dumbbells",
        "video_url": "https://youtu.be/8nNi8jbbUPE",
    },
    {
        "exercise_name": "Squat",
        "description": "A compound lower-body lift that trains leg drive, balance, and core bracing.",
        "category": ExerciseCategory.STRENGTH,
        "difficulty_level": DifficultyLevel.MEDIUM,
        "muscle_groups_targeted": "Quadriceps, glutes, core",
        "equipment_needed": "Barbell, squat rack",
        "video_url": "https://youtu.be/R2dMsNhN3DE",
    },
    {
        "exercise_name": "Deadlift",
        "description": "A full-body hinge pattern for posterior-chain strength and total-body power.",
        "category": ExerciseCategory.STRENGTH,
        "difficulty_level": DifficultyLevel.HARD,
        "muscle_groups_targeted": "Hamstrings, glutes, spinal erectors, lats",
        "equipment_needed": "Barbell, weight plates",
        "video_url": "https://youtu.be/CkrqLaDGvOA",
    },
    {
        "exercise_name": "Pull-Up",
        "description": "A vertical pulling exercise that strengthens the back, grip, and arms.",
        "category": ExerciseCategory.STRENGTH,
        "difficulty_level": DifficultyLevel.MEDIUM,
        "muscle_groups_targeted": "Lats, biceps, upper back",
        "equipment_needed": "Pull-up bar",
        "video_url": "https://youtu.be/eGo4IYlbE5g",
    },
    {
        "exercise_name": "Barbell Row",
        "description": "A horizontal pulling movement used to build back thickness and scapular control.",
        "category": ExerciseCategory.STRENGTH,
        "difficulty_level": DifficultyLevel.MEDIUM,
        "muscle_groups_targeted": "Lats, rhomboids, posterior deltoids, biceps",
        "equipment_needed": "Barbell, weight plates",
        "video_url": "https://youtu.be/paCfxhgW6bI",
    },
    {
        "exercise_name": "Overhead Press",
        "description": "Builds shoulder and triceps strength while training full-body tension.",
        "category": ExerciseCategory.STRENGTH,
        "difficulty_level": DifficultyLevel.MEDIUM,
        "muscle_groups_targeted": "Shoulders, triceps, upper chest",
        "equipment_needed": "Barbell or dumbbells",
        "video_url": "https://youtu.be/j7ULT6dznNc",
    },
    {
        "exercise_name": "Incline Dumbbell Curl",
        "description": "Isolates the biceps through a long range of motion to improve arm development.",
        "category": ExerciseCategory.STRENGTH,
        "difficulty_level": DifficultyLevel.EASY,
        "muscle_groups_targeted": "Biceps, forearms",
        "equipment_needed": "Adjustable bench, dumbbells",
        "video_url": "https://youtu.be/UeleXjsE-98",
    },
    {
        "exercise_name": "Cable Overhead Triceps Extension",
        "description": "Emphasizes the long head of the triceps using a controlled overhead cable path.",
        "category": ExerciseCategory.STRENGTH,
        "difficulty_level": DifficultyLevel.EASY,
        "muscle_groups_targeted": "Triceps",
        "equipment_needed": "Cable machine, rope attachment",
        "video_url": "https://youtu.be/VjmgzEmODnI",
    },
    {
        "exercise_name": "Leg Press",
        "description": "A machine-based lower-body press that helps build leg strength with added stability.",
        "category": ExerciseCategory.STRENGTH,
        "difficulty_level": DifficultyLevel.EASY,
        "muscle_groups_targeted": "Quadriceps, glutes, hamstrings",
        "equipment_needed": "Leg press machine",
        "video_url": "https://youtu.be/sEM_zo9w2ss",
    },
    {
        "exercise_name": "Lat Pulldown",
        "description": "A beginner-friendly vertical pull that develops the lats and upper back.",
        "category": ExerciseCategory.STRENGTH,
        "difficulty_level": DifficultyLevel.EASY,
        "muscle_groups_targeted": "Lats, biceps, upper back",
        "equipment_needed": "Lat pulldown machine",
        "video_url": "https://youtu.be/CAwf7n6Luuc",
    },
    {
        "exercise_name": "Push-Up",
        "description": "A bodyweight push exercise that builds upper-body endurance and core control.",
        "category": ExerciseCategory.STRENGTH,
        "difficulty_level": DifficultyLevel.EASY,
        "muscle_groups_targeted": "Chest, triceps, shoulders, core",
        "equipment_needed": "Bodyweight only",
        "video_url": "https://youtu.be/IODxDxX7oi4",
    },
    {
        "exercise_name": "Cable Chest Fly",
        "description": "An isolation movement that keeps constant tension on the chest through the full arc.",
        "category": ExerciseCategory.STRENGTH,
        "difficulty_level": DifficultyLevel.EASY,
        "muscle_groups_targeted": "Chest, anterior deltoids",
        "equipment_needed": "Cable machine",
        "video_url": "https://youtu.be/eozdVDA78K0",
    },
    {
        "exercise_name": "T-Bar Row",
        "description": "Strengthens the mid-back and lats with a stable chest-supported or landmine row setup.",
        "category": ExerciseCategory.STRENGTH,
        "difficulty_level": DifficultyLevel.MEDIUM,
        "muscle_groups_targeted": "Mid-back, lats, biceps",
        "equipment_needed": "T-bar row machine or landmine setup",
        "video_url": "https://youtu.be/j3Igk5nyZE4",
    },
    {
        "exercise_name": "Face Pull",
        "description": "Improves shoulder health and upper-back posture with a controlled pulling pattern.",
        "category": ExerciseCategory.STRENGTH,
        "difficulty_level": DifficultyLevel.EASY,
        "muscle_groups_targeted": "Rear deltoids, upper back, rotator cuff",
        "equipment_needed": "Cable machine, rope attachment",
        "video_url": "https://youtu.be/rep-qVOkqgk",
    },
    {
        "exercise_name": "World's Greatest Stretch",
        "description": "A dynamic mobility drill that opens the hips, thoracic spine, and hamstrings.",
        "category": ExerciseCategory.STRETCHING,
        "difficulty_level": DifficultyLevel.EASY,
        "muscle_groups_targeted": "Hip flexors, hamstrings, thoracic spine",
        "equipment_needed": "Bodyweight only",
        "video_url": "https://youtu.be/q4jSLLD5sQ8",
    },
    {
        "exercise_name": "Standing Hamstring Stretch",
        "description": "A simple flexibility drill for the posterior chain and lower-back tension relief.",
        "category": ExerciseCategory.FLEXIBILITY,
        "difficulty_level": DifficultyLevel.EASY,
        "muscle_groups_targeted": "Hamstrings, calves, lower back",
        "equipment_needed": "Bodyweight only",
        "video_url": "https://youtu.be/v7AYKMP6rOE",
    },
    {
        "exercise_name": "Jump Rope",
        "description": "A conditioning staple that improves footwork, coordination, and aerobic capacity.",
        "category": ExerciseCategory.CARDIO,
        "difficulty_level": DifficultyLevel.EASY,
        "muscle_groups_targeted": "Calves, shoulders, cardiovascular system",
        "equipment_needed": "Jump rope",
        "video_url": "https://youtu.be/1BZM4P0lzKg",
    },
    {
        "exercise_name": "Rowing Machine Intervals",
        "description": "Alternating hard and easy efforts on the erg to build aerobic power and stamina.",
        "category": ExerciseCategory.CARDIO,
        "difficulty_level": DifficultyLevel.MEDIUM,
        "muscle_groups_targeted": "Legs, back, cardiovascular system",
        "equipment_needed": "Rowing ergometer",
        "video_url": "https://youtu.be/zQ82RYIFLN8",
    },
    {
        "exercise_name": "Treadmill Tempo Run",
        "description": "A sustained moderate-hard run designed to improve pacing and endurance.",
        "category": ExerciseCategory.CARDIO,
        "difficulty_level": DifficultyLevel.MEDIUM,
        "muscle_groups_targeted": "Legs, cardiovascular system",
        "equipment_needed": "Treadmill",
        "video_url": "https://youtu.be/_kGESn8ArrU",
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
                exercise_name=item["exercise_name"],
                video_url=item["video_url"],
                defaults={
                    "description": item.get("description", ""),
                    "category": item["category"],
                    "difficulty_level": item["difficulty_level"],
                    "muscle_groups_targeted": item.get("muscle_groups_targeted", ""),
                    "equipment_needed": item.get("equipment_needed", ""),
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
