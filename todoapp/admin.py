from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'completed', 'priority', 'due_date', 'created_at')
    list_filter = ('completed', 'priority', 'created_at', 'user')
    search_fields = ('title', 'description', 'user__username')
