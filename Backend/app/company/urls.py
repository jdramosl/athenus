"""
URL mappings for the Company app.
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from company import views


router = DefaultRouter()
# This will create endpoint "/recipes", it will support CRUD methods
router.register('companies', views.CompanyViewSet)

# Name for reverse look up
app_name = 'company'

# Include the router urls
urlpatterns = [
    path('', include(router.urls))
]