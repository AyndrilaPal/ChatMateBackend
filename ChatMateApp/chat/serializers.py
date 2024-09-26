from rest_framework import serializers
from .models import *

#serializer for stored messages
class ChatMessagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessages
        fields = ['id','sender','receiver','message','created_at']