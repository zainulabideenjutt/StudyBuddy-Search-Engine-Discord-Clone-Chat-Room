from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..serializers import RoomSerializer, MessageSerializer
from ..models import Room, Message

@api_view(['GET', 'POST'])
def room_api(request, pk):
    try:
        room = Room.objects.get(id=pk)
    except Room.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        room_messages = room.message_set.all().order_by('created')
        participants = room.participants.all()
        
        room_serializer = RoomSerializer(room)
        messages_serializer = MessageSerializer(room_messages, many=True)
        
        return Response({
            'room': room_serializer.data,
            'messages': messages_serializer.data,
            'participants_count': participants.count(),
            'is_authenticated': request.user.is_authenticated
        })

    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return Response({
                'error': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)

        message = Message.objects.create(
            User=request.user,
            room=room,
            body=request.data.get('message', '')
        )
        room.participants.add(request.user)
        
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['PUT', 'DELETE'])
def message_api(request, pk):
    try:
        message = Message.objects.get(id=pk)
    except Message.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
        
    if request.user != message.User:
        return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'PUT':
        message.body = request.data.get('message', '')
        message.save()
        serializer = MessageSerializer(message)
        return Response(serializer.data)

    elif request.method == 'DELETE':
        message.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)