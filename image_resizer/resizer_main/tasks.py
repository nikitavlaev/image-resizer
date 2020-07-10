import os
from celery import shared_task
from PIL import Image

from django.conf import settings

@shared_task
def resize_img(img_path, w, h):
    os.chdir(settings.IMAGES_DIR)
    path, file = os.path.split(img_path)
    img_name, ext = os.path.splitext(file)

    new_img_path = os.path.join(f"{settings.MEDIA_URL}images", img_name + f"_{w}x{h}" + ext) 
    results = {'img_path': new_img_path, 'status': 'SUCCESS'}
    try:
        img = Image.open(img_path)
        os.remove(img_path)
        img = img.resize((int(w),int(h)))
        img.save(img_name + f"_{w}x{h}" + ext)
        img.close()
    except Exception as e:
        return {'status': 'FAILURE'}
    return results        

