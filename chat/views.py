from django.shortcuts import render

# Create your views here.
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Conversation, Message
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    ConversationSerializer,
    MessageSerializer
)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "message": "User registered successfully"
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class UserListView(APIView):

    def get(self, request):
        users = User.objects.exclude(id=request.user.id)
        serializer = UserSerializer(users, many=True)

        return Response(serializer.data)


class ConversationListCreateView(APIView):

    def get(self, request):
        conversations = request.user.conversation_set.all()
        serializer = ConversationSerializer(
            conversations,
            many=True
        )

        return Response(serializer.data)

    def post(self, request):
        user_id = request.data.get('user_id')

        if not user_id:
            return Response(
                {"error": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            other_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if other_user == request.user:
            return Response(
                {"error": "You cannot chat with yourself"},
                status=status.HTTP_400_BAD_REQUEST
            )

        conversation = Conversation.objects.create()
        conversation.participants.add(
            request.user,
            other_user
        )

        serializer = ConversationSerializer(conversation)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


class MessageListView(APIView):

    def get(self, request, conversation_id):

        try:
            conversation = Conversation.objects.get(
                id=conversation_id
            )
        except Conversation.DoesNotExist:
            return Response(
                {"error": "Conversation not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if not conversation.participants.filter(
            id=request.user.id
        ).exists():
            return Response(
                {"error": "You are not part of this conversation"},
                status=status.HTTP_403_FORBIDDEN
            )

        messages = conversation.messages.all().order_by(
            'created_at'
        )

        serializer = MessageSerializer(
            messages,
            many=True
        )

        return Response(serializer.data)