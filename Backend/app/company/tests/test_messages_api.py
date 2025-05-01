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
    Message,
    Company
)

from company.serializers import (
    ModelLLMSerializer,
    MessageSerializer
)


MESSAGES_URL = reverse('company:message-list')


def detail_url(message_id):
    """Create and return a tag detail url."""
    return reverse('company:message-detail', args=[message_id])

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

class PublicMessageApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()  # from drf

    def test_auth_required(self):
        """Test auth is required for retrieving messages."""
        res = self.client.get(MESSAGES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateMessageApiTests(TestCase):
    """
    Test authenticated API requests.
    """
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_llm_models_messages(self):
        """Test retrieving a list of messages."""
        # 1. Company
        company = create_company(user=self.user)

        # 2. LLM models
        model1 = ModelLLM.objects.create(
            company=company,
            name='Gemini',
            issuer='Google',
            base_url='Some URL Google',
        )
        model2 = ModelLLM.objects.create(
            company=company,
            name='Claude',
            issuer='OpenAI',
            base_url='Some URL Google',
        )

        # 3. Messages, creation straight into db
        message = Message.objects.create(
            role='User',
            message='Why the sky is blue?',
            model=model1,
            user=self.user
        )
        # Database Messages
        messages = Message.objects.all().order_by('-created_at')
        serializer = MessageSerializer(messages, many=True)

        # Request to API
        res = self.client.get(MESSAGES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
