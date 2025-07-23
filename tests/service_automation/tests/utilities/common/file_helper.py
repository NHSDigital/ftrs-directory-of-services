import tempfile
import os
from loguru import logger

def create_temp_file(data, suffix):

    downloads_dir = os.path.join(os.getcwd(), 'downloads')
    os.makedirs(downloads_dir, exist_ok=True)
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix, mode='w', dir=downloads_dir)
    with open(temp.name, mode='w') as f:
        f.write(data)
    temp.close()
    logger.info(f"Temporary file created at {temp.name} with suffix {suffix}")
    return temp.name
