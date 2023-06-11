import uuid

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.db import models


class UserManager(BaseUserManager):
    def create_user(
        self,
        email="",
        password=None,
    ):
        """
        Creates and saves a User with the given email and password.
        """

        user = self.model(email=email)

        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_admin = True
        user.save()
        return user


class UserRole(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(
        auto_now=False,
        null=True,
    )

    class Meta:
        db_table = "User_Roles"


class Country(models.Model):
    name = models.CharField(
        max_length=255,
        blank=True,
        null=False,
    )

    abbreviation = models.CharField(
        max_length=255,
        blank=True,
        null=False,
    )

    calling_code = models.CharField(
        max_length=255,
        blank=True,
        null=False,
    )

    flag = models.CharField(
        max_length=255,
        blank=True,
        null=False,
    )

    class Meta:
        db_table = "Countries"


class User(AbstractBaseUser):
    user_key = models.UUIDField(
        unique=True,
        primary_key=True,
        default=uuid.uuid4,
    )

    role = models.ForeignKey(
        UserRole,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    email = models.EmailField(unique=True)

    mobile_number = models.CharField(max_length=255, blank=True, null=True)

    first_name = models.CharField(max_length=255, blank=True)

    last_name = models.CharField(max_length=255, blank=True)

    organization = models.CharField(max_length=255, null=True, blank=True)

    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    bio = models.TextField(null=True, blank=True)

    links = models.JSONField(null=True, blank=True)

    is_admin = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    is_verified = models.BooleanField(default=False)

    created_on = models.DateTimeField(auto_now_add=True)

    updated_on = models.DateTimeField(auto_now_add=False, null=True, blank=True)

    password_reset_code = models.CharField(max_length=255, blank=True, null=True)

    profile_image = models.CharField(max_length=255, blank=True, null=True)

    account_type = models.CharField(max_length=255, null=False)

    is_deleted = models.BooleanField(default=False)

    # unique field
    USERNAME_FIELD = "email"
    objects = UserManager()

    class Meta:
        db_table = "Users"
