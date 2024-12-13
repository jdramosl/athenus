"""
URL mappings for the Employee app.
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from employee import views


router = DefaultRouter()
# This will create endpoint "/recipes", it will support CRUD methods
router.register('employees', views.EmployeeViewSet)

# Name for reverse look up
app_name = 'employee'

# Include the router urls
urlpatterns = [
    path('', include(router.urls))
]