import json
import numpy as np
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import F
from django.core.cache import cache
from sentence_transformers import SentenceTransformer
from hybrid.models import MagazineInformation, MagazineContent
from sklearn.metrics.pairwise import cosine_similarity
from annoy import AnnoyIndex

def perform_full_text_search(author_query, title_query, content_query, limit=100):
    # Combine all query terms into a single search string
    combined_query_string = f"{author_query} {title_query} {content_query}"
    
    # Use cache
    cache_key = f"search:{combined_query_string}:{limit}"
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result

    # Create a single combined query
    combined_query = SearchQuery(author_query, config='english') | \
                     SearchQuery(title_query, config='english') | \
                     SearchQuery(content_query, config='english')

    # Perform the search
    magazine_records = MagazineInformation.objects.filter(
        search_vector=combined_query
    ).annotate(
        rank=SearchRank(F('search_vector'), combined_query)
    ).order_by('-rank')[:limit]
    
    # Convert to list for caching
    result = list(magazine_records)

    # Cache the result
    cache.set(cache_key, result, timeout=3600)  # Cache for 1 hour
    
    return result

def perform_semantic_search(content_query):
    model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')
    query_embedding = model.encode(content_query).reshape(1, -1)

    # Fetch all magazine contents from DB
    magazine_contents = MagazineContent.objects.all()
    dimensions=384

    annoy_index = build_annoy_index_from_db(dimensions,magazine_contents)

    # Find nearest neighbors in the Annoy index
    nearest_neighbors = annoy_index.get_nns_by_vector(query_embedding.flatten(), 10, include_distances=True)

    # Retrieve the related magazine content
    results = []
    for idx in nearest_neighbors[0]:

        # Retrieves magazine content based on vector similarities
        magazine_content = MagazineContent.objects.get(id=magazine_contents[idx].id)

        # Retrieves magazine information based on foreign key Id
        magazine_information = MagazineInformation.objects.get(id=magazine_content.magazine_id)

        doc_embedding = np.array(magazine_content.vector_representation).reshape(-1, dimensions)

        # Calculate cosine similarity between query and document embeddings
        similarities = cosine_similarity(query_embedding,doc_embedding )
        avg_similarity = np.mean(similarities)

        results.append((magazine_information, avg_similarity))

    results = sorted(results, key=lambda x: x[1], reverse=True)
    return [result[0] for result in results]

def reciprocal_rank_fusion(full_text_results, semantic_results):
    rank_dict = {}
    
    # Process full_text_results (MagazineInformation objects)
    for idx, item in enumerate(full_text_results, 1):
        rank_dict[item.id] = rank_dict.get(item.id, 0) + 1 / idx

    # Process semantic_results (MagazineInformation objects)
    for idx, item in enumerate(semantic_results, 1):
        rank_dict[item.id] = rank_dict.get(item.id, 0) + 1 / idx

    sorted_ids = sorted(rank_dict, key=rank_dict.get, reverse=True)

    # Fetch MagazineInformation objects for the final results
    combined_results = [MagazineInformation.objects.get(id=record_id) for record_id in sorted_ids]
    return combined_results

def build_annoy_index_from_db(dimension, magazine_contents):
    # Initialize Annoy Index
    annoy_index = AnnoyIndex(dimension, 'angular')

    for idx, magazine_content in enumerate(magazine_contents):
    
        # Reshape the embedding back to the original 2D array
        embeddings = np.array(magazine_content.vector_representation).reshape(-1,dimension)

        for embedding in embeddings:
            annoy_index.add_item(idx, embedding)

    # Build the Annoy index
    annoy_index.build(500)  # Number of trees

    return annoy_index
