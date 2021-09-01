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


@db_connection.executor
def list_column(cursor, db_table):
    query = util.query_builder('SELECT', db_table, '*')
    cursor.execute(query)

    return [dict(row) for row in cursor.fetchall()]


@db_connection.executor
def get_headers(cursor, db_table):
    return list(list_column(db_table)[0].keys())


def question_display(question_id, db_table):
    db_data, headers = list_column(db_table), get_headers(db_table)
    answers = [answer for answer in list_column('answer')
               if int(answer['question_id']) == question_id]

    for question in db_data:
        if int(question['id']) == question_id:
            return question, headers, answers


@db_connection.executor
def answer_display(answer_id):
    list_of_answers = csv_connection.csv_opening(ANSWERS)
    for answer in list_of_answers:
        if int(answer['id']) == int(answer_id):
            return answer


@db_connection.executor
def add_question(cursor, requested_data, requested_image, db_table):
    path = files_connection.upload_file(requested_image)
    if path:
        values = [str(v) for v in [util.current_date(), '0', '0', requested_data['title'], requested_data['message'], path]]
    else:
        values = [str(v) if v else v for v in [util.current_date(), '0', '0', requested_data['title'],
                                               requested_data['message'], None]]

    query = util.query_builder('INSERT', db_table, values=values)
    cursor.execute(query, values)

    return dict(cursor.fetchone())['id']


@db_connection.executor
def answer_question(cursor, requested_data, requested_image, db_table, question_id):
    path = files_connection.upload_file(requested_image)
    if path:
        values = [str(v) for v in
                  [util.current_date(), 0, question_id, requested_data['message'], path]]
    else:
        values = [str(v) if v else v for v in [util.current_date(), 0, question_id, requested_data['message'], None]]

    query = util.query_builder('INSERT', db_table, values=values)
    cursor.execute(query, values)


@db_connection.executor
def voting_for_up_down(cursor, db_table, given_id, up_or_down):
    values = {'up': "+ 1", 'down': "- 1"}

    query = util.query_builder('VOTING', db_table, update=values[up_or_down], condition=f'id = {given_id}',
                               col_to_update='vote_number')
    cursor.execute(query)

    if db_table == 'answer':
        return dict(cursor.fetchone())['question_id']


@db_connection.executor
def record_edit(cursor, db_table, given_id, columns, values):
    # csv_connection.csv_editing(file, given_id, keys=keys, values_to_update=values)

    query = util.query_builder('EDITING', db_table, given_id, cols_to_update=columns, condition=f'id = {given_id}')
    cursor.execute(query, values)


@db_connection.executor
def record_delete(cursor, db_table, given_id):
    query = util.query_builder('DELETE', db_table, condition=f'id = {given_id}')
    cursor.execute(query)

    if db_table == 'answer':
        return dict(cursor.fetchone())['question_id']
