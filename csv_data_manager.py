import os
import csv_connection
import files_connection
import util
import variables


def list_questions(csv_file):
    list_of_data = csv_connection.csv_opening(csv_file)

    headers = list(list_of_data[0].keys())

    return list_of_data, headers


def get_headers(csv_file):
    list_of_data = csv_connection.csv_opening(csv_file)

    return list(list_of_data[0].keys())


def question_display(question_id, questions_csv_file, answers_csv_file, comments_q_csv_file, comments_a_csv_file):
    questions, headers = list_questions(questions_csv_file)
    answers = [answer for answer in csv_connection.csv_opening(answers_csv_file)
               if int(answer['question_id']) == question_id]
    comments_q = [comment for comment in csv_connection.csv_opening(comments_q_csv_file)
                  if int(comment['question_id']) == question_id]
    comments_a = [comment for comment in csv_connection.csv_opening(comments_a_csv_file)
                  if int(comment['question_id']) == question_id]

    for question in questions:
        if int(question['id']) == question_id:
            return question, headers, answers, comments_q, comments_a


def add_question(requested_data, requested_image):
    path = files_connection.upload_file(requested_image, variables.UPLOAD_FOLDER_Q)
    keys = ['id', 'submission_time', 'title', 'message', 'view_number', 'vote_number', 'image']
    values = [util.get_next_id(variables.QUESTIONS), util.current_date(), requested_data['title'],
              requested_data['message'], 0, 0, path]
    prepared_dict = {k: v for k, v in zip(keys, values)}

    return csv_connection.csv_appending(variables.QUESTIONS, prepared_dict)


def answer_question(requested_data, requested_image, question_id):
    path = files_connection.upload_file(requested_image, variables.UPLOAD_FOLDER_A)
    keys = ['id', 'submission_time', 'message', 'vote_number', 'question_id', 'image']
    values = [util.get_next_id(variables.ANSWERS), util.current_date(), requested_data['message'], 0, question_id, path]
    prepared_dict = {k: v for k, v in zip(keys, values)}

    return csv_connection.csv_appending(variables.ANSWERS, prepared_dict)


def comment_question(requested_data, question_id):
    keys = ['id', 'submission_time', 'message', 'question_id']
    values = [util.get_next_id(variables.COMMENTS_Q), util.current_date(), requested_data['message'], question_id]
    prepared_dict = {k: v for k, v in zip(keys, values)}

    return csv_connection.csv_appending(variables.COMMENTS_Q, prepared_dict)


def comment_answer(requested_data, answer_id, question_id):
    keys = ['id', 'submission_time', 'message', 'answer_id', 'question_id']
    values = [util.get_next_id(variables.COMMENTS_A), util.current_date(), requested_data['message'], answer_id,
              question_id]
    prepared_dict = {k: v for k, v in zip(keys, values)}

    return csv_connection.csv_appending(variables.COMMENTS_A, prepared_dict)


def display_answer(answer_id):
    list_of_answers = csv_connection.csv_opening(variables.ANSWERS)
    for answer in list_of_answers:
        if int(answer['id']) == int(answer_id):
            return answer


def voting_for_up_down(file, given_id, method):
    returned_id = csv_connection.csv_editing(file, given_id, method=method)

    if returned_id:
        return returned_id


def record_edit(file, given_id, keys, values):
    csv_connection.csv_editing(file, given_id, keys=keys, values_to_update=values)


def record_delete(file, given_id):
    returned_id = csv_connection.csv_delete_row(file, given_id)

    if returned_id:
        return returned_id


def edit_answer(answer_id, edited_answer, new_image):
    if new_image.filename != '':
        new_path = files_connection.upload_file(new_image, variables.UPLOAD_FOLDER_A)
        os.remove(display_answer(answer_id)['image'])
    else:
        new_path = display_answer(answer_id)['image']

    keys = ['submission_time', 'message', 'image']
    values = [util.current_date(), edited_answer['message'], new_path]

    return csv_connection.csv_editing(variables.ANSWERS, answer_id, keys, values)


def delete_image(answer_id):
    os.remove(display_answer(answer_id)['image'])
    csv_connection.csv_editing(variables.ANSWERS, answer_id, ['image'], [""])
