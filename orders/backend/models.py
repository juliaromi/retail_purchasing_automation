from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


# Create your models here.

class UserManager(BaseUserManager):

    def create_user(self, name, lastname, login, password):
        if not name:
            raise ValidationError('Name must be provided')
        if not lastname:
            raise ValidationError('Lastname must be provided')
        if not login:
            raise ValidationError('Email address must be provided')
        if not password:
            raise ValidationError('Password must be provided')
        user = self.model(name=name, lastname=lastname, login=login)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_staff(self, name, lastname, login, password):
        staff_user = self.create_user(name, lastname, login, password)
        staff_user.is_staff = True
        staff_user.save(using=self._db)

        return staff_user


class User(AbstractUser):
    """
    User model
    """

    name = models.CharField(max_length=50, blank=False)
    lastname= models.CharField(max_length=50, blank=False)
    login = models.EmailField(unique=True, blank=False, null=False)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = ['name', 'lastname', 'contact']

    objects = UserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f'User {self.login}: {self.name} {self.lastname}'
