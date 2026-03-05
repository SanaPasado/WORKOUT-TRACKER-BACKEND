from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Exercise, UserProfile


class ExercisePermissionsAPITests(APITestCase):
	def setUp(self):
		self.user_model = get_user_model()
		self.default_password = "StrongPass123!"

		self.free_user = self.user_model.objects.create_user(
			username="freeuser",
			email="free@example.com",
			password=self.default_password,
		)
		self.premium_user = self.user_model.objects.create_user(
			username="premiumuser",
			email="premium@example.com",
			password=self.default_password,
		)
		self.admin_user = self.user_model.objects.create_user(
			username="adminuser",
			email="admin@example.com",
			password=self.default_password,
			is_staff=True,
		)

		# Profile is auto-created by signal, then we mark premium entitlement.
		premium_profile = UserProfile.objects.get(user=self.premium_user)
		premium_profile.is_premium = True
		premium_profile.save(update_fields=["is_premium"])

		self.exercise = Exercise.objects.create(
			exercise_name="Bodyweight Squat",
			description="Lower with control and keep your chest tall.",
			category="strength",
			difficulty_level="easy",
			video_url="https://www.youtube.com/watch?v=aclHkVaku9U",
			muscle_groups_targeted="Quads, Glutes",
			equipment_needed="None",
			is_premium=True,
		)

	def authenticate_via_jwt(self, username):
		login_response = self.client.post(
			reverse("token_obtain_pair"),
			{"username": username, "password": self.default_password},
			format="json",
		)
		self.assertEqual(login_response.status_code, status.HTTP_200_OK)
		access_token = login_response.data["access"]
		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

	def test_public_user_can_list_exercises_with_basic_fields_only(self):
		response = self.client.get(reverse("exercise-list"))

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 1)

		payload = response.data[0]
		self.assertIn("exercise_name", payload)
		self.assertIn("category", payload)
		self.assertIn("difficulty_level", payload)
		self.assertIn("short_description", payload)
		self.assertIn("video_url", payload)
		self.assertNotIn("description", payload)
		self.assertNotIn("muscle_groups_targeted", payload)
		self.assertNotIn("equipment_needed", payload)

	def test_anonymous_user_cannot_access_premium_exercise_details(self):
		response = self.client.get(reverse("exercise-detail", args=[self.exercise.id]))
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_free_user_cannot_access_premium_exercise_details(self):
		self.authenticate_via_jwt("freeuser")

		response = self.client.get(reverse("exercise-detail", args=[self.exercise.id]))

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_premium_user_can_access_full_exercise_details(self):
		self.authenticate_via_jwt("premiumuser")

		response = self.client.get(reverse("exercise-detail", args=[self.exercise.id]))

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertIn("description", response.data)
		self.assertIn("muscle_groups_targeted", response.data)
		self.assertIn("equipment_needed", response.data)
		self.assertEqual(response.data["exercise_name"], "Bodyweight Squat")

	def test_admin_can_create_update_and_delete_exercise(self):
		self.authenticate_via_jwt("adminuser")

		create_payload = {
			"exercise_name": "Jump Rope Intervals",
			"description": "Alternate pace every 30 seconds.",
			"category": "cardio",
			"difficulty_level": "medium",
			"video_url": "https://www.youtube.com/watch?v=1BZM6E4wLjM",
			"muscle_groups_targeted": "Calves, Shoulders",
			"equipment_needed": "Jump rope",
			"is_premium": False,
		}

		create_response = self.client.post(
			reverse("exercise-create"),
			create_payload,
			format="json",
		)
		self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

		created_id = create_response.data["id"]
		update_response = self.client.patch(
			reverse("exercise-update", args=[created_id]),
			{"difficulty_level": "hard"},
			format="json",
		)
		self.assertEqual(update_response.status_code, status.HTTP_200_OK)
		self.assertEqual(update_response.data["difficulty_level"], "hard")

		delete_response = self.client.delete(reverse("exercise-delete", args=[created_id]))
		self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
		self.assertFalse(Exercise.objects.filter(id=created_id).exists())

	def test_non_admin_cannot_create_update_or_delete_exercise(self):
		self.authenticate_via_jwt("freeuser")

		create_response = self.client.post(
			reverse("exercise-create"),
			{
				"exercise_name": "Mountain Climbers",
				"category": "cardio",
				"difficulty_level": "medium",
				"video_url": "https://www.youtube.com/watch?v=nmwgirgXLYM",
			},
			format="json",
		)
		self.assertEqual(create_response.status_code, status.HTTP_403_FORBIDDEN)

		update_response = self.client.patch(
			reverse("exercise-update", args=[self.exercise.id]),
			{"difficulty_level": "hard"},
			format="json",
		)
		self.assertEqual(update_response.status_code, status.HTTP_403_FORBIDDEN)

		delete_response = self.client.delete(reverse("exercise-delete", args=[self.exercise.id]))
		self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)

	def test_admin_create_rejects_non_youtube_video_url(self):
		self.authenticate_via_jwt("adminuser")

		response = self.client.post(
			reverse("exercise-create"),
			{
				"exercise_name": "Bad URL Exercise",
				"category": "strength",
				"difficulty_level": "easy",
				"video_url": "https://vimeo.com/12345",
			},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertIn("video_url", response.data)
