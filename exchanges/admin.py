from django.contrib import admin
from .models import SkillExchangeRequest, Feedback

@admin.register(SkillExchangeRequest)
class SkillExchangeRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'skill_offered', 'skill_requested', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('sender__username', 'receiver__username', 'skill_offered__name', 'skill_requested__name', 'message')
    ordering = ('-updated_at',)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'exchange_request', 'reviewer', 'rating', 'comment', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('reviewer__username', 'comment')
    ordering = ('-created_at',)
