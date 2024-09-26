from rest_framework import serializers
from .models import *

"""serializers are used basically to 
convert model instances to python data types here"""
#serializer for Interest 
class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interests
        fields = ['id','sender','receiver','status' ,'created_at','updated_at']


#serializer for sending interests messages
class SendInterestSerializer(serializers.Serializer):
    receiver_id = serializers.IntegerField()
    def validate_receiver(self,value):
        try:
            receiver = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Receiver not found")
        if self.context['request'].user.id == value:
            raise serializers.ValidationError("You cannot send an interest to yourself")
        
        return value

    def create(self, validated_data):
        sender = self.context['request'].user
        receiver = User.objects.get(id=validated_data['receiver_id'])
        if Interests.objects.filter(sender=sender, receiver=receiver).exists():
            raise serializers.ValidationError("Interest already sent")
        interest = Interests.objects.create(sender=sender, receiver=receiver)
        return interest
    
#serializer for updating status of interest shown by one user to another
class UpdateInterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interests
        fields = ['status']

    def validate_status(self, value):
        value = value.lower()
        if value not in ['accepted', 'rejected']:
            raise serializers.ValidationError("Invalid status. Must be 'accepted' or 'rejected'.")
        return value

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance