from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ProductInfo, User
from .tasks import make_thumbnails

@receiver(post_save, sender=ProductInfo)
@receiver(post_save, sender=User)
def generate_thumbnails(sender, instance, **kwargs):
    if instance.image:
        make_thumbnails.delay(instance.image.name)
