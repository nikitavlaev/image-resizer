from django.urls import path

from . import views

urlpatterns = [
    path('api/', views.SetTaskView.as_view(), name = 'set'),
    path('api/task/<str:task_id>/', views.GetTaskView.as_view(), name = 'task'),
]
