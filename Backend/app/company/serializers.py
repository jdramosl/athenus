"""
Serializers for Company APIs
"""
from rest_framework import serializers

from core.models import (
    Company,
    Employee
)


class CompanySerializer(serializers.ModelSerializer):
    """Serializer for recipes."""

    class Meta:
        model = Company
        fields = ['id', 'name', 'address', 'city']
        read_only_fields = ['id']

class CompanyDetailSerializer(CompanySerializer):
    """Serializer for recipe detail view."""

    class Meta(CompanySerializer.Meta):
        fields = CompanySerializer.Meta.fields + ['description']


class EmployeeSerializer(serializers.ModelSerializer):
    """Serializer for employee."""

    class Meta:
        model = Employee
        fields = ['user', 'department', 'job_title', 'is_active', 'company']
        read_only_fields = ['user']

    def _get_or_create_company(self, company):
        """Handle getting or creating a company as needed."""
        # The view passes the context containing the user.
        auth_user = self.context['request'].user

        # Get - or - get and create
        company_obj, created = Company.objects.get_or_create(
            user=auth_user,
            **company
        )

        return company_obj

    def create(self, validated_data):
        """Customizing creating Employee."""
        company_data = validated_data.pop('company', None)

        # Validate if company exists. If not, it creates it and then it creates employee.
        if company_data:
            company = self._get_or_create_company(company_data)
            validated_data['company'] = company

        return Employee.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Update employee."""
        company = validated_data.pop('company', None)

        if company is not None:
            instance.company = company

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


