import os
import django
import multiprocessing as mp
from tqdm import tqdm

# Now you can import your Django models
from django.db import connection
from django.db.models import Min, Max
from hybrid.models import MagazineInformation


def update_search_vector(start_id, end_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE hybrid_magazineinformation
            SET search_vector = (
                setweight(to_tsvector('english', COALESCE(title, '')), 'A') ||
                setweight(to_tsvector('english', COALESCE(author, '')), 'B') ||
                setweight(to_tsvector('english', COALESCE(content, '')), 'B')
            )
            WHERE id BETWEEN %s AND %s
        """, [start_id, end_id])
    return end_id - start_id + 1

def process_search_vector(batch):
    start_id, end_id = batch
    return update_search_vector(start_id, end_id)

def create_search_vector_batch(batch_size):

    # Finds the smallest and largest id values in magazine_information table
    id_range = MagazineInformation.objects.aggregate(Min('id'), Max('id'))
    min_id, max_id = id_range['id__min'], id_range['id__max']

    # Creates batches of IDs, where each batch is represented by a tuple (start,end)
    batches = [(i, min(i + batch_size - 1, max_id)) for i in range(min_id, max_id + 1, batch_size)]
    return batches

# Creates processes to save search vector index 
# function is called in load_magazines.py
def create_search_vector_process(num_processes, batch_size):
    print("Starting to populate search_vector fields...")

    batches = create_search_vector_batch(batch_size)

    # Process batches using multiprocessing
    with mp.Pool(processes=num_processes) as pool:
        results = list(tqdm(
            pool.imap(process_search_vector, batches),
            total=len(batches),
            desc="Processing batches"
        ))

    total_processed = sum(results)
    print(f"Successfully populated search_vector fields for {total_processed} records.")
