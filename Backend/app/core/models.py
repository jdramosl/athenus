"""
Database Models.
"""
from django.conf import settings
from django.db import models # noqa
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):
    """Manager for Users."""
    # Password is default to none, works for testing for instance. # noqa
    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    User in the system.
    By default, Django provides the Manager class, which handles database query operations like .create(), .get(), .filter(), etc.  noqa
    UserManager is a specialized manager that includes methods tailored to managing user objects, such as creating users and superusers.  noqa
    """
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Assign user manager to our Custom User model
    objects = UserManager()

    USERNAME_FIELD = 'email'


class Company(models.Model):
    """Company object."""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL, # the base user model is the FK
        on_delete=models.CASCADE
    )

    def __str__(self):
        """Printable object"""
        return self.name


class Employee(models.Model):
    """
    Employee model representing additional details for users working in the organization.
    This model creates a one-to-one relationship with the custom User model.
    So in Athenus we can creeate users without link them to employees.
    But we can't create an employee without an user.
    """
    DEPARTMENT_CHOICES = [
        ('HR', 'Human Resources'),
        ('IT', 'Information Technology'),
        ('FIN', 'Finance'),
        ('SALES', 'Sales'),
        ('MARKETING', 'Marketing'),
        ('OPS', 'Operations'),
    ]

    JOB_TITLE_CHOICES = [
        ('ENTRY', 'Entry Level'),
        ('MID', 'Mid Level'),
        ('SENIOR', 'Senior Level'),
        ('MANAGER', 'Management'),
        ('DIRECTOR', 'Director'),
        ('EXEC', 'Executive'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True
    )

   # Employee Specific
    department = models.CharField(
        max_length=20,
        choices=DEPARTMENT_CHOICES,
        help_text="Department the employee belongs to"
    )
    job_title = models.CharField(
        max_length=20,
        choices=JOB_TITLE_CHOICES,
        help_text="Employee's job title"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the employee is currently employed"
    )

    # Optional manager contact details
    manager = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='direct_reports'
    )

    def __str__(self):
        return f"{self.user.name} - {self.job_title} ({self.department})"

    def get_full_name(self):
        """
        Returns the full name of the employee.
        """
        return self.user.name

    def is_management(self):
        """
        Check if the employee is in a management position.
        """
        return self.job_title in ['MANAGER', 'DIRECTOR', 'EXEC']