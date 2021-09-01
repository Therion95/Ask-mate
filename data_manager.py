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
COMMENTS_Q = os.environ.get('COMMENTS_Q')
COMMENTS_A = os.environ.get('COMMENTS_A')


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
    path = csv_connection.upload_file(requested_image, UPLOAD_FOLDER_Q)
    keys = ['id', 'submission_time', 'title', 'message', 'view_number', 'vote_number', 'image']
    values = [util.get_next_id(QUESTIONS), util.current_date(), requested_data['title'], requested_data['message'], 0, 0, path]
    prepared_dict = {k: v for k, v in zip(keys, values)}

    return csv_connection.csv_appending(QUESTIONS, prepared_dict)


def answer_question(requested_data, requested_image, question_id):
    path = csv_connection.upload_file(requested_image, UPLOAD_FOLDER_A)
    keys = ['id', 'submission_time', 'message', 'vote_number', 'question_id', 'image']
    values = [util.get_next_id(ANSWERS), util.current_date(), requested_data['message'], 0, question_id, path]
    prepared_dict = {k: v for k, v in zip(keys, values)}

    return csv_connection.csv_appending(ANSWERS, prepared_dict)


def comment_question(requested_data, question_id):
    keys = ['id', 'submission_time', 'message', 'question_id']
    values = [util.get_next_id(COMMENTS_Q), util.current_date(), requested_data['message'], question_id]
    prepared_dict = {k: v for k, v in zip(keys, values)}

    return csv_connection.csv_appending(COMMENTS_Q, prepared_dict)


def comment_answer(requested_data, answer_id, question_id):
    keys = ['id', 'submission_time', 'message', 'answer_id', 'question_id']
    values = [util.get_next_id(COMMENTS_A), util.current_date(), requested_data['message'], answer_id, question_id]
    prepared_dict = {k: v for k, v in zip(keys, values)}

    return csv_connection.csv_appending(COMMENTS_A, prepared_dict)


def display_answer(answer_id):
    list_of_answers = csv_connection.csv_opening(ANSWERS)
    for answer in list_of_answers:
        if int(answer['id']) == int(answer_id):
            return answer


def edit_answer(answer_id, edited_answer, new_image):
    if new_image.filename != '':
        new_path = csv_connection.upload_file(new_image, UPLOAD_FOLDER_A)
        os.remove(display_answer(answer_id)['image'])
    else:
        new_path = display_answer(answer_id)['image']

    keys = ['submission_time', 'message', 'image']
    values = [util.current_date(), edited_answer['message'], new_path]

    return csv_connection.csv_editing(ANSWERS, answer_id, keys, values)


def delete_image(answer_id):
    os.remove(display_answer(answer_id)['image'])
    csv_connection.csv_editing(ANSWERS, answer_id, ['image'], [""])


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

    # cursor.execute(sql.SQL(query).format(table=sql.Identifier(db_table)).as_string(cursor), (util.current_date(),
    # '0', '0', requested_data['title'], requested_data['message'], path,))
    return dict(cursor.fetchone())['id']


@db_connection.executor
def get_tag_names_by_question_id(cursor, question_id):
    query = """
        SELECT name
        FROM tag
        RIGHT JOIN question_tag
        ON tag.id = question_tag.tag_id
        WHERE question_id = %s
    """
    cursor.execute(query, [question_id])
    return cursor.fetchall()


@db_connection.executor
def get_tags(cursor):
    query = """
        SELECT name
        FROM tag
        ORDER BY id ASC 
    """
    cursor.execute(query)
    return cursor.fetchall()


@db_connection.executor
def get_new_id(cursor):
    query = """
        SELECT MAX(id)
        AS max_id
        FROM tag
    """
    cursor.execute(query)
    return int(cursor.fetchone().get('max_id')) + 1


@db_connection.executor
def add_tag(cursor, new_tag):
    query = """
        INSERT INTO tag
        VALUES (%s, %s)
    """
    tag_id = get_new_id()
    cursor.execute(query, [tag_id, new_tag])

#INSERT INTO tag(name)
#VALUES (%s)

@db_connection.executor
def get_tags_id(cursor, tags):
    get_id = []
    for tag in tags:
        query = """
            SELECT id
            FROM tag
            WHERE name LIKE %s
        """
        cursor.execute(query, [tag])
        get_id.append(cursor.fetchall())
    return get_id


@db_connection.executor
def insert_updated_tags(cursor, question_id, new_tags):
    tags_already_in = [tag['name'] for tag in get_tag_names_by_question_id(question_id)]
    tags_to_add = [tag for tag in new_tags if tag not in tags_already_in]
    for id_list in get_tags_id(tags_to_add):
        for selected_id in id_list:
            query = """
                INSERT INTO question_tag (question_id, tag_id)
                VALUES (%s, %s)
            """
            cursor.execute(query, [question_id, selected_id['id']])
