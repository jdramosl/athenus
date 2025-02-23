"""
Views for the Company API's.
"""
import requests
from rest_framework import (
    viewsets,
    mixins # Additional funct. to a view  noqa
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import (
    Company,
    Employee,
    ModelLLM,
    Message
)
from company import serializers


CHATBOT_URL = 'https://eb55-186-31-183-18.ngrok-free.app/query'

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
        return self.queryset.filter(user=self.request.user).order_by('-id')

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
        serializer.save(user=self.request.user)


class EmployeeViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """
    Manage tags in the database.
    It is important that GenericViewSet is the last to inherit from.
    UpdateModelMixin allowed to update using patch.
    """
    serializer_class = serializers.EmployeeSerializer
    queryset = Employee.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticated user."""
        return self.queryset.filter(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='chatbot')
    def chatbot(self, request, pk=None):
        """
        Custom endpoint for chatbot functionality.
        Accessible at: /api/companies/employee/<user>/chatbot
        """
        url = CHATBOT_URL

        # Process chatbot request
        user_message = request.data.get('message', '')
        if not user_message:
            return Response({"error": "No message provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Make the external POST request
        url = "https://6600-186-31-183-18.ngrok-free.app/query/"
        headers = {"Content-Type": "application/json"}
        payload = {"text": user_message}

        try:
            response = requests.post(url, headers=headers, json=payload)
            response_data = response.json()
        except requests.RequestException as e:
            return Response({"error": "Failed to communicate with chatbot service", "details": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Return the chatbot's response
        return Response({
            "employee": self.request.user.name,
            "chatbot_response": response_data
        }, status=status.HTTP_200_OK)

# class LLM