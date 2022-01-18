from rest_framework import serializers
from .models import Audio_store


class Audio_serializer(serializers.ModelSerializer):
    class Meta:
        model = Audio_store
        fields = ('word', 'allow_mumble')