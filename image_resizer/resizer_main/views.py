import os

from django import forms
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .tasks import resize_img

from celery import current_app

import logging

logger = logging.getLogger('django')


class FileUploadForm(forms.Form):
    '''
    Handle form data
    '''
    image_file = forms.ImageField(required=True)
    width = forms.IntegerField(required=True, widget=forms.NumberInput
                                (attrs={'id': 'width'}))
    height = forms.IntegerField(required=True, widget=forms.NumberInput
                                (attrs={'id': 'height'}))


class SetTaskView(APIView):
    '''
    Handle post image request
    '''
    def post(self, request):
        form = FileUploadForm(request.POST, request.FILES)
        logger.debug("post image request")

        if form.is_valid():
            w = form['width'].value()
            h = form['height'].value()
            image_name = request.FILES['image_file'].name
            file_path = os.path.join(settings.IMAGES_DIR, image_name)
            logger.debug(f"image_name={image_name}, width={w}, height={h}")

            # process multipart data
            try:
                with open(file_path, 'wb+') as fp:
                    for chunk in request.FILES['image_file']:
                        fp.write(chunk)
            except IOError:
                logger.error("Error during img load")
                return Response('Error during image file processing', status.HTTP_500_INTERNAL_SERVER_ERROR)

            # start celery task
            task = resize_img.delay(file_path, w, h)

            response_data = {'task_status': task.status, 'task_id': task.id}
            logger.debug(f"Correct response: {response_data}")
            return JsonResponse(response_data)

        logger.error(f"Wrong form data: {form.errors}")
        return Response('Wrong form input', status.HTTP_400_BAD_REQUEST)


class GetTaskView(APIView):
    '''
    Retrieve task status(and result url, if ready)
    '''
    def get(self, request, task_id):
        logger.debug("get status/image request")

        task = current_app.AsyncResult(task_id)
        response_data = {'task_status': task.status, 'task_id': task.id}

        if task.status == 'SUCCESS':
            result = task.get()
            if result['status'] == 'FAILURE':
                logger.debug("error during image processing")
                return Response('Error during image processing', status.HTTP_500_INTERNAL_SERVER_ERROR)
            response_data['results'] = result

        logger.debug(f"Correct response with: {response_data}")
        return JsonResponse(response_data)
