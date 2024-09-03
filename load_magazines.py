import django
import json
from math import ceil
import multiprocessing as mp
import os
import sys
from tqdm import tqdm

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)


# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'search.settings')


# Configure Django
django.setup()


from hybrid.utils.batch_process_utils import create_process, compute_batch_size
from hybrid.utils.text_vector_utils import create_search_vector_process
from hybrid.utils.magazine_utils import create_magazine_record
from hybrid.models import MagazineInformation


# 'Load mock dataset'
def load_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        return data
        

def main():

    print("Step 1: load mock dataset from file")
    data = load_json('magazine.json')

    # Determine the number of CPU cores
    num_cores = mp.cpu_count()

    # determine number batch size based on systems memory
    batch_size = compute_batch_size(num_cores, len(data))

    # Calculate the number of processes to be created
    num_processes = min(num_cores, ceil(len(data) / batch_size))

    
    print("Step 2: initiate batch processes to create magazine information table")
    create_process(create_magazine_record, MagazineInformation, data)


    print("Step 3: Building and search vector index...")
    create_search_vector_process(num_processes, batch_size)

if __name__ == "__main__":
    main()


      

       
