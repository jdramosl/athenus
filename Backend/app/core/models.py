"""
Database Models.
"""
from django.conf import settings
from django.db import models  # noqa
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils.timezone import now


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

    def get_full_name(self):
        """
        Returns the full name of the user.
        """
        return f"{self.name}".strip()


class Company(models.Model):
    """Company model."""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)

    # FK to the User model (settings.AUTH_USER_MODEL)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='companies_owned'
    )

    def __str__(self):
        """Printable representation."""
        return self.name


class Employee(models.Model):
    """
    Employee model representing users working in the organization.
    """
    DEPARTMENT_CHOICES = [
        ('HR', 'Human Resources'),
        ('IT', 'Information Technology'),
        ('FIN', 'Finance'),
        ('SALES', 'Sales'),
        ('MARKETING', 'Marketing'),
        ('OPS', 'Operations'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='employees'
    )

    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES)
    job_title = models.CharField(max_length=20, help_text="Employee's job title")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.company.name}"


class ModelLLM(models.Model):
    """
    LLM models model class.
    """
    name = models.CharField(max_length=255)
    issuer = models.CharField(max_length=255)
    base_url = models.CharField(max_length=255)

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='llm_models'
    )


class Message(models.Model):
    """
    LLM models model class.
    """
    role = models.CharField(max_length=255)
    message = models.TextField(blank=False)

    model = models.ForeignKey(
        ModelLLM,
        on_delete=models.CASCADE,
        related_name='model_message'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_messages'
    )

    created_at = models.DateTimeField(auto_now_add=True)  # Set once when created.  # noqa
    updated_at = models.DateTimeField(auto_now=True)  # Update on every save.  # noqa

    def __str__(self):
        return f"Message: {self.user.get_full_name()} - {self.message}"
