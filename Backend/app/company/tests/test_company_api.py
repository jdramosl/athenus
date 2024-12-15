"""
Testing for the company API.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Company

from company.serializers import (
    CompanySerializer,
    CompanyDetailSerializer,
)

# URLS
"""
| **Name**            | **URL**             | **HTTP Method**  | **Action**         | **Description**                              |
|---------------------|---------------------|------------------|--------------------|----------------------------------------------|
| company-list        | `/companies/`       | GET              | list               | Fetch a list of all companies.                 |
| company-list        | `/companies/`       | POST             | create             | Create a new companies.                         |
| company-detail      | `/companies/<id>/`  | GET              | retrieve           | Fetch details of a specific companies.          |
| company-detail      | `/companies/<id>/`  | PUT              | update             | Update a specific companies (complete update).  |
| company-detail      | `/companies/<id>/`  | PATCH            | partial_update     | Partially update a specific companies.          |
| company-detail      | `/companies/<id>/`  | DELETE           | destroy            | Delete a specific companies.                    |

"""

COMPANIES_URL = reverse('company:company-list')

def detail_url(company_id):
    """
    Detailed company URL.
    """
    return reverse('company:company-detail', args=[company_id])

def create_company(employee, **params):
    """Create and return a sample company."""
    defaults = {
        'name': 'Some Company',
        'description': 'It was founded in 1887',
        'address': '100 st. 1400',
        'city': 'Bogotá D.C.',
    }
    defaults.update(params)

    company = Company.objects.create(employee=employee, **defaults)
    return company

def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicCompanyeAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(COMPANIES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCompanyApiTest(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='user@example.com',
            password='testpass123',
        )
        # Makes this user is auhtneticated for test purposes
        self.client.force_authenticate(self.user)

    def test_retrieve_companies(self):
        """Test retrieveing a list of companies. We retrieve ids in descending order."""
        # 1. First we create two companies for athenus
        create_company(employee=self.user)
        create_company(employee=self.user)

        # 2. We make the request
        res = self.client.get(COMPANIES_URL)
        # 3.  Retrieve all comanies
        companies = Company.objects.all().order_by('-id')
        # many=True means we're passing al list of items. We pass the companies to the serializer.  noqa
        serializer = CompanySerializer(companies, many=True)

        # 4. We test status code successful
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # and test that response 'res' get request matches objects.all() in Company serializer data  noqa

        # 4. Note we need to use the serializer, to compare against the request.
        self.assertEqual(res.data, serializer.data)

    def test_company_list_limited_to_user(self):
        """Test list of companies is limited to authenticated user."""
        other_user = create_user(
            email='other@example.com',
            password='password123',
        )
        # One company bu the actual user (authenticated)
        create_company(employee=other_user)
        # One by the other user.
        create_company(employee=self.user)

        res = self.client.get(COMPANIES_URL)

        # Only authenticated user companies
        companies = Company.objects.filter(employee=self.user)
        serializer = CompanySerializer(companies, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Only Company from authenticated users should be in res data
        self.assertEqual(res.data, serializer.data)

    def test_get_company_detail(self):
        """Test get Company detail."""
        company = create_company(employee=self.user)

        url = detail_url(company.id)
        res = self.client.get(url)

        serializer = CompanyDetailSerializer(company)

        self.assertEqual(res.data, serializer.data)

    def test_create_company(self):
        """Test creating a company."""
        payload = {
            'name': 'Some Company',
            'description': 'It was founded in 1887',
            'address': '100 st. 1400',
            'city': 'Bogotá D.C.',
        }
        # COMPANIES URL uses "list" endpoint, so the normal endopint "/companies"
        res = self.client.post(COMPANIES_URL, payload)
        # Check code is correct
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Retrieve Company object with ID from creation
        company = Company.objects.get(id=res.data['id'])
        # getattr uses the actual value found in k
        for k, v in payload.items():
            # Assert that retrieving the Company object with the id, matches the payload values.
            self.assertEqual(getattr(company, k), v)
        # Check user from API
        self.assertEqual(company.employee, self.user)