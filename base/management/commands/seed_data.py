from django.core.management.base import BaseCommand

from base.models import DifficultyLevel, Exercise, ExerciseCategory


EXERCISE_SEED_DATA = [
    # Chest exercises
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
        "equipment_needed": "Cable machine, handles",
        "video_url": "https://youtu.be/eozdVDA78K0",
    },
    # Back exercises
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
        "exercise_name": "T-Bar Row",
        "description": "Strengthens the mid-back and lats with a stable chest-supported or landmine row setup.",
        "category": ExerciseCategory.STRENGTH,
        "difficulty_level": DifficultyLevel.MEDIUM,
        "muscle_groups_targeted": "Mid-back, lats, biceps",
        "equipment_needed": "T-bar row machine, landmine, barbell",
        "video_url": "https://youtu.be/j3Igk5nyZE4",
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
        "exercise_name": "Seated Cable Row",
        "description": "A horizontal pulling variation using the cable machine to target the back and biceps.",
        "category": ExerciseCategory.STRENGTH,
        "difficulty_level": DifficultyLevel.EASY,
        "muscle_groups_targeted": "Lats, rhomboids, posterior deltoids, biceps",
        "equipment_needed": "Cable machine, seat attachment",
        "video_url": "https://youtu.be/oT5mpUzkkAE",
    },
    # Leg exercises
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
        "exercise_name": "Leg Press",
        "description": "A machine-based lower-body press that helps build leg strength with added stability.",
        "category": ExerciseCategory.STRENGTH,
        "difficulty_level": DifficultyLevel.EASY,
        "muscle_groups_targeted": "Quadriceps, glutes, hamstrings",
        "equipment_needed": "Leg press machine",
        "video_url": "https://youtu.be/sEM_zo9w2ss",
    },
    {
        "exercise_name": "Romanian Deadlift",
        "description": "A hip-hinge variation that emphasizes hamstring and glute strength.",
        "category": ExerciseCategory.STRENGTH,
        "difficulty_level": DifficultyLevel.MEDIUM,
        "muscle_groups_targeted": "Hamstrings, glutes, lower back",
        "equipment_needed": "Barbell, weight plates",
        "video_url": "https://youtu.be/-m45n1_x32E",
    },
    {
        "exercise_name": "Leg Curl",
        "description": "An isolation exercise targeting hamstring development through knee flexion.",
        "category": ExerciseCategory.STRENGTH,
        "difficulty_level": DifficultyLevel.EASY,
        "muscle_groups_targeted": "Hamstrings",
        "equipment_needed": "Leg curl machine",
        "video_url": "https://youtu.be/3BWiLFc8Dbg",
    },
    {
        "exercise_name": "Walking Lunge",
        "description": "A unilateral lower-body movement that challenges stability and leg strength.",
        "category": ExerciseCategory.STRENGTH,
        "difficulty_level": DifficultyLevel.EASY,
        "muscle_groups_targeted": "Quadriceps, glutes, hamstrings",
        "equipment_needed": "Dumbbells (optional)",
        "video_url": "https://youtu.be/uRSsOoZG9z8",
    },
    {
        "exercise_name": "Leg Extension",
        "description": "An isolation exercise that targets the quadriceps through knee extension.",
        "category": ExerciseCategory.STRENGTH,
        "difficulty_level": DifficultyLevel.EASY,
        "muscle_groups_targeted": "Quadriceps",
        "equipment_needed": "Leg extension machine",
        "video_url": "https://youtu.be/YyvSXwIC_8o",
    },
    {
        "exercise_name": "Seated Calf Raise",
        "description": "A calf isolation exercise performed from a seated position for targeted development.",
        "category": ExerciseCategory.STRENGTH,
        "difficulty_level": DifficultyLevel.EASY,
        "muscle_groups_targeted": "Calves",
        "equipment_needed": "Calf raise machine or barbell",
        "video_url": "https://youtu.be/Yh5TXz99xwY",
    },
    {
        "exercise_name": "Standing Calf Raise",
        "description": "A standing calf exercise for building calf strength and definition.",
        "category": ExerciseCategory.STRENGTH,
        "difficulty_level": DifficultyLevel.EASY,
        "muscle_groups_targeted": "Calves",
        "equipment_needed": "Calf raise machine or dumbbells",
        "video_url": "https://youtu.be/I4CtoAiICYw",
    },
    # Shoulder exercises
    {
        "exercise_name": "Military Press",
        "description": "Builds shoulder and triceps strength while training full-body tension.",
        "category": ExerciseCategory.STRENGTH,
        "difficulty_level": DifficultyLevel.MEDIUM,
        "muscle_groups_targeted": "Shoulders, triceps, upper chest",
        "equipment_needed": "Barbell",
        "video_url": "https://youtu.be/j7ULT6dznNc",
    },
    {
        "exercise_name": "Dumbbell Lateral Raise",
        "description": "Isolates the lateral deltoids to build wider shoulders.",
        "category": ExerciseCategory.STRENGTH,
        "difficulty_level": DifficultyLevel.EASY,
        "muscle_groups_targeted": "Lateral deltoids, traps",
        "equipment_needed": "Dumbbells",
        "video_url": "https://youtu.be/3VcKaXpzMh8",
    },
    {
        "exercise_name": "Cable Upright Row",
        "description": "Uses a cable machine to target the shoulders and traps with constant tension.",
        "category": ExerciseCategory.STRENGTH,
        "difficulty_level": DifficultyLevel.EASY,
        "muscle_groups_targeted": "Lateral deltoids, traps, biceps",
        "equipment_needed": "Cable machine, bar or rope",
        "video_url": "https://youtu.be/kZpdmn_djFI",
    },
    {
        "exercise_name": "Rear Delt Fly",
        "description": "Develops the rear shoulders for better posture and upper-back balance.",
        "category": ExerciseCategory.STRENGTH,
        "difficulty_level": DifficultyLevel.EASY,
        "muscle_groups_targeted": "Rear deltoids, upper back",
        "equipment_needed": "Dumbbells or cable machine",
        "video_url": "https://youtu.be/Baavi8rJWBI",
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
    # Arm exercises
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
        "exercise_name": "Hammer Curl",
        "description": "A dumbbell curl variation that also targets the brachialis and forearms.",
        "category": ExerciseCategory.STRENGTH,
        "difficulty_level": DifficultyLevel.EASY,
        "muscle_groups_targeted": "Biceps, brachialis, forearms",
        "equipment_needed": "Dumbbells",
        "video_url": "https://youtu.be/ZdcFOgFi1Dg",
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
        "exercise_name": "Triceps Extension",
        "description": "A dumbbell triceps exercise performed with one arm overhead.",
        "category": ExerciseCategory.STRENGTH,
        "difficulty_level": DifficultyLevel.EASY,
        "muscle_groups_targeted": "Triceps",
        "equipment_needed": "Dumbbell",
        "video_url": "https://youtu.be/mpZ9VRisAyw",
    },
    {
        "exercise_name": "Overhead Triceps Extension",
        "description": "An isolation exercise that targets the triceps from an overhead position.",
        "category": ExerciseCategory.STRENGTH,
        "difficulty_level": DifficultyLevel.EASY,
        "muscle_groups_targeted": "Triceps",
        "equipment_needed": "Barbell or dumbbell",
        "video_url": "https://youtu.be/NRENeEgaIgA",
    },
    # Core exercises
    {
        "exercise_name": "Plank",
        "description": "A fundamental isometric core exercise that builds stability and endurance.",
        "category": ExerciseCategory.STRENGTH,
        "difficulty_level": DifficultyLevel.EASY,
        "muscle_groups_targeted": "Core, shoulders, upper back",
        "equipment_needed": "Bodyweight only",
        "video_url": "https://youtu.be/pSHjTRCQxIw",
    },
    {
        "exercise_name": "Plank to Hip Raise",
        "description": "A dynamic plank variation that engages the obliques and deep core muscles.",
        "category": ExerciseCategory.STRENGTH,
        "difficulty_level": DifficultyLevel.EASY,
        "muscle_groups_targeted": "Obliques, core",
        "equipment_needed": "Bodyweight only",
        "video_url": "https://youtu.be/9Wd3xH6-QYw",
    },
    {
        "exercise_name": "Weighted Crunch",
        "description": "Crunches performed with additional weight for increased core strength.",
        "category": ExerciseCategory.STRENGTH,
        "difficulty_level": DifficultyLevel.EASY,
        "muscle_groups_targeted": "Upper abdominals",
        "equipment_needed": "Dumbbell or cable machine",
        "video_url": "https://youtu.be/6kHg3JAFNFo",
    },
    {
        "exercise_name": "Cable Crunch",
        "description": "A cable machine crunch providing constant tension on the abdominals.",
        "category": ExerciseCategory.STRENGTH,
        "difficulty_level": DifficultyLevel.EASY,
        "muscle_groups_targeted": "Upper abdominals",
        "equipment_needed": "Cable machine, rope attachment",
        "video_url": "https://youtu.be/bmmJZN5B-4w",
    },
    {
        "exercise_name": "Dead Bug",
        "description": "An anti-rotation core exercise that improves coordination and stability.",
        "category": ExerciseCategory.STRENGTH,
        "difficulty_level": DifficultyLevel.EASY,
        "muscle_groups_targeted": "Core, hip flexors",
        "equipment_needed": "Bodyweight only",
        "video_url": "https://youtu.be/eEhoSeBFoBk",
    },
    # Cardio exercises
    {
        "exercise_name": "Treadmill Run",
        "description": "A foundational cardio exercise for building aerobic fitness and lower-body endurance.",
        "category": ExerciseCategory.CARDIO,
        "difficulty_level": DifficultyLevel.EASY,
        "muscle_groups_targeted": "Legs, cardiovascular system",
        "equipment_needed": "Treadmill",
        "video_url": "https://youtu.be/_kGESn8ArrU",
    },
    {
        "exercise_name": "Rowing Machine",
        "description": "A full-body cardio exercise that builds endurance and engages multiple muscle groups.",
        "category": ExerciseCategory.CARDIO,
        "difficulty_level": DifficultyLevel.MEDIUM,
        "muscle_groups_targeted": "Legs, back, shoulders, cardiovascular system",
        "equipment_needed": "Rowing ergometer",
        "video_url": "https://youtu.be/zQ82RYIFLN8",
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
]


class Command(BaseCommand):
    help = "Seed exercise library with comprehensive exercise data."

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
                defaults={
                    "description": item.get("description", ""),
                    "category": item["category"],
                    "difficulty_level": item["difficulty_level"],
                    "video_url": item["video_url"],
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
                f"Seed complete: {created_count} created, {updated_count} updated. "
                f"Total exercises in database: {Exercise.objects.count()}"
            )
        )
