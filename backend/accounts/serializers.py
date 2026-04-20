from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, UserProgress

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                 'role', 'avatar', 'group', 'phone', 'telegram')
        read_only_fields = ('role',)

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class UserProgressSerializer(serializers.ModelSerializer):
    track_name = serializers.CharField(source='track.name', read_only=True)
    completed_tasks_count = serializers.SerializerMethodField()
    total_tasks_count = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProgress
        fields = ('id', 'track', 'track_name', 'completed_tasks_count', 'total_tasks_count', 'updated_at')
    
    def get_completed_tasks_count(self, obj):
        return obj.completed_tasks.count()
    
    def get_total_tasks_count(self, obj):
        return obj.track.tasks.count()
