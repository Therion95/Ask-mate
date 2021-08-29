import os

import psycopg2
import psycopg2.extras
from psycopg2 import sql

import csv_connection
import db_connection
import files_connection
import util

# GLOBAL directory for the app config
UPLOAD_FOLDER_A = os.environ.get('UPLOAD_FOLDER_A')
UPLOAD_FOLDER_Q = os.environ.get('UPLOAD_FOLDER_Q')
# GLOBAL directories to our CSV files:
QUESTIONS = os.environ.get('QUESTIONS_PATH')
ANSWERS = os.environ.get('ANSWERS_PATH')


# CSV version:

# def list_questions(csv_file):
#     list_of_data = csv_connection.csv_opening(csv_file)
#
#     headers = list(list_of_data[0].keys())
#
#     return list_of_data, headers


# def get_headers(csv_file):
#     list_of_data = csv_connection.csv_opening(csv_file)
#
#     return list(list_of_data[0].keys())


# def question_display(question_id, questions_csv_file, answers_csv_file):
#     questions, headers = list_questions(questions_csv_file)
#     answers = [answer for answer in csv_connection.csv_opening(answers_csv_file)
#                if int(answer['question_id']) == question_id]
#
#     for question in questions:
#         if int(question['id']) == question_id:
#             return question, headers, answers


# def add_question(requested_data, requested_image):
#     path = files_connection.upload_file(requested_image)
#     keys = ['id', 'submission_time', 'title', 'message', 'view_number', 'vote_number', 'image']
#     values = [util.get_next_id(QUESTIONS), util.current_date(), requested_data['title'], requested_data['message'], 0, 0, path]
#     prepared_dict = {k: v for k, v in zip(keys, values)}
#
#     return csv_connection.csv_appending(QUESTIONS, prepared_dict)


def answer_question(requested_data, requested_image, question_id):
    path = files_connection.upload_file(requested_image)
    keys = ['id', 'submission_time', 'message', 'vote_number', 'question_id', 'image']
    values = [util.get_next_id(ANSWERS), util.current_date(), requested_data['message'], 0, question_id, path]
    prepared_dict = {k: v for k, v in zip(keys, values)}

    return csv_connection.csv_appending(ANSWERS, prepared_dict)


def display_answer(answer_id):
    list_of_answers = csv_connection.csv_opening(ANSWERS)
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


# DB version:

@db_connection.executor
def list_column(cursor, db_table):
    query = """
    SELECT *
    FROM {table}
    order by id;
    """
    cursor.execute(sql.SQL(query).format(table=sql.Identifier(db_table)).as_string(cursor))

    return [dict(row) for row in cursor.fetchall()]


@db_connection.executor
def get_headers(cursor, db_table):
    return list(list_column(db_table)[0].keys())


@db_connection.executor
def question_display(cursor, question_id, db_table):
    db_data, headers = list_column(db_table), get_headers(db_table)
    answers = [answer for answer in list_column('answer')
               if int(answer['question_id']) == question_id]

    for question in db_data:
        if int(question['id']) == question_id:
            return question, headers, answers


@db_connection.executor
def add_question(cursor, requested_data, requested_image, db_table):
    path = files_connection.upload_file(requested_image)
    # table_keys = tuple(get_headers(db_table))

    new_values = (util.current_date(), 0, 0, requested_data['title'], requested_data['message'], path)
    query = """
    INSERT INTO question (submission_time, view_number, vote_number, title, message, image)
    VALUES (%s, %s, %s, %s, %s, %s)
    RETURNING id;
    """
    cursor.execute(query, new_values)

    # cursor.execute(sql.SQL(query).format(table=sql.Identifier(db_table)).as_string(cursor), (util.current_date(), '0', '0', requested_data['title'], requested_data['message'], path,))
    return dict(cursor.fetchone())['id']