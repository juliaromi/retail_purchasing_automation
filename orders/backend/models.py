from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


# Create your models here.

class UserManager(BaseUserManager):

    def create_user(self, login, password, **extra_fields):
        if not login:
            raise ValidationError('Email address must be provided')
        if not password:
            raise ValidationError('Password must be provided')
        user = self.model(login=login, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_staff(self, login, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        staff_user = self.create_user(login, password, **extra_fields)

        if extra_fields.get('is_staff') is not True:
            raise ValidationError('User must be staff')

        staff_user.save(using=self._db)

        return staff_user

    def create_superuser(self, login, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        admin_user = self.create_user(login, password, **extra_fields)
        admin_user.save(using=self._db)

        if (extra_fields.get('is_staff') and extra_fields.get('is_staff')) is not True:
            raise ValidationError('User must be superuser')

        return admin_user


class User(AbstractUser):
    """
    User model
    """

    name = models.CharField(max_length=50, blank=False)
    lastname= models.CharField(max_length=50, blank=False)
    login = models.EmailField(unique=True, blank=False, null=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = ['name', 'lastname']

    objects = UserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f'User {self.login}: {self.name} {self.lastname}'
