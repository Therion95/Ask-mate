import os

UPLOAD_FOLDER_A = os.environ.get('UPLOAD_FOLDER_A')
UPLOAD_FOLDER_Q = os.environ.get('UPLOAD_FOLDER_Q')


def upload_file(given_image):
    if given_image.filename != '':
        path = f"{UPLOAD_FOLDER_Q}/{given_image.filename}"
        given_image.save(path)

        return path
