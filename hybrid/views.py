from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import MagazineContentSerializer,MagazineInformationSerializer
from .utils.search_utils import perform_full_text_search, perform_semantic_search, reciprocal_rank_fusion

# Create your views here.
class MagazineSearchAPIView(APIView):

    def get(self, request):
        # Extract query parameters
        author_query = request.query_params.get('author', '').strip('"')
        title_query = request.query_params.get('title', '').strip('"')
        content_query = request.query_params.get('content', '').strip('"')

        if not any([author_query, title_query, content_query]):
            return Response({"detail": "At least one query parameter ('author', 'title', or 'content') is required."}, status=400)

        # Perform full-text search
        full_text_results = perform_full_text_search(author_query, title_query, content_query)

        # Perform semantic search if content_query is provided
        semantic_results = perform_semantic_search(content_query) if content_query else []

        # Combine results using Reciprocal Rank Fusion (RRF)
        combined_results = reciprocal_rank_fusion(full_text_results, semantic_results)

        serializer = MagazineInformationSerializer(combined_results, many=True)
        return Response(serializer.data, status=200)
