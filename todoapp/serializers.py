from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    # automatically use request.user for the user field
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')