"""
Views for the Company API's.
"""
import os
import requests
from rest_framework import (
    viewsets,
    mixins # Additional funct. to a view  noqa
)

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes
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
from rest_framework.utils import json

CHATBOT_URL = 'https://eb55-186-31-183-18.ngrok-free.app/query'
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
HEADERS = {
    "Content-Type": "application/json"
}
PARAMS = {
    "key": f"{GEMINI_API_KEY}"  # API Key as a query parameter
}



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


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'company',
                OpenApiTypes.STR,
                description='ID of Company'
            ),
        ]
    )
)
class ModelLLMViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """Manage LLM models in database."""
    serializer_class = serializers.ModelLLMSerializer
    queryset = ModelLLM.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _params_to_ints(self, qs):
        """Convert a list of strings to integers."""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        queryset = self.queryset

        company = self.request.query_params.get('company')

        if company:
            company_id = self._params_to_ints(company)
            queryset = queryset.filter(company__id__in=company_id)
            return queryset.order_by('-name')

        return queryset.order_by('-name')  # Return empty queryset if no company is selected.  # noqa


class MessageViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
)         :
    """Manage LLM models in database."""
    serializer_class = serializers.MessageSerializer
    queryset = Message.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

    def perform_create(self, serializer):
        """
        Create a new Company.
        When we create a new Company we call this method.

        Here it is assumed that the serializer is validated.
        """
        # Save the initial message and assign the logged-in user
        message = serializer.save(user=self.request.user)

        # If the message is from the user, call the model's API
        if message.role == "user":
            model_instance = message.model  # Get associated ModelLLM instance
            base_url = model_instance.base_url  # Retrieve base_url from ModelLLM

            try:
                # Define the request payload
                PAYLOAD = {
                    "contents": [{
                        "parts": [{"text": f"{message.message}"}]
                    }]
                }
                # DEBUG
                print(f'{base_url} - {message.message}')
                response = requests.post(
                    base_url,
                    headers=HEADERS,
                    params=PARAMS,
                    json=PAYLOAD,
                    timeout=100,
                )

                # Check for errors
                response.raise_for_status()

                # Parse JSON response
                data = response.json()
                print("Response:", json.dumps(data, indent=2))  # Pretty print response
                print()

                if response.status_code == 200:
                    print('Success - 200 - LLM endpoint')

                    try:
                        response_json = response.json()
                        # Extract message text from the response structure
                        response_data = (
                            response_json.get("candidates", [{}])[0]
                            .get("content", {})
                            .get("parts", [{}])[0]
                            .get("text", "No response")
                        )

                        # Create a new message with role 'model'
                        Message.objects.create(
                            role="model",
                            message=response_data,
                            model=model_instance,
                            user=message.user  # Link to the same user
                        )
                        print('Model role message created in DB.')

                    except (IndexError, KeyError, TypeError) as e:
                        print(f"Error parsing LLM response: {e}, Response: {response_json}")
                else:
                    print(f"API error: {response.status_code}, {response.text}")

            except requests.RequestException as e:
                print(f"Request failed: {e}")  # Log the error

    def get_queryset(self):
        """Filter queryset to authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-created_at')