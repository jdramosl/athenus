"""
Testing for the company API.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    ModelLLM,
    Company
)

from company.serializers import (
    ModelLLMSerializer,
)


LLM_MODELS_URL = reverse('company:modelllm-list')


def detail_url(llm_id):
    """Create and return a tag detail url."""
    return reverse('company:modelllm-detail', args=[llm_id])

def create_user(email="user@example.com", password="testpass123"):
    """Create and return a user."""
    return get_user_model().objects.create_user(email=email, password=password)

def create_company(user, **params):
    """Create and return a sample company."""
    defaults = {
        'name': 'Some Company',
        'description': 'It was founded in 1887',
        'address': '100 st. 1400',
        'city': 'Bogotá D.C.',
    }
    defaults.update(params)

    company = Company.objects.create(user=user, **defaults)
    return company

class PublicLLMModelApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()  # from drf

    def test_auth_required(self):
        """Test auth is required for retrieving LLM MODELS."""
        res = self.client.get(LLM_MODELS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateLLMModelApiTests(TestCase):
    """
    Test authenticated API requests.
    """

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_llm_models_unsuccessful_without_company(self):
        """Test retrieving a list of llm_models_unsuccessful_without_company."""
        company = create_company(user=self.user)

        ModelLLM.objects.create(
            company=company,
            name='Gemini',
            issuer='Google',
            base_url='Some URL Google',
        )

        ModelLLM.objects.create(
            company=company,
            name='Claude',
            issuer='OpenAI',
            base_url='Some URL Google',
        )

        res = self.client.get(LLM_MODELS_URL)

        llms = ModelLLM.objects.all().order_by("-name")

        serializer = ModelLLMSerializer(llms, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotEqual(res.data, serializer.data)


    def test_llm_models_limited_to_company(self):
        """Test list of llm models is limited to company."""
        # Create user
        user2 = create_user(email="user2@example.com")

        # Create Company 1 with default user
        company = create_company(user=self.user)

        # Create Company 2
        company2 = create_company(user=user2)

        ModelLLM.objects.create(
            company=company2,
            name='Gemini',
            issuer='Google',
            base_url='Some URL Google',
        )

        llm1 = ModelLLM.objects.create(
            company=company,
            name='Claude',
            issuer='OpenAI',
            base_url='Some URL Google'
        )

        # Testing that /tags/
        # endpoint lists only
        # tags for authenticated users.
        params = {'company': f'{company.id}'}
        res = self.client.get(LLM_MODELS_URL, params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Only 1 tag, the one we created with authenticated user.
        self.assertEqual(len(res.data), 1)

        self.assertEqual(res.data[0]["name"], llm1.name)
        # self.assertEqual(res.data[0]["id"], tag.id)
    #
    # def test_update_tag(self):
    #     """Test updating a tag."""
    #     # Original object name
    #     tag = Tag.objects.create(user=self.user, name="After dinner")
    #
    #     # Updating with patch
    #     payload = {"name": "Dessert"}
    #     url = detail_url(tag.id)
    #     res = self.client.patch(url, payload)
    #
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     tag.refresh_from_db()
    #     self.assertEqual(tag.name, payload["name"])
    #
    # def test_delete_tag(self):
    #     """Test deleting a tag."""
    #     tag = Tag.objects.create(user=self.user, name="Breakfast")
    #
    #     url = detail_url(tag.id)
    #     res = self.client.delete(url)
    #
    #     self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
    #     tags = Tag.objects.filter(user=self.user)
    #     # Since the user only created 1 tag and then we delete it, there shouldn't be any.  # noqa
    #     self.assertFalse(tags.exists())