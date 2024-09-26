import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from users.models import User
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.backends import TokenBackend
from .models import ChatMessages
from interests.models import Interests


class ChatMessagesConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        token = self.get_token_from_headers()

        if token is None:
            await self.close()
            return

        # Decode the JWT token and extract user_id
        decoded_data = self.decode_jwt_token(token)

        if decoded_data is None:
            await self.close()
            return

        user_id = decoded_data.get('user_id')

        # Set self.scope['user'] manually based on the decoded JWT
        self.scope['user'] = await self.get_user(user_id)

        if self.scope['user'] is None:
            await self.close()
            return
        self.room_name = f"chat_{self.scope['user'].id}_{self.scope['url_route']['kwargs']['user_id']}"
        self.room_group_name = f"chat_{self.room_name}"

        other_user = await self.get_user(self.scope['url_route']['kwargs']['user_id'])

        # Check if the interest is accepted between the users
        if not await self.check_interest(self.scope['user'], other_user):
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
        message = data['message']
        receiver_id = data['receiver_id']

        # Save the chat message
        await self.create_chat_message(receiver_id, message)

        # Broadcast the message to the room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': self.scope['user'].username
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender
        }))

    def get_token_from_headers(self):
        # Extract Authorization header and return the Bearer token
        headers = dict(self.scope['headers'])
        auth_header = headers.get(b'authorization', None)
        print(auth_header)
        if auth_header:
            auth_data = auth_header.decode('utf-8').split()
            print(auth_data)
            if len(auth_data) == 2 and auth_data[0].lower() == 'bearer':
                print(auth_data[1])
                return auth_data[1]
        return None

    def decode_jwt_token(self, token):
        try:
            # This automatically verifies and decodes the token
            decoded_data = UntypedToken(token)
            return decoded_data.payload  # Return the decoded payload
        except (InvalidToken, TokenError) as e:
            print(f"Token decoding failed: {e}")
            return None

    @sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @sync_to_async
    def check_interest(self, sender, receiver):
        # Check if there's an accepted interest between the sender and receiver
        return Interests.objects.filter(
            sender=sender,
            receiver=receiver,
            status='accepted'
        ).exists()

    @sync_to_async
    def create_chat_message(self, receiver_id, message):
        receiver = User.objects.get(id=receiver_id)
        return ChatMessages.objects.create(
            sender=self.scope['user'],
            receiver=receiver,
            message=message
        )
