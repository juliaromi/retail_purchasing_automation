import re
from decimal import Decimal

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

        if (extra_fields.get('is_staff') and extra_fields.get('is_superuser')) is not True:
            raise ValidationError('User must be superuser')

        return admin_user


class User(AbstractUser):
    """
    User model
    """

    first_name = models.CharField(max_length=50, blank=False)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    last_name= models.CharField(max_length=50, blank=False)
    login = models.EmailField(unique=True, blank=False, null=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    username = None

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Shop(models.Model):
    """
    Shop model
    """

    name = models.CharField(max_length=50, blank=False, null=False, unique=True)
    site = models.URLField(blank=True, null=True)

    objects = models.Manager()

    class Meta:
        verbose_name = 'Shop'
        verbose_name_plural = 'Shops'

    def __str__(self):
        return self.name


class Category(models.Model):
    """
    Product category model
    """

    shops = models.ManyToManyField(Shop, related_name='product_categories')
    name = models.CharField(max_length=50, blank=False, null=False, unique=True)

    objects = models.Manager()

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
    name = models.CharField(unique=True, max_length=50, blank=False, null=False)

    objects = models.Manager()

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

    product_name = models.CharField(blank=False, null=False)
    model = models.ForeignKey(Model, on_delete=models.CASCADE, related_name='products_info')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='products_info')
    quantity = models.PositiveIntegerField(blank=False, null=False)
    price = models.DecimalField(max_digits=12, decimal_places=2, blank=False, null=False)
    rrp = models.DecimalField(max_digits=12, decimal_places=2, blank=False, null=False)

    objects = models.Manager()

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

    name = models.CharField(max_length=50, blank=False, null=False, unique=True)

    objects = models.Manager()

    class Meta:
        verbose_name = 'Parameter name'
        verbose_name_plural = 'Parameter names'

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    """
    Product parameter model
    """

    product_info = models.ForeignKey(ProductInfo, on_delete=models.CASCADE, blank=False, null=False)
    parameter = models.ForeignKey(Parameter, on_delete=models.CASCADE, blank=False, null=False)
    value = models.CharField(max_length=50, blank=False, null=False)

    objects = models.Manager()

    class Meta:
        verbose_name = 'Product parameter'
        verbose_name_plural = 'Product parameters'

    def __str__(self):
        return f'{self.product_info.product_name} has {self.parameter.name} with {self.value} value'


class Order(models.Model):
    """
    Order model
    """

    class OrderStatus(models.IntegerChoices):
        CREATED = 1
        PAID = 2
        PROCESSING = 3
        DISPATCHED = 4
        IN_TRANSIT = 5
        DELIVERED = 6
        CANCELLED = 7

    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    status =models.IntegerField(choices=OrderStatus, default=1, blank=False)

    objects = models.Manager()

    @property
    def order_total(self):
        total = Decimal('0.00')
        for product in self.orderitem_set.all():
            total += product.quantity * product.product.price
        return total


    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return (f'Order created at {self.created_at} '
                f'by {self.user} '
                f'has status: {self.status}')


class OrderItem(models.Model):
    """
    Order item model
    """

    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=False, null=False)
    product = models.ForeignKey(ProductInfo, on_delete=models.CASCADE, blank=False, null=False)
    shop =models.ForeignKey(Shop, on_delete=models.CASCADE, blank=False, null=False)
    quantity = models.PositiveSmallIntegerField(blank=False, null=False)

    objects = models.Manager()

    def clean(self):
        super().clean()
        if self.quantity < 0:
            raise ValidationError('Item quantity must be positive')

    class Meta:
        verbose_name = 'Order item'
        verbose_name_plural = 'Order items'

    def __str__(self):
        return (f'{self.product.product_name}: '
                f'order created at {self.order.created_at}, '
                f'from {self.shop.name} shop, '
                f'quantity {self.quantity} pcs')

class Contact(models.Model):
    """
    User contact model
    """

    TYPES = [
        ('PHONE', 'phone number'),
        ('EMAIL', 'email'),
    ]

    type = models.CharField(max_length=5, choices=TYPES, blank=False, null=False, default='EMAIL')
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    value = models.CharField(blank=False, null=False)

    objects = models.Manager()

    def clean(self):
        super().clean()
        if self.type == 'PHONE':
            if not re.match(r'^[+8]\d{10,11}$', self.value):
                raise ValidationError('Phone number is invalid')
        else:
            if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9.-]+$', self.value):
                raise ValidationError('Email is invalid')


    class Meta:
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'

    def __str__(self):
        return f'{self.user}: {self.type} - {self.value}'


class DeliveryAddress(models.Model):
    """
    User delivery address model
    """

    city = models.CharField(max_length=50, blank=False, null=False)
    street = models.CharField(max_length=100, blank=False, null=False)
    building = models.CharField(max_length=10, blank=False, null=False)
    block = models.CharField(max_length=10, blank=True, null=True)
    structure = models.CharField(max_length=10, blank=True, null=True)
    apartment = models.PositiveSmallIntegerField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)

    objects = models.Manager()

    def clean(self):
        super().clean()
        if not self.city:
            raise ValidationError('City must be provided')
        if not self.street:
            raise ValidationError('Street must be provided')

        if not self.building:
            raise ValidationError('Building number must be provided')
        else:
            if not re.match(r'^[a-zA-Z0-9]+$', self.building):
                raise ValidationError('Building number is invalid')

        if self.block:
            if not re.match(r'^[a-zA-Z0-9]+$', self.block):
                raise ValidationError('Block number is invalid')

        if self.structure:
            if not re.match(r'^[a-zA-Z0-9]+$', self.structure):
                raise ValidationError('Structure number is invalid')


    class Meta:
        verbose_name = 'User delivery address'
        verbose_name_plural = 'Users delivery addresses'

    def __str__(self):
        address = [self.city, self.street, self.building]

        if self.block:
            address.append(self.block)
        if self.structure:
            address.append(self.structure)
        if self.apartment:
            address.append(str(self.apartment))

        return ', '.join(address)
