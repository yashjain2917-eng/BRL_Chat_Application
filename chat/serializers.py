from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Conversation, Message


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(
        source='sender.username',
        read_only=True
    )

    class Meta:
        model = Message
        fields = [
            'id',
            'sender',
            'content',
            'created_at'
        ]


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = [
            'id',
            'participants',
            'created_at'
        ]