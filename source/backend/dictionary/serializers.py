from rest_framework import serializers
from .models import Dictionary

# Dùng cho API 2
class DictionaryEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Dictionary
        fields = ['videosrc', 'subset']
