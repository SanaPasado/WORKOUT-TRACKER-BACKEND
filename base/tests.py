from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from base.models import (
	ChatMessage,
	DifficultyLevel,
	Exercise,
	ExerciseCategory,
	UserProfile,
)


class ExerciseApiTests(APITestCase):
	def setUp(self):
		self.exercise = Exercise.objects.create(
			exercise_name="Bench Press",
			description="A heavy compound pressing movement for upper-body strength.",
			category=ExerciseCategory.STRENGTH,
			difficulty_level=DifficultyLevel.MEDIUM,
			video_url="https://www.youtube.com/watch?v=tuwHzzPdaGc",
			muscle_groups_targeted="Chest, triceps, shoulders",
			equipment_needed="Barbell, bench",
		)

		self.free_user = User.objects.create_user(username="free", password="Password123!")
		self.premium_user = User.objects.create_user(username="premium", password="Password123!")
		self.admin_user = User.objects.create_user(
			username="admin",
			password="Password123!",
			is_staff=True,
		)

		UserProfile.objects.filter(user=self.premium_user).update(is_premium=True)

	def test_public_exercise_list_returns_basic_fields(self):
		response = self.client.get(reverse("exercise-list"))

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 1)
		self.assertSetEqual(
			set(response.data[0].keys()),
			{
				"id",
				"exercise_name",
				"category",
				"difficulty_level",
				"short_description",
				"video_url",
			},
		)

	def test_free_user_cannot_view_exercise_details(self):
		self.client.force_authenticate(user=self.free_user)

		response = self.client.get(reverse("exercise-detail", args=[self.exercise.id]))

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_premium_user_can_view_exercise_details(self):
		self.client.force_authenticate(user=self.premium_user)

		response = self.client.get(reverse("exercise-detail", args=[self.exercise.id]))

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data["exercise_name"], self.exercise.exercise_name)
		self.assertEqual(response.data["equipment_needed"], self.exercise.equipment_needed)

	def test_admin_can_create_exercise(self):
		self.client.force_authenticate(user=self.admin_user)
		payload = {
			"exercise_name": "Assault Bike Sprints",
			"description": "High-output intervals for anaerobic conditioning.",
			"category": ExerciseCategory.CARDIO,
			"difficulty_level": DifficultyLevel.HARD,
			"video_url": "https://youtu.be/bfLHTLQZ5nc",
			"muscle_groups_targeted": "Legs, lungs",
			"equipment_needed": "Assault bike",
		}

		response = self.client.post(reverse("exercise-list"), payload, format="json")

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertTrue(Exercise.objects.filter(exercise_name="Assault Bike Sprints").exists())

	def test_admin_create_rejects_non_youtube_url(self):
		self.client.force_authenticate(user=self.admin_user)
		payload = {
			"exercise_name": "Invalid Exercise",
			"description": "Should fail validation.",
			"category": ExerciseCategory.CARDIO,
			"difficulty_level": DifficultyLevel.EASY,
			"video_url": "https://vimeo.com/12345",
		}

		response = self.client.post(reverse("exercise-list"), payload, format="json")

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertIn("video_url", response.data)


class ChatApiTests(APITestCase):
	def setUp(self):
		self.free_user = User.objects.create_user(username="chatfree", password="Password123!")
		self.premium_user = User.objects.create_user(username="chatpremium", password="Password123!")
		UserProfile.objects.filter(user=self.premium_user).update(is_premium=True)
		self.chat_url = reverse("chat-view")
		self.history_url = reverse("chat-history")

	def _configure_gemini_mock(self, client_mock, reply_text="Mock coach reply"):
		instance = client_mock.return_value
		instance.models.generate_content.return_value = Mock(text=reply_text)

	def test_chat_requires_authentication(self):
		response = self.client.post(self.chat_url, {"message": "hello"}, format="json")
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	@patch("base.views.genai.Client")
	def test_free_user_limit_is_enforced(self, client_mock):
		self._configure_gemini_mock(client_mock)
		self.client.force_authenticate(user=self.free_user)

		conversation_id = None
		for attempt in range(5):
			payload = {"message": f"hello {attempt + 1}"}
			if conversation_id is not None:
				payload["conversation_id"] = conversation_id
			response = self.client.post(self.chat_url, payload, format="json")
			self.assertEqual(response.status_code, status.HTTP_200_OK)
			conversation_id = response.data["conversation_id"]
			self.assertEqual(response.data["remaining_free_messages"], 4 - attempt)

		blocked_response = self.client.post(
			self.chat_url,
			{"message": "message 6", "conversation_id": conversation_id},
			format="json",
		)
		self.assertEqual(blocked_response.status_code, status.HTTP_403_FORBIDDEN)
		self.assertEqual(blocked_response.data["remaining_free_messages"], 0)

		profile = UserProfile.objects.get(user=self.free_user)
		self.assertEqual(profile.free_chat_messages_used, 5)

	@patch("base.views.genai.Client")
	def test_chat_history_returns_saved_messages(self, client_mock):
		self._configure_gemini_mock(client_mock, reply_text="History reply")
		self.client.force_authenticate(user=self.free_user)

		chat_response = self.client.post(
			self.chat_url,
			{"message": "Build me a push day"},
			format="json",
		)
		self.assertEqual(chat_response.status_code, status.HTTP_200_OK)
		conversation_id = chat_response.data["conversation_id"]

		history_response = self.client.get(
			self.history_url,
			{"conversation_id": conversation_id},
		)
		self.assertEqual(history_response.status_code, status.HTTP_200_OK)
		self.assertEqual(history_response.data["active_conversation"]["id"], conversation_id)
		self.assertEqual(len(history_response.data["messages"]), 2)
		self.assertEqual(history_response.data["messages"][0]["role"], ChatMessage.ROLE_USER)
		self.assertEqual(history_response.data["messages"][1]["role"], ChatMessage.ROLE_ASSISTANT)

	@patch("base.views.genai.Client")
	def test_premium_user_has_unlimited_chat(self, client_mock):
		self._configure_gemini_mock(client_mock)
		self.client.force_authenticate(user=self.premium_user)

		for attempt in range(6):
			response = self.client.post(
				self.chat_url,
				{"message": f"premium {attempt + 1}"},
				format="json",
			)
			self.assertEqual(response.status_code, status.HTTP_200_OK)
			self.assertTrue(response.data["is_premium"])
			self.assertIsNone(response.data["remaining_free_messages"])

		profile = UserProfile.objects.get(user=self.premium_user)
		self.assertEqual(profile.free_chat_messages_used, 0)

	def test_login_response_includes_premium_flags(self):
		response = self.client.post(
			reverse("token_obtain_pair"),
			{"username": self.premium_user.username, "password": "Password123!"},
			format="json",
		)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertTrue(response.data["is_premium"])
		self.assertIsNone(response.data["remaining_free_messages"])
