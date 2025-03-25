import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Room, Message
from .serializers import MessageSerializer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope["user"]

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
        
        if not self.user.is_authenticated:
            await self.send(text_data=json.dumps({
                'error': 'Please login to send messages'
            }))
            return

        action = data.get('action', 'create')
        
        if action == 'create':
            message = await self.save_message(data['message'])
            message_data = await self.serialize_message(message)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'action': 'create',
                    'message': message_data
                }
            )
        elif action == 'update':
            message = await self.update_message(data['message_id'], data['message'])
            if message:
                message_data = await self.serialize_message(message)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'action': 'update',
                        'message': message_data
                    }
                )
        elif action == 'delete':
            success = await self.delete_message(data['message_id'])
            if success:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'action': 'delete',
                        'message_id': data['message_id']
                    }
                )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_message(self, message_text):
        room = Room.objects.get(id=self.room_id)
        message = Message.objects.create(
            User=self.user,
            room=room,
            body=message_text
        )
        room.participants.add(self.user)
        return message

    @database_sync_to_async
    def update_message(self, message_id, new_text):
        try:
            message = Message.objects.get(id=message_id, User=self.user)
            message.body = new_text
            message.save()
            return message
        except Message.DoesNotExist:
            return None

    @database_sync_to_async
    def delete_message(self, message_id):
        try:
            message = Message.objects.get(id=message_id, User=self.user)
            message.delete()
            return True
        except Message.DoesNotExist:
            return False

    @database_sync_to_async
    def serialize_message(self, message):
        return MessageSerializer(message).data
