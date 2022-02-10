from rest_framework import serializers
from .models import Audio_store, Survey


class Audio_serializer(serializers.ModelSerializer):
    class Meta:
        model = Audio_store
        fields = ('word', 'allow_mumble')


class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = ('id', 'code', 'host', 'name', 'round_count', 'round_list', 'created_at')


class CreateSurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = ('name', 'round_count', 'round_list')

