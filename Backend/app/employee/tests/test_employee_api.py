"""
Testing for the employee API.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Employee

from employee.serializers import (
    EmployeeSerializer
)

# URLS
"""
Table for Employee
"""

EMPLOYEES_URL = reverse('employee:employee-list')


def create_employee(user, **defaults):
    """Helper function to create an employee."""
    if Employee.objects.filter(user=user).exists():
        return Employee.objects.get(user=user)  # Return existing Employee
    return Employee.objects.create(user=user, **defaults)


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicEmployeeAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(EMPLOYEES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateEmployeeApiTest(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='user@example.com',
            password='testpass123',
        )
        # Makes this user is auhtneticated for test purposes
        self.client.force_authenticate(self.user)

    def test_retrieve_employees(self):
        """Test retrieveing a list of employee. We retrieve ids in descending order."""
        # 1. First we create two employees for athenus
        create_employee(user=self.user)
        create_employee(user=self.user)

        # 2. We make the request
        res = self.client.get(EMPLOYEES_URL)
        # 3.  Retrieve all comanies
        employees = Employee.objects.all().order_by('-user')
        # many=True means we're passing al list of items. We pass the employees to the serializer.  noqa
        serializer = EmployeeSerializer(employees, many=True)

        # 4. We test status code successful
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # and test that response 'res' get request matches objects.all() in employee serializer data  noqa

        # 4. Note we need to use the serializer, to compare against the request.
        self.assertEqual(res.data, serializer.data)

    def test_employee_is_limited_to_user(self):
        """Test list of employees is limited to authenticated user."""
        other_user = create_user(
            email='other@example.com',
            password='password123',
        )
        # One employee bu the actual user (authenticated)
        create_employee(user=other_user)
        # One by the other user.
        create_employee(user=self.user)

        res = self.client.get(EMPLOYEES_URL)

        # Only authenticated user employee
        employees = Employee.objects.filter(user=self.user)
        serializer = EmployeeSerializer(employees, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Only employee from authenticated users should be in res data
        self.assertEqual(res.data, serializer.data)



    def test_create_Employee(self):
        """Test creating a Employee."""
        payload = {
            'department': 'IT',
            'job_title': 'MID',
            'is_active': True,
        }
        # COMPANIES URL uses "list" endpoint, so the normal endopint "/companies"
        res = self.client.post(EMPLOYEES_URL, payload)
        # Debugging response   noqa
        print(res.json())

        # Check code is correct
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Retrieve Employee object with ID from creation
        employee = Employee.objects.get(user=res.data['user'])
        # getattr uses the actual value found in k
        for k, v in payload.items():
            # Assert that retrieving the Employee object with the id, matches the payload values.
            self.assertEqual(getattr(employee, k), v)
        # Check user from API
        self.assertEqual(employee.user, self.user)