from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


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


class Shop(models.Model):
    """
    Shop model
    """

    name = models.CharField(max_length=50, blank=False, null=False)
    site = models.URLField(blank=True, null=True)

    shops = models.Manager()

    class Meta:
        verbose_name = 'Shop'
        verbose_name_plural = 'Shops'

    def __str__(self):
        return f'Shop {self.name}'


class Category(models.Model):
    """
    Product category model
    """

    shops = models.ManyToManyField(Shop, related_name='product_categories')
    name = models.CharField(max_length=50, blank=False, null=False)

    categories = models.Manager()

    class Meta:
        verbose_name = 'Product category'
        verbose_name_plural = 'Product categories'

    def __str__(self):
        return self.name


class Model(models.Model):
    """
    Product model model
    """

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='product_models')
    name = models.CharField(max_length=50, blank=False, null=False)

    products = models.Manager()

    class Meta:
        verbose_name = 'Product model'
        verbose_name_plural = 'Product model'

    def __str__(self):
        return self.name


class ProductInfo(models.Model):
    """
    Product information model:
        - product name
        - model
        - shop
        - quantity
        - price
        - recommended retail price (rrp)
    """

    product_name = models.CharField(max_length=50, blank=False, null=False)
    model = models.ForeignKey(Model, on_delete=models.CASCADE, related_name='products_info')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='products_info')
    quantity = models.PositiveIntegerField(blank=False, null=False)
    price = models.DecimalField(max_digits=12, decimal_places=2, blank=False, null=False)
    rrp = models.DecimalField(max_digits=12, decimal_places=2, blank=False, null=False)

    products_info = models.Manager()

    class Meta:
        verbose_name = 'Product info'
        verbose_name_plural = 'Products info'

    def __str__(self):
        return (f'Product {self.product_name}: '
                f'model {self.model}, '
                f'store in shop {self.shop}, '
                f'{self.quantity} in stock, '
                f'price - {self.price}$, '
                f'rrp - {self.rrp}')

    def clean(self):
        super().clean()
        if self.price < 0:
            raise ValidationError('Price must be positive')
        if self.rrp < 0:
            raise ValidationError('RRP must be positive')


class Parameter(models.Model):
    """
    Product parameters model
    """

    name = models.CharField(max_length=50, blank=False, null=False)

    parameters = models.Manager()

    class Meta:
        verbose_name = 'Product parameter'
        verbose_name_plural = 'Product parameters'

    def __str__(self):
        return self.name
