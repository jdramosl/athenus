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
