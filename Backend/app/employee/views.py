"""
Views for the Employee API's.
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Employee
from employee import serializers


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    View for manage Employee API's.
    ModelViewSet will help on the different endpoints.
    It helps with the logic of this.
    """
    serializer_class = serializers.EmployeeSerializer  # We changed to be detail the default one.  noqa
    queryset = Employee.objects.all()
    # Specifies authentication
    authentication_classes = [TokenAuthentication]
    # This means you need to be authenticated.
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retrieve Employee for authenticated users. Desc order by Employee id
        self.request.user means the user that authenticated at the request
        """
        return self.queryset.filter(user=self.request.user).order_by('-user')

    def perform_create(self, serializer):
        """
        Create a new Employee.
        When we create a new Employee we call this method.

        Here it is assumed that the serializer is validated.
        """
        serializer.save(user=self.request.user)