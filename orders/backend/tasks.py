import os
from PIL import Image
from celery import shared_task
from django.conf import settings

# Celery functionality test
@shared_task
def adding_task(x, y):
    return x + y

@shared_task
def make_thumbnails(image_path, sizes=[(200, 200), (100, 100), (50, 50)]):
    """
    Creating thumbnails of various sizes for faster image loading
    """
    full_path = os.path.join(settings.MEDIA_ROOT, image_path)
    base_name, ext = os.path.splitext(os.path.basename(image_path))
    thumbnails_dir = os.path.join(settings.MEDIA_ROOT, 'thumbnails')
    os.makedirs(thumbnails_dir, exist_ok=True)

    try:
        with Image.open(full_path) as img:
            for width, height in sizes:
                img_copy = img.copy()
                img_copy.thumbnail((width, height))
                thumb_filename = f'{base_name}_{width}x{height}{ext}'
                thumb_path = os.path.join(thumbnails_dir, thumb_filename)
                img_copy.save(thumb_path)
    except Exception as e:
        print(f'Error while creating thumbnails: {e}')
        return {'error': str(e)}

    return {'status': 'ok', 'generated': len(sizes)}
