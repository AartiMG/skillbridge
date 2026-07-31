from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'college_or_organization', 'city', 'preferred_learning_mode', 'created_at')
    list_filter = ('preferred_learning_mode', 'city')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'college_or_organization', 'city')
    ordering = ('-created_at',)
