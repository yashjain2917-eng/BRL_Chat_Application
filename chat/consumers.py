import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import Conversation, Message


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.conversation_id = self.scope['url_route']['kwargs'][
            'conversation_id'
        ]

        self.room_group_name = (
            f'chat_{self.conversation_id}'
        )

        if not await self.user_in_conversation():
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):

        data = json.loads(text_data)

        message_content = data.get('message')

        if not message_content:
            return

        message = await self.save_message(
            message_content
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_content,
                'sender': self.scope['user'].username,
                'created_at': message.created_at.isoformat()
            }
        )

    async def chat_message(self, event):

        await self.send(
            text_data=json.dumps({
                'message': event['message'],
                'sender': event['sender'],
                'created_at': event['created_at']
            })
        )

    @database_sync_to_async
    def user_in_conversation(self):

        return Conversation.objects.filter(
            id=self.conversation_id,
            participants=self.scope['user']
        ).exists()

    @database_sync_to_async
    def save_message(self, content):

        conversation = Conversation.objects.get(
            id=self.conversation_id
        )

        return Message.objects.create(
            conversation=conversation,
            sender=self.scope['user'],
            content=content
        )