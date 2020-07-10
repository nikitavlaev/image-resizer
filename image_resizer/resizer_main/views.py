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



class FileUploadForm(forms.Form):
    image_file = forms.ImageField(required = True)
    width = forms.IntegerField(required = True, widget= forms.NumberInput
                           (attrs={'id':'width'}))
    height = forms.IntegerField(required = True, widget= forms.NumberInput
                           (attrs={'id':'height'}))

class SetTaskView(APIView):
    def post(self, request):
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            w = form['width'].value()
            h = form['height'].value()
            file_path = os.path.join(settings.IMAGES_DIR, request.FILES['image_file'].name)
            try:
                with open(file_path, 'wb+') as fp:
                    for chunk in request.FILES['image_file']:
                        fp.write(chunk)
            except IOError:
                return Response('Error during image file processing', status.HTTP_500_INTERNAL_SERVER_ERROR) 

            task = resize_img.delay(file_path, w, h)
            response_data = {'task_status': task.status, 'task_id': task.id}

            return JsonResponse(response_data)  
        return Response('Wrong form input', status.HTTP_400_BAD_REQUEST)    

class GetTaskView(APIView):
    def get(self, request, task_id):
        task = current_app.AsyncResult(task_id)
        response_data = {'task_status': task.status, 'task_id': task.id}

        if task.status == 'SUCCESS':
            result = task.get()
            if result['status'] == 'FAILURE':
                return Response('Error during image processing', status.HTTP_500_INTERNAL_SERVER_ERROR)
            response_data['results'] = result

        return JsonResponse(response_data)        
