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
        # Save the user message first
        message = serializer.save(user=self.request.user)

        #if message.role == 'user':
        model_instance = message.model
        # Initialize response_data in case of failure
        response_payload = {"role": "model", "content": "No response from model"}
        base_url = model_instance.base_url

        print(f'base_url - {base_url}')

        # Fetch conversation history for the same user and model
        conversation_history = Message.objects.filter(
            user=message.user, model=model_instance
        ).order_by("created_at")


        if model_instance.name == 'Gemini':
            conversation_payload = [
                {"text": msg.message} for msg in conversation_history
            ]
            # Construct the request payload
            payload = {
                "contents": [{"parts": conversation_payload}]
            }

        elif model_instance.name == 'Llama3.2 3b':
            # Convert conversation history to LLM API format
            conversation_payload = [
                {"role": msg.role, "content": msg.message}
                for msg in conversation_history
                if msg.message.strip()  # Ensure message is not empty
            ]

            # Add system prompt (optional but recommended)
            system_message = {"role": "system", "content": "You are a helpful assistant called Athenus."}

            # Construct request payload (ensuring all messages have 'content')
            payload = {
                "model": "llama",
                "messages": [system_message] + conversation_payload,
            }

        else:
            # Convert conversation history to LLM API format
            print(f'MODEL NAME: {model_instance.name}')
            conversation_payload = 'I am athenus assistant'


            # conversation_payload = "\n".join(
            #     msg.message.strip() for msg in conversation_history if msg.message.strip()
            # )

            # Construct request payload (ensuring all messages have 'content')
            payload = {
                "role": message.role,
                "text": f"Context: {conversation_payload}. Message: {message.user}",
                "userId": f"{message.user.id}"
            }

        try:
            response = requests.post(
                base_url,
                headers=HEADERS,
                #params=PARAMS,
                json=payload,
                timeout=100
            )

            # Parse JSON response
            data = response.json()
            print("Response: ", json.dumps(data, indent=2))  # Pretty print response
            print()

            if response.status_code == 200:
                print('Success - 200 - LLM endpoint')

                try:
                    response_json = response.json()

                    if model_instance.name == 'Llama3.2 3b':
                        # Extract model's response message
                        response_data = (
                            response_json.get("choices", [{}])[0]
                            .get("message", {})
                            .get("content", "No response")
                        )
                    else:
                        response_data = (
                            response_json.get("answer")
                        )

                    # Store LLM response in the database
                    # Store model's response as a new Message object
                    model_message = Message.objects.create(
                        role="model",
                        message=response_data,
                        model=model_instance,
                        user=message.user
                    )
                    print('Model role message created in DB.')

                    # Prepare structured response
                    response_payload = {
                        "id": model_message.id,
                        "role": "model",
                        "content": response_data,
                        "created_at": model_message.created_at.isoformat()
                    }

                    print('Model role message created in DB.')

                except (IndexError, KeyError, TypeError) as e:
                    print(f"Error parsing LLM response: {e}, Response: {response_json}")

            else:
                print(f"API error: {response.status_code}, {response.text}")

        except Exception as e:
            print(f"Request failed: {e}")

        return message, response_payload

    def create(self, request, *args, **kwargs):
        """
        Override create() to return the user message and model response in the payload.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Call perform_create() to handle message creation and LLM response
        user_message, model_response = self.perform_create(serializer)

        # Build response payload
        response_payload = {
            "user_message": {
                "id": user_message.id,
                "role": user_message.role,
                "content": user_message.message,
                "created_at": user_message.created_at.isoformat()
            },
            "model_response": model_response
        }

        return Response(response_payload, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        """Filter queryset to authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-created_at')