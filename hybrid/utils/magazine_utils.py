import json
import numpy as np
from hybrid.models import MagazineInformation, MagazineContent
from sentence_transformers import SentenceTransformer
# vector enbedding model
 
 
 
model= SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')

# Create MagazineInformation instance
def create_magazine_record(magazine):
    content_property = create_content_property(magazine)  # Removed the unused 'help' variable
    return MagazineInformation(
        title=magazine['title'],
        author=magazine['author'],
        publication_date=magazine['publication_date'],
        category=magazine['publication_category'],
        publication_country=magazine['publication_country'],
        content=content_property,  # Added a missing comma here
        revenue_generated=magazine['revenue_generated']
    )

def create_content_property(magazine):
    return f"{magazine['title']} was published on {magazine['publication_date']} by author {magazine['author']} " \
           f"The {magazine['publication_country']} based author publication was categorized in the {magazine['publication_category']} genre. " \
           f"{magazine['title']} has generated {magazine['revenue_generated']} million in revenue since published."

# Creates magazine content record with vector embedding
def create_content_record(magazine_record):
    content = magazine_record.get('content','')
    record_id = magazine_record.get('id', '')
    embeddings = model.encode(content)

    # Creates MagazineContent
    record = MagazineContent(
        magazine_id=record_id,
        content=content,
        vector_representation=embeddings
    )

    return record