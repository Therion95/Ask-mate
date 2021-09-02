import os

# GLOBAL directory for the app config
UPLOAD_FOLDER_A = os.environ.get('UPLOAD_FOLDER_A')
UPLOAD_FOLDER_Q = os.environ.get('UPLOAD_FOLDER_Q')
# GLOBAL directories to our CSV files:
QUESTIONS = os.environ.get('QUESTIONS_PATH')
ANSWERS = os.environ.get('ANSWERS_PATH')
COMMENTS_Q = os.environ.get('COMMENTS_Q')
COMMENTS_A = os.environ.get('COMMENTS_A')