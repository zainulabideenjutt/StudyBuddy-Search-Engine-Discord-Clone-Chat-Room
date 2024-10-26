from dataclasses import fields
from pyexpat import model
from rest_framework.serializers import ModelSerializer
from base.models import Room

class RoomSerializer(ModelSerializer):
    class Meta:
        model=Room
        fields='__all__'