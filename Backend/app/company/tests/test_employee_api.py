"""
Tests for the Employee API.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Employee, Company

from company.serializers import EmployeeSerializer

EMPLOYEE_URL = reverse('company:employee-list')


def detail_url(employee_id): # user id -> employee id
    """Create and return a employee detail url."""
    return reverse('company:employee-detail', args=[employee_id])

def create_user(email='user@example.com', password='testpass123'):
    """Create and return a user."""
    return get_user_model().objects.create_user(email=email, password=password)

def create_user_2(email='user2@example.com', password='testpass123'):
    """Create and return a user."""
    return get_user_model().objects.create_user(email=email, password=password)




class PublicEmployeeApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient() # from drf

    def test_auth_required(self):
        """Test auth is required for retrieving employees."""
        res = self.client.get(EMPLOYEE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """
    Test authenticated API requests.
    """

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def _create_company(self, **params):
        """Create and return a sample company."""
        defaults = {
            'name': 'Some Company',
            'description': 'It was founded in 1887',
            'address': '100 st. 1400',
            'city': 'Bogotá D.C.',
        }
        defaults.update(params)

        company = Company.objects.create(user=self.user, **defaults)
        return company

    def test_retrieve_employees(self):
        """Test retriving a list of employees."""
        user2 = create_user_2()
        # Employee instance 1
        Employee.objects.create(
            user=self.user,
            company=self._create_company(),
            department='IT',
            job_title='Software Engineer',
            is_active=True
        )

        # Employee instance 2
        Employee.objects.create(
            user=user2,
            company=self._create_company(),
            department='HR',
            job_title='HR Manager',
            is_active=True
        )
        res = self.client.get(EMPLOYEE_URL)

        employees = Employee.objects.all().order_by('-user')

        serializer = EmployeeSerializer(employees, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        # Serializer only retrieves employee assigned to authenticated user
        self.assertEqual(len(serializer.data), 2)

    def test_tags_limited_to_user(self):
        """Test employee is limited to authenticated user."""
        user2 = create_user_2()

        authenticated_employee = Employee.objects.create(
            user=self.user,
            company=self._create_company(),
            department='IT',
            job_title='Software Engineer',
            is_active=True
        )

        # Employee instance 2
        Employee.objects.create(
            user=user2,
            company=self._create_company(),
            department='HR',
            job_title='HR Manager',
            is_active=True
        )

        # Testign that /employees/ endpoint lists only tags for authenticated users.  noqa
        res = self.client.get(EMPLOYEE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Only 1 employee, the one we created with authenticated user.
        self.assertEqual(len(res.data), 1)

        self.assertEqual(res.data[0]['department'], authenticated_employee.department)
        self.assertEqual(res.data[0]['user'], authenticated_employee.user.id)



    def test_update_employee(self):
        """Test updating an employee."""
        # Original object name
        employee = Employee.objects.create(
            user=self.user,
            company=self._create_company(),
            department='IT',
            job_title='Software Engineer',
            is_active=True
        )

        # Updating with patch
        payload = {'department': 'FIN'}
        url = detail_url(employee.user.pk)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        employee.refresh_from_db()
        self.assertEqual(employee.department, payload['department'])

    def test_delete_employee(self):
        """Test deleting an employee."""
        employee = Employee.objects.create(
            user=self.user,
            company=self._create_company(),
            department='IT',
            job_title='Software Engineer',
            is_active=True
        )
        url = detail_url(employee.user.pk)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        employee = Employee.objects.filter(user=self.user)
        # Since the user only created 1 tag and then we delete it, there shouldn't be any.
        self.assertFalse(employee.exists())

