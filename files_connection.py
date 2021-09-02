import os

UPLOAD_FOLDER_A = os.environ.get('UPLOAD_FOLDER_A')
UPLOAD_FOLDER_Q = os.environ.get('UPLOAD_FOLDER_Q')


def upload_file(given_image, folder):
    if given_image.filename != '':
        path = f"{folder}/{given_image.filename}"
        given_image.save(path)

        return path
