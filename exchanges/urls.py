from django.urls import path
from . import views

urlpatterns = [
    path('send/<str:receiver_username>/', views.send_request_view, name='send_request'),
    path('requests/', views.requests_list_view, name='requests_list'),
    path('respond/<int:request_id>/<str:action>/', views.respond_request_view, name='respond_request'),
    path('feedback/<int:request_id>/', views.add_feedback_view, name='add_feedback'),
]
