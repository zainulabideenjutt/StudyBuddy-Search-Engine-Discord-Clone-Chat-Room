from rest_framework import serializers
from .models import Room, Message, User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'avatar', 'email']  # Add any other needed user fields

class MessageSerializer(serializers.ModelSerializer):
    User = UserSerializer()
    is_owner = serializers.SerializerMethodField()
    created = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    
    class Meta:
        model = Message
        fields = ['id', 'User', 'body', 'created', 'is_owner']

    def get_is_owner(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.User == request.user
        return False

class RoomSerializer(serializers.ModelSerializer):
    host = UserSerializer()
    messages = MessageSerializer(source='message_set', many=True, read_only=True)
    participants = UserSerializer(many=True, read_only=True)
    
    class Meta:
        model = Room
        fields = ['id', 'name', 'description', 'host', 'participants', 'messages']
