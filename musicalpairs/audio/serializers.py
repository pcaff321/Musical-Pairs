from rest_framework import serializers
from .models import Audio_store


class Audio_serializer(serializers.ModelSerializer):
    class Meta:
        model = Audio_store
        fields = ('name', 'allow_mumble', 'file_location')