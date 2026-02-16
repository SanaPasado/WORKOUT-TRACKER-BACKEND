from django.db import models
from django.contrib.auth.models import User


class Exercise(models.Model):
    """
    Exercise library entry.
    Can be a global exercise or created by a specific user.
    """

    DIFFICULTY_CHOICES = [
        ("easy", "Easy"),
        ("medium", "Medium"),
        ("hard", "Hard"),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    muscle_group = models.CharField(max_length=100, blank=True)  # e.g. "Chest", "Legs"
    equipment = models.CharField(max_length=100, blank=True)  # e.g. "Dumbbells", "Barbell"
    difficulty = models.CharField(
        max_length=10, choices=DIFFICULTY_CHOICES, default="medium"
    )
    is_public = models.BooleanField(
        default=True,
        help_text="If false, only the creator should see this exercise.",
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="exercises",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name
