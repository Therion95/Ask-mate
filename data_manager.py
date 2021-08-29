import os

import connection
import util

# GLOBAL directory for the app config
UPLOAD_FOLDER_A = os.environ.get('UPLOAD_FOLDER_A')
UPLOAD_FOLDER_Q = os.environ.get('UPLOAD_FOLDER_Q')
# GLOBAL directories to our CSV files:
QUESTIONS = os.environ.get('QUESTIONS_PATH')
ANSWERS = os.environ.get('ANSWERS_PATH')
COMMENTS_Q = os.environ.get('COMMENTS_Q')
COMMENTS_A = os.environ.get('COMMENTS_A')


def list_questions(csv_file):
    list_of_data = connection.csv_opening(csv_file)

    headers = list(list_of_data[0].keys())

    return list_of_data, headers


def get_headers(csv_file):
    list_of_data = connection.csv_opening(csv_file)

    return list(list_of_data[0].keys())


def question_display(question_id, questions_csv_file, answers_csv_file, comments_q_csv_file, comments_a_csv_file):
    questions, headers = list_questions(questions_csv_file)
    answers = [answer for answer in connection.csv_opening(answers_csv_file)
               if int(answer['question_id']) == question_id]
    comments_q = [comment for comment in connection.csv_opening(comments_q_csv_file)
               if int(comment['question_id']) == question_id]
    comments_a = [comment for comment in connection.csv_opening(comments_a_csv_file)
               if int(comment['question_id']) == question_id]

    for question in questions:
        if int(question['id']) == question_id:
            return question, headers, answers, comments_q, comments_a


def add_question(requested_data, requested_image):
    path = connection.upload_file(requested_image, UPLOAD_FOLDER_Q)
    keys = ['id', 'submission_time', 'title', 'message', 'view_number', 'vote_number', 'image']
    values = [util.get_next_id(QUESTIONS), util.current_date(), requested_data['title'], requested_data['message'], 0, 0, path]
    prepared_dict = {k: v for k, v in zip(keys, values)}

    return connection.csv_appending(QUESTIONS, prepared_dict)


def answer_question(requested_data, requested_image, question_id):
    path = connection.upload_file(requested_image, UPLOAD_FOLDER_A)
    keys = ['id', 'submission_time', 'message', 'vote_number', 'question_id', 'image']
    values = [util.get_next_id(ANSWERS), util.current_date(), requested_data['message'], 0, question_id, path]
    prepared_dict = {k: v for k, v in zip(keys, values)}

    return connection.csv_appending(ANSWERS, prepared_dict)


def comment_question(requested_data, question_id):
    keys = ['id', 'submission_time', 'message', 'question_id']
    values = [util.get_next_id(COMMENTS_Q), util.current_date(), requested_data['message'], question_id]
    prepared_dict = {k: v for k, v in zip(keys, values)}

    return connection.csv_appending(COMMENTS_Q, prepared_dict)


def comment_answer(requested_data, answer_id, question_id):
    keys = ['id', 'submission_time', 'message', 'answer_id', 'question_id']
    values = [util.get_next_id(COMMENTS_A), util.current_date(), requested_data['message'], answer_id, question_id]
    prepared_dict = {k: v for k, v in zip(keys, values)}

    return connection.csv_appending(COMMENTS_A, prepared_dict)


def display_answer(answer_id):
    list_of_answers = connection.csv_opening(ANSWERS)
    for answer in list_of_answers:
        if int(answer['id']) == int(answer_id):
            return answer


def edit_answer(answer_id, edited_answer, new_image):
    if new_image.filename != '':
        new_path = connection.upload_file(new_image, UPLOAD_FOLDER_A)
        os.remove(display_answer(answer_id)['image'])
    else:
        new_path = display_answer(answer_id)['image']

    keys = ['submission_time', 'message', 'image']
    values = [util.current_date(), edited_answer['message'], new_path]

    return connection.csv_editing(ANSWERS, answer_id, keys, values)


def delete_image(answer_id):
    os.remove(display_answer(answer_id)['image'])
    connection.csv_editing(ANSWERS, answer_id, ['image'], [""])
