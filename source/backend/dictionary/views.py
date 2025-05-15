from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from collections import defaultdict

from .models import Dictionary
from .serializers import DictionaryEntrySerializer

# Lấy danh sách gloss
class GlossListView(APIView):
    def get(self, request):
        glosses = Dictionary.objects.values_list('gloss', flat=True).distinct()
        return Response(glosses, status=status.HTTP_200_OK)
# LẤy src theo gloss
class GlossDetailView(APIView):
    def get(self, request, gloss_value):
        search_gloss = Dictionary.objects.filter(gloss=gloss_value)
        if not search_gloss.exists():
            return Response({"error": "Gloss not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = DictionaryEntrySerializer(search_gloss, many=True)
        
        # Nhóm theo từng subset
        grouped_data = defaultdict(list)
        for item in serializer.data:
            grouped_data[item['subset']].append(item['videosrc'])

        return Response(grouped_data, status=status.HTTP_200_OK)
