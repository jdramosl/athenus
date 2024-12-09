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
| company-list        | `/companies/`       | GET              | list               | Fetch a list of all recipes.                 |
| company-list        | `/companies/`       | POST             | create             | Create a new recipe.                         |
| company-detail      | `/companies/<id>/`  | GET              | retrieve           | Fetch details of a specific recipe.          |
| company-detail      | `/companies/<id>/`  | PUT              | update             | Update a specific recipe (complete update).  |
| company-detail      | `/companies/<id>/`  | PATCH            | partial_update     | Partially update a specific recipe.          |
| company-detail      | `/companies/<id>/`  | DELETE           | destroy            | Delete a specific recipe.                    |

"""

COMPANIES_URL = reverse('company:company-list')

def detail_url(company_id):
    """
    Detailed company URL.
    """
    return reverse('company:company-detail', args=[company_id])

def create_recipe(user, **params):
    """Create and return a sample recipe."""
    defaults = {
        'title': 'Sample recipe title',
        'time_minutes': 22,
        'price': Decimal('5.25'),
        'description': 'Sample description.',
        'link': 'http://example.com/recipe.pdf',
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe
