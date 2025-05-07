import os


def create_folder(foldername: str):
    isExist = os.path.exists(foldername)
    if not isExist:
        os.makedirs(foldername)
