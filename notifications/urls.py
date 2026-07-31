from django.urls import path
from . import views

urlpatterns = [
    path('', views.notifications_list_view, name='notifications_list'),
    path('<int:notification_id>/read/', views.mark_notification_read_view, name='mark_notification_read'),
]
