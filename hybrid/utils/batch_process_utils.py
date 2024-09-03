# Create MagazineContent
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
import psutil
from math import ceil
from django.db import transaction
from hybrid.models import MagazineInformation


# Main function to create processes and manage batch fetching
def create_process(create_object_func, MagazineModel, data=None):
    
    total_records = 10000 if data is None else len(data)  # Adjust based on total data or provided data

     # Divide the number of cores by 4
    num_cores = max(1, psutil.cpu_count(logical=False) // 4)

    batch_size = compute_batch_size(num_cores, total_records)
    total_batches = ceil(total_records / batch_size)
    num_processes = min(num_cores, ceil(total_records / batch_size))

    print(f"Using {num_processes} processes with batch size of {batch_size}")

    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        futures = []
        for i in tqdm(range(total_batches), desc="Processing batches"):
            start_idx = i * batch_size
            end_idx = min(start_idx + batch_size, total_records)
            batch_data = fetch_data(start_idx, end_idx, data)
            futures.append(executor.submit(process_batch, batch_data, MagazineModel, create_object_func))

        successful_records = 0
        for future in tqdm(as_completed(futures), desc="Collecting results"):
            try:
                successful_records += future.result()
            except Exception as e:
                print(f"Error processing batch: {e}")

    print(f"Successfully processed {successful_records} out of {total_records} records")
    return successful_records

# Function processes child workers information by provding batch data
# Function also bulks create table information for faster processing time
def process_batch(batch_data, MagazineModel, create_object_func):
    successful_records = 0
    record_instances = []

    for record in batch_data:
        try:
            recordObject = create_object_func(record)
            record_instances.append(recordObject)
            successful_records += 1
        except Exception as e:
            print(f"Error processing record: {e}")

    with transaction.atomic():
        MagazineModel.objects.bulk_create(record_instances)
    return successful_records

# Function fetches data in range batches based on use case
def fetch_data(start_idx, end_idx, data=None):
    if data is None:
        return list(MagazineInformation.objects.all().values('id', 'content')[start_idx:end_idx])
    else:
        return data[start_idx:end_idx]

# Function compute appropriate batch size based on system capabilities
def compute_batch_size(num_cores, total_records):

    # Get available memory (in bytes)
    available_memory = psutil.virtual_memory().available

    # Estimate memory per record (adjust this based on your data structure)
    estimated_memory_per_record = 10 # 1 KB per record,

    # Calculate the maximum number of records we can process at once
    max_records_in_memory = available_memory // estimated_memory_per_record

     # Determine the optimal batch size
    batch_size = min(max_records_in_memory // num_cores,  total_records // num_cores)
    batch_size = max(batch_size, 1)  # Ensure batch size is at least 1

    return batch_size

