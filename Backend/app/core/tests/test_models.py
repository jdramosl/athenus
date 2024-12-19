"""
Tests for models.
"""
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def create_user(email='user@example.com', password='testpass123'):
    """Create and return new user."""
    return get_user_model().objects.create_user(email, password)

class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email successful."""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        # Asserts
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.com', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            # Take the input email (left) and create user with it  # noqa
            user = get_user_model().objects.create_user(email, 'sample123')
            # Take the email that resulted from the user creation and compare it to expected  # noqa
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_employee(self):
        """Test creating a recipe is successful."""
        user = create_user()
        company = models.Company.objects.create(
            name='Juanse Café',
            description='Juanse Company in Bogota',
            address='101 St.',
            city='Bogotá D.C.',
            user=user
        )
        employee = models.Employee.objects.create(
            user=user,
            department='HR',
            job_title='MID',
            is_active=True,
            company=company
        )

        # Means that the print value of the employee object is its title.
        employee_string = f"{user.name} - {company.name}"
        self.assertEqual(str(employee), employee_string)

    def test_create_company(self):
        """Test creating a recipe is successful."""
        user = create_user()

        company = models.Company.objects.create(
            name='Juan',
            description='Company in Bogota',
            address='101 St.',
            city='Bogotá D.C.',
            user=user
        )

        # Means that the print value of the employee object is its title.
        self.assertEqual(str(company), company.name)