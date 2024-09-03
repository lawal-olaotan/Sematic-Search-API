import django
import os

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "search.settings")
django.setup()

from hybrid.utils.batch_process_utils import create_process
from hybrid.utils.magazine_utils import create_content_record
from hybrid.models import MagazineContent


def main():

    print("Step 2: Creating magazine contents and generating embeddings...")
    create_process(create_content_record, MagazineContent)

if __name__ == "__main__":
    main()