from django.urls import path
from . import views

urlpatterns = [
    path('manage/', views.manage_skills_view, name='manage_skills'),
    path('remove/<int:skill_id>/', views.remove_user_skill_view, name='remove_user_skill'),
]
