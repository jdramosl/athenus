"""
Views for the Company API's.
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Company
from company import serializers


class CompanyViewSet(viewsets.ModelViewSet):
    """
    View for manage Company API's.
    ModelViewSet will help on the different endpoints.
    It helps with the logic of this.
    """
    serializer_class = serializers.CompanyDetailSerializer  # We changed to be detail the default one.  noqa
    queryset = Company.objects.all()
    # Specifies authentication
    authentication_classes = [TokenAuthentication]
    # This means you need to be authenticated.
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retrieve Company for authenticated users. Desc order by Company id
        self.request.user means the user that authenticated at the request
        """
        return self.queryset.filter(employee=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """
        Return the serializer class for request.
        It will depend if the action is list.
        We are customizing the serializer for the following Default Router config:
        endpoint: Companies/	type: GET	self.action: list	Action: List all Company
        """
        if self.action == 'list':
            return serializers.CompanySerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """
        Create a new Company.
        When we create a new Company we call this method.

        Here it is assumed that the serializer is validated.
        """
        serializer.save(employee=self.request.user)
