import tempfile
import os


def create_temp_file(data, suffix):

    downloads_dir = os.path.join(os.getcwd(), 'downloads')
    os.makedirs(downloads_dir, exist_ok=True)
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix, mode='wb', dir=downloads_dir)
    with open(temp.name, mode='wb') as f:
        f.write(data.encode("utf-8"))
    temp.close()
    return temp.name
