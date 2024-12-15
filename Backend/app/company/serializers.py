"""
Serializers for Company APIs
"""
from rest_framework import serializers

from core.models import Company


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