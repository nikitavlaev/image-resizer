import os

from django import forms
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from .tasks import resize_img

from celery import current_app

class FileUploadForm(forms.Form):
    image_file = forms.ImageField(required = True)
    width = forms.IntegerField(required = True, widget= forms.NumberInput
                           (attrs={'id':'width'}))
    height = forms.IntegerField(required = True, widget= forms.NumberInput
                           (attrs={'id':'width'}))

class HomeView(View):
    def get(self, request):
        form = FileUploadForm()
        return render(request, 'home.html', {'form': form})

    def post(self, request):
        form = FileUploadForm(request.POST, request.FILES)
        context = {}

        if form.is_valid():
            w = form['width'].value()
            h = form['height'].value()
            file_path = os.path.join(settings.IMAGES_DIR, request.FILES['image_file'].name)
            with open(file_path, 'wb+') as fp:
                for chunk in request.FILES['image_file']:
                    fp.write(chunk)
            task = resize_img.delay(file_path, w, h)
            context['task_id'] = task.id
            context['task-status'] = task.status 
            context['form'] = form

            return render(request, 'home.html', context)
        context['form'] = form 

        return render(request, 'home.html', context)

class TaskView(View):
    def get(self, request, task_id):
        task = current_app.AsyncResult(task_id)
        response_data = {'task_status': task.status, 'task_id': task.id}

        if task.status == 'SUCCESS':
            response_data['results'] = task.get()

        return JsonResponse(response_data)        
