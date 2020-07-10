import os

from shutil import copy2
from django.conf import settings
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from .tasks import resize_img

import requests


def make_img_copy(img_name, prefix=''):
    img_path = os.path.join(settings.IMAGES_DIR, img_name)
    img_copy_path = os.path.join(settings.IMAGES_DIR, 'copy_' + prefix + img_name)
    copy2(img_path, img_copy_path)
    return img_copy_path


class CeleryTest(TestCase):
    def test_resize_success(self):
        img_copy_path = make_img_copy(settings.TEST_IMG)
        result = resize_img.delay(img_copy_path, 100, 100).get()
        self.assertEqual(result['status'], 'SUCCESS')

    def test_resize_fail(self):
        img_copy_path = make_img_copy(settings.TEST_IMG)
        result = resize_img.delay(img_copy_path, 0, 0).get()
        self.assertEqual(result['status'], 'FAILURE')


class APITest(TestCase):
    def setUp(self):
        self.client = Client()

    def upload_image(self, img_name, height, width, prefix=''):
        img_copy_path = make_img_copy(img_name, prefix)

        url = settings.SITE_URL + reverse('set')

        payload = {'width': width,
                   'height': height}
        files = {'image_file': open(img_copy_path, 'rb')}

        response = requests.request("POST", url, data=payload, files=files)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        return response.json()['task_id'], response.json()['task_status']

    def resize_example(self, w, h):
        task_id, task_status = self.upload_image(settings.TEST_IMG, w, h)
        while task_status == 'PENDING':
            url = settings.SITE_URL + reverse('task', args=(task_id,))
            response = requests.request("GET", url)
            task_status = response.json()['task_status']
        self.assertEqual(task_status, 'SUCCESS')

    def test_make_small(self):
        self.resize_example(10, 10)

    def test_make_big(self):
        self.resize_example(2000, 2000)

    def test_concurrent_resize(self, n_tasks=3):
        task_ids = [0 for i in range(n_tasks)]
        task_status = ['' for i in range(n_tasks)]

        for i in range(n_tasks):
            task_ids[i], task_status[i] = self.upload_image(settings.TEST_IMG, 2000, 2000, prefix=str(i))

        while 'PENDING' in task_status:
            for i in range(n_tasks):
                url = settings.SITE_URL + reverse('task', args=(task_ids[i],))
                response = requests.request("GET", url)
                task_status[i] = response.json()['task_status']

        self.assertTrue(all([x == 'SUCCESS' for x in task_status]))