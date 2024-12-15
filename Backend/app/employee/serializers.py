"""
Serializers for Employee APIs
"""
from rest_framework import serializers

from core.models import Employee


class EmployeeSerializer(serializers.ModelSerializer):
    """Serializer for Employee."""

    class Meta:
        model = Employee
        fields = ['user', 'department', 'job_title', 'is_active']
        read_only_fields = ['user']

